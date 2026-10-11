use quinn::{Endpoint, RecvStream};
use rustls::client::danger::{HandshakeSignatureValid, ServerCertVerified, ServerCertVerifier};
use rustls::pki_types::{CertificateDer, ServerName, UnixTime};
use sha2::{Digest, Sha256};
use std::env;
use std::io::{self, Read};
use std::net::{SocketAddr, ToSocketAddrs};
use std::sync::Arc;
use std::time::Duration;
use tokio::io::AsyncReadExt;
use tokio::time::timeout;

const ALPN_DEFAULT: &str = "ilc-native-submit-v1";
const REQUEST_TAG: u8 = 0x01;
const OK_TAG: u8 = 0x81;
const ERR_TAG: u8 = 0xff;
const MAX_FRAME_BYTES: usize = 1_048_576;

#[derive(Debug)]
struct FingerprintVerifier {
    expected_sha256_hex: String,
}

impl ServerCertVerifier for FingerprintVerifier {
    fn verify_server_cert(
        &self,
        end_entity: &CertificateDer<'_>,
        _intermediates: &[CertificateDer<'_>],
        _server_name: &ServerName<'_>,
        _ocsp_response: &[u8],
        _now: UnixTime,
    ) -> Result<ServerCertVerified, rustls::Error> {
        let actual = hex_lower(&Sha256::digest(end_entity.as_ref()));
        if actual == self.expected_sha256_hex {
            Ok(ServerCertVerified::assertion())
        } else {
            Err(rustls::Error::General(
                "native_submit_tls_fingerprint_mismatch".into(),
            ))
        }
    }

    fn verify_tls12_signature(
        &self,
        _message: &[u8],
        _cert: &CertificateDer<'_>,
        _dss: &rustls::DigitallySignedStruct,
    ) -> Result<HandshakeSignatureValid, rustls::Error> {
        Err(rustls::Error::General("TLS 1.2 not supported".into()))
    }

    fn verify_tls13_signature(
        &self,
        message: &[u8],
        cert: &CertificateDer<'_>,
        dss: &rustls::DigitallySignedStruct,
    ) -> Result<HandshakeSignatureValid, rustls::Error> {
        rustls::crypto::verify_tls13_signature(
            message,
            cert,
            dss,
            &rustls::crypto::ring::default_provider().signature_verification_algorithms,
        )
    }

    fn supported_verify_schemes(&self) -> Vec<rustls::SignatureScheme> {
        rustls::crypto::ring::default_provider()
            .signature_verification_algorithms
            .supported_schemes()
    }
}

struct Config {
    endpoint: String,
    expected_tls_fingerprint: Option<String>,
    alpn: String,
    timeout_ms: u64,
}

#[tokio::main]
async fn main() {
    if let Err(err) = run().await {
        eprintln!("{err}");
        std::process::exit(1);
    }
}

async fn run() -> Result<(), String> {
    let _ = rustls::crypto::ring::default_provider().install_default();
    let config = parse_args(env::args().skip(1).collect())?;
    let mut input = Vec::new();
    io::stdin()
        .read_to_end(&mut input)
        .map_err(|_| "native_submit_client_stdin_read_failed".to_string())?;
    if input.is_empty() || input.len() > MAX_FRAME_BYTES {
        return Err("native_submit_client_input_size_invalid".to_string());
    }
    if std::str::from_utf8(&input).is_err() {
        return Err("native_submit_client_input_not_utf8".to_string());
    }
    if input.iter().any(|b| matches!(b, b'\n' | b'\r')) {
        return Err("native_submit_client_input_not_single_line_json".to_string());
    }
    serde_json::from_slice::<serde_json::Value>(&input)
        .map_err(|_| "native_submit_client_input_json_invalid".to_string())?;

    let (host, addr) = resolve_endpoint(&config.endpoint)?;
    let mut endpoint = Endpoint::client(
        "0.0.0.0:0"
            .parse()
            .map_err(|_| "native_submit_client_bind_addr_invalid".to_string())?,
    )
    .map_err(|_| "native_submit_client_endpoint_init_failed".to_string())?;
    endpoint.set_default_client_config(build_client_config(
        config.expected_tls_fingerprint,
        config.alpn.as_bytes().to_vec(),
    )?);

    let connection = timeout(Duration::from_millis(config.timeout_ms), async {
        endpoint
            .connect(addr, &host)
            .map_err(|_| "native_submit_client_connect_start_failed".to_string())?
            .await
            .map_err(|_| "native_submit_client_connect_failed".to_string())
    })
    .await
    .map_err(|_| "native_submit_client_timeout".to_string())??;

    let (mut send, mut recv) = timeout(Duration::from_millis(config.timeout_ms), async {
        connection
            .open_bi()
            .await
            .map_err(|_| "native_submit_client_open_stream_failed".to_string())
    })
    .await
    .map_err(|_| "native_submit_client_timeout".to_string())??;

    let request = frame(REQUEST_TAG, &input);
    timeout(Duration::from_millis(config.timeout_ms), async {
        send.write_all(&request)
            .await
            .map_err(|_| "native_submit_client_write_failed".to_string())?;
        send.finish()
            .map_err(|_| "native_submit_client_finish_failed".to_string())?;
        Ok::<(), String>(())
    })
    .await
    .map_err(|_| "native_submit_client_timeout".to_string())??;

    let (tag, body) = timeout(
        Duration::from_millis(config.timeout_ms),
        read_response_frame(&mut recv),
    )
    .await
    .map_err(|_| "native_submit_client_timeout".to_string())??;
    println!("{}", String::from_utf8_lossy(&body));
    if tag == OK_TAG {
        Ok(())
    } else if tag == ERR_TAG {
        std::process::exit(1);
    } else {
        Err("native_submit_client_response_tag_invalid".to_string())
    }
}

async fn read_response_frame(recv: &mut RecvStream) -> Result<(u8, Vec<u8>), String> {
    let tag = recv
        .read_u8()
        .await
        .map_err(|_| "native_submit_client_response_header_invalid".to_string())?;
    let length = recv
        .read_u32()
        .await
        .map_err(|_| "native_submit_client_response_length_missing".to_string())?;
    let length = usize::try_from(length)
        .map_err(|_| "native_submit_client_response_length_invalid".to_string())?;
    if length == 0 || length > MAX_FRAME_BYTES {
        return Err("native_submit_client_response_length_exceeded".to_string());
    }
    let mut body = vec![0u8; length];
    recv.read_exact(&mut body)
        .await
        .map_err(|_| "native_submit_client_response_body_truncated".to_string())?;
    let mut trailing = [0u8; 1];
    match recv.read(&mut trailing).await {
        Ok(None) => {}
        Ok(Some(_)) => return Err("native_submit_client_response_trailing_bytes".to_string()),
        Err(_) => return Err("native_submit_client_response_trailing_read_failed".to_string()),
    }
    serde_json::from_slice::<serde_json::Value>(&body)
        .map_err(|_| "native_submit_client_response_json_invalid".to_string())?;
    Ok((tag, body))
}

fn parse_args(args: Vec<String>) -> Result<Config, String> {
    let mut endpoint = None;
    let mut expected_tls_fingerprint = None;
    let mut alpn = ALPN_DEFAULT.to_string();
    let mut timeout_ms = 10_000_u64;
    let mut i = 0;
    while i < args.len() {
        match args[i].as_str() {
            "--endpoint" => {
                i += 1;
                endpoint = args.get(i).cloned();
            }
            "--expected-tls-fingerprint" => {
                i += 1;
                expected_tls_fingerprint =
                    Some(require_sha256_hex(args.get(i).ok_or_else(|| {
                        "native_submit_client_arg_missing".to_string()
                    })?)?);
            }
            "--alpn" => {
                i += 1;
                alpn = args
                    .get(i)
                    .cloned()
                    .ok_or_else(|| "native_submit_client_arg_missing".to_string())?;
                if alpn.trim().is_empty() || alpn.len() > 255 {
                    return Err("native_submit_client_alpn_invalid".to_string());
                }
            }
            "--timeout-ms" => {
                i += 1;
                timeout_ms = args
                    .get(i)
                    .ok_or_else(|| "native_submit_client_arg_missing".to_string())?
                    .parse()
                    .map_err(|_| "native_submit_client_timeout_invalid".to_string())?;
                if timeout_ms == 0 {
                    return Err("native_submit_client_timeout_invalid".to_string());
                }
            }
            _ => return Err("native_submit_client_arg_invalid".to_string()),
        }
        i += 1;
    }
    Ok(Config {
        endpoint: endpoint.ok_or_else(|| "native_submit_client_endpoint_missing".to_string())?,
        expected_tls_fingerprint,
        alpn,
        timeout_ms,
    })
}

fn require_sha256_hex(value: &str) -> Result<String, String> {
    if value.len() == 64
        && value
            .bytes()
            .all(|b| matches!(b, b'0'..=b'9' | b'a'..=b'f'))
    {
        Ok(value.to_string())
    } else {
        Err("native_submit_client_tls_fingerprint_invalid".to_string())
    }
}

fn resolve_endpoint(endpoint: &str) -> Result<(String, SocketAddr), String> {
    let (host, _port) = endpoint
        .rsplit_once(':')
        .ok_or_else(|| "native_submit_client_endpoint_invalid".to_string())?;
    if host.trim().is_empty() {
        return Err("native_submit_client_endpoint_invalid".to_string());
    }
    let addr = endpoint
        .to_socket_addrs()
        .map_err(|_| "native_submit_client_endpoint_invalid".to_string())?
        .next()
        .ok_or_else(|| "native_submit_client_endpoint_invalid".to_string())?;
    Ok((host.to_string(), addr))
}

fn build_client_config(
    expected_tls_fingerprint: Option<String>,
    alpn: Vec<u8>,
) -> Result<quinn::ClientConfig, String> {
    let tls = if let Some(expected_sha256_hex) = expected_tls_fingerprint {
        rustls::ClientConfig::builder()
            .dangerous()
            .with_custom_certificate_verifier(Arc::new(FingerprintVerifier {
                expected_sha256_hex,
            }))
            .with_no_client_auth()
    } else {
        let mut roots = rustls::RootCertStore::empty();
        roots.extend(webpki_roots::TLS_SERVER_ROOTS.iter().cloned());
        rustls::ClientConfig::builder()
            .with_root_certificates(roots)
            .with_no_client_auth()
    };
    let mut tls = tls;
    tls.alpn_protocols = vec![alpn];
    let quic_tls = quinn::crypto::rustls::QuicClientConfig::try_from(tls)
        .map_err(|_| "native_submit_client_quic_tls_config_invalid".to_string())?;
    Ok(quinn::ClientConfig::new(Arc::new(quic_tls)))
}

fn frame(tag: u8, body: &[u8]) -> Vec<u8> {
    let body_len = u32::try_from(body.len()).expect("frame body exceeds u32 max");
    let mut out = Vec::with_capacity(1 + 4 + body.len());
    out.push(tag);
    out.extend_from_slice(&body_len.to_be_bytes());
    out.extend_from_slice(body);
    out
}

fn hex_lower(bytes: &[u8]) -> String {
    const HEX: &[u8; 16] = b"0123456789abcdef";
    let mut out = String::with_capacity(bytes.len() * 2);
    for byte in bytes {
        out.push(HEX[(byte >> 4) as usize] as char);
        out.push(HEX[(byte & 0x0f) as usize] as char);
    }
    out
}
