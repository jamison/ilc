use quinn::{Endpoint, RecvStream, SendStream};
use rustls::pki_types::{CertificateDer, PrivateKeyDer};
use serde_json::json;
use std::env;
use std::fs::File;
use std::io::BufReader;
use std::net::SocketAddr;
use std::path::PathBuf;
use std::sync::Arc;
use std::time::Duration;
use tokio::io::{AsyncBufReadExt, AsyncReadExt, AsyncWriteExt, BufReader as TokioBufReader};
use tokio::net::UnixStream;
use tokio::sync::Mutex;
use tokio::time::timeout;

const DEFAULT_BIND_ADDR: &str = "0.0.0.0:4433";
const DEFAULT_SOCKET_PATH: &str = "/tmp/ilc_submit_bridge.sock";
const DEFAULT_POOL_SIZE: usize = 4;
const ALPN: &[u8] = b"ilc-native-submit-v1";
const REQUEST_TAG: u8 = 0x01;
const OK_TAG: u8 = 0x81;
const ERR_TAG: u8 = 0xff;
const MAX_FRAME_BYTES: usize = 1_048_576;
const MAX_WORKER_RESPONSE_BYTES: usize = 65_536;
const WORKER_TIMEOUT: Duration = Duration::from_secs(30);

struct WorkerPool {
    socket_path: PathBuf,
    streams: Mutex<Vec<UnixStream>>,
}

type SharedPool = Arc<WorkerPool>;

#[tokio::main]
async fn main() {
    if let Err(err) = run().await {
        eprintln!("{err}");
        std::process::exit(1);
    }
}

async fn run() -> Result<(), String> {
    let _ = rustls::crypto::ring::default_provider().install_default();

    let bind_addr: SocketAddr = env::var("ILC_SUBMIT_RECEIVER_BIND_ADDR")
        .unwrap_or_else(|_| DEFAULT_BIND_ADDR.to_string())
        .parse()
        .map_err(|_| "native_submit_receiver_bind_addr_invalid".to_string())?;
    let cert_path = required_env_path("ILC_SUBMIT_RECEIVER_TLS_CERT")?;
    let key_path = required_env_path("ILC_SUBMIT_RECEIVER_TLS_KEY")?;
    let socket_path = PathBuf::from(
        env::var("ILC_SUBMIT_BRIDGE_SOCKET").unwrap_or_else(|_| DEFAULT_SOCKET_PATH.to_string()),
    );
    let pool_size = parse_pool_size()?;

    let server_config = build_server_config(cert_path, key_path)?;
    let endpoint = Endpoint::server(server_config, bind_addr)
        .map_err(|_| "native_submit_receiver_endpoint_bind_failed".to_string())?;
    let pool = Arc::new(WorkerPool {
        socket_path: socket_path.clone(),
        streams: Mutex::new(build_worker_pool(&socket_path, pool_size).await?),
    });

    while let Some(incoming) = endpoint.accept().await {
        let pool = pool.clone();
        tokio::spawn(async move {
            match incoming.await {
                Ok(connection) => {
                    while let Ok((send, recv)) = connection.accept_bi().await {
                        let pool = pool.clone();
                        tokio::spawn(async move {
                            if let Err(err) = handle_stream(send, recv, pool).await {
                                eprintln!("native_submit_receiver_stream_failed:{err}");
                            }
                        });
                    }
                }
                Err(err) => eprintln!("native_submit_receiver_connection_failed:{err}"),
            }
        });
    }
    Ok(())
}

fn required_env_path(name: &str) -> Result<PathBuf, String> {
    let value =
        env::var(name).map_err(|_| "native_submit_receiver_tls_config_missing".to_string())?;
    if value.trim().is_empty() {
        return Err("native_submit_receiver_tls_config_missing".to_string());
    }
    Ok(PathBuf::from(value))
}

fn parse_pool_size() -> Result<usize, String> {
    match env::var("ILC_SUBMIT_BRIDGE_POOL_SIZE") {
        Ok(value) => {
            let parsed = value
                .parse::<usize>()
                .map_err(|_| "native_submit_bridge_pool_size_invalid".to_string())?;
            if parsed == 0 {
                Err("native_submit_bridge_pool_size_invalid".to_string())
            } else {
                Ok(parsed)
            }
        }
        Err(_) => Ok(DEFAULT_POOL_SIZE),
    }
}

fn build_server_config(
    cert_path: PathBuf,
    key_path: PathBuf,
) -> Result<quinn::ServerConfig, String> {
    let certs = load_certs(cert_path)?;
    let key = load_private_key(key_path)?;
    let mut tls = rustls::ServerConfig::builder()
        .with_no_client_auth()
        .with_single_cert(certs, key)
        .map_err(|_| "native_submit_receiver_tls_config_invalid".to_string())?;
    tls.alpn_protocols = vec![ALPN.to_vec()];
    let quic_tls = quinn::crypto::rustls::QuicServerConfig::try_from(tls)
        .map_err(|_| "native_submit_receiver_quic_tls_config_invalid".to_string())?;
    Ok(quinn::ServerConfig::with_crypto(Arc::new(quic_tls)))
}

fn load_certs(path: PathBuf) -> Result<Vec<CertificateDer<'static>>, String> {
    let file =
        File::open(path).map_err(|_| "native_submit_receiver_tls_config_missing".to_string())?;
    let mut reader = BufReader::new(file);
    let certs = rustls_pemfile::certs(&mut reader)
        .collect::<Result<Vec<_>, _>>()
        .map_err(|_| "native_submit_receiver_tls_config_invalid".to_string())?;
    if certs.is_empty() {
        return Err("native_submit_receiver_tls_config_invalid".to_string());
    }
    Ok(certs)
}

fn load_private_key(path: PathBuf) -> Result<PrivateKeyDer<'static>, String> {
    let file =
        File::open(path).map_err(|_| "native_submit_receiver_tls_config_missing".to_string())?;
    let mut reader = BufReader::new(file);
    rustls_pemfile::private_key(&mut reader)
        .map_err(|_| "native_submit_receiver_tls_config_invalid".to_string())?
        .ok_or_else(|| "native_submit_receiver_tls_config_invalid".to_string())
}

async fn build_worker_pool(
    socket_path: &PathBuf,
    pool_size: usize,
) -> Result<Vec<UnixStream>, String> {
    let mut pool = Vec::with_capacity(pool_size);
    for _ in 0..pool_size {
        pool.push(connect_worker(socket_path).await?);
    }
    Ok(pool)
}

async fn connect_worker(socket_path: &PathBuf) -> Result<UnixStream, String> {
    let mut last_error = "native_submit_bridge_socket_unavailable".to_string();
    for _ in 0..50 {
        match UnixStream::connect(socket_path).await {
            Ok(stream) => return Ok(stream),
            Err(err) => {
                last_error = format!("native_submit_bridge_socket_unavailable:{err}");
                tokio::time::sleep(Duration::from_millis(100)).await;
            }
        }
    }
    Err(last_error)
}

async fn handle_stream(
    mut send: SendStream,
    mut recv: RecvStream,
    pool: SharedPool,
) -> Result<(), String> {
    // Request-frame read and worker roundtrip have separate 30s limits; worst
    // case for a malformed/slow stream is therefore bounded by both phases.
    let response = match timeout(WORKER_TIMEOUT, read_request_frame(&mut recv)).await {
        Ok(Ok(envelope_bytes)) => match worker_roundtrip(pool, envelope_bytes).await {
            Ok(receipt) => worker_receipt_frame(receipt),
            Err(token) => error_frame(&token),
        },
        Ok(Err(token)) => error_frame(&token),
        Err(_) => error_frame("native_submit_frame_read_timeout"),
    };
    send.write_all(&response)
        .await
        .map_err(|_| "native_submit_receiver_response_write_failed".to_string())?;
    send.finish()
        .map_err(|_| "native_submit_receiver_response_finish_failed".to_string())?;
    Ok(())
}

fn worker_receipt_frame(receipt: Vec<u8>) -> Vec<u8> {
    match serde_json::from_slice::<serde_json::Value>(&receipt) {
        Ok(value) if value.get("ok").and_then(serde_json::Value::as_bool) == Some(true) => {
            success_frame(receipt)
        }
        Ok(_) => frame(ERR_TAG, &receipt),
        Err(_) => error_frame("native_submit_bridge_worker_response_invalid"),
    }
}

async fn read_request_frame(recv: &mut RecvStream) -> Result<Vec<u8>, String> {
    let tag = recv
        .read_u8()
        .await
        .map_err(|_| "native_submit_frame_header_invalid".to_string())?;
    if tag != REQUEST_TAG {
        return Err("native_submit_frame_type_invalid".to_string());
    }
    let length = recv
        .read_u32()
        .await
        .map_err(|_| "native_submit_frame_length_missing".to_string())?;
    let length =
        usize::try_from(length).map_err(|_| "native_submit_frame_length_invalid".to_string())?;
    if length == 0 || length > MAX_FRAME_BYTES {
        return Err("native_submit_frame_length_exceeded".to_string());
    }
    let mut payload = vec![0u8; length];
    recv.read_exact(&mut payload)
        .await
        .map_err(|_| "native_submit_frame_body_truncated".to_string())?;
    let mut trailing = [0u8; 1];
    match recv.read(&mut trailing).await {
        Ok(None) => {}
        Ok(Some(_)) => return Err("native_submit_frame_trailing_bytes".to_string()),
        Err(_) => return Err("native_submit_frame_trailing_read_failed".to_string()),
    }
    if std::str::from_utf8(&payload).is_err() {
        return Err("native_submit_frame_body_not_utf8".to_string());
    }
    if payload.iter().any(|b| matches!(b, b'\n' | b'\r')) {
        return Err("native_submit_frame_body_not_single_line_json".to_string());
    }
    serde_json::from_slice::<serde_json::Value>(&payload)
        .map_err(|_| "native_submit_frame_body_json_invalid".to_string())?;
    Ok(payload)
}

async fn worker_roundtrip(pool: SharedPool, envelope_bytes: Vec<u8>) -> Result<Vec<u8>, String> {
    let mut stream = {
        let mut guard = pool.streams.lock().await;
        guard
            .pop()
            .ok_or_else(|| "native_submit_bridge_pool_exhausted".to_string())?
    };

    let response = timeout(WORKER_TIMEOUT, async {
        stream
            .write_all(&envelope_bytes)
            .await
            .map_err(|_| "native_submit_bridge_worker_write_failed".to_string())?;
        stream
            .write_all(b"\n")
            .await
            .map_err(|_| "native_submit_bridge_worker_write_failed".to_string())?;
        stream
            .flush()
            .await
            .map_err(|_| "native_submit_bridge_worker_write_failed".to_string())?;
        let mut reader = TokioBufReader::new(&mut stream);
        let line = read_worker_response_line(&mut reader).await?;
        serde_json::from_slice::<serde_json::Value>(&line)
            .map_err(|_| "native_submit_bridge_worker_response_invalid".to_string())?;
        Ok(line)
    })
    .await
    .map_err(|_| "native_submit_bridge_worker_timeout".to_string())?;

    match response {
        Ok(line) => {
            let mut guard = pool.streams.lock().await;
            guard.push(stream);
            Ok(line)
        }
        Err(token) => {
            replenish_worker_pool(&pool).await;
            Err(token)
        }
    }
}

async fn replenish_worker_pool(pool: &SharedPool) {
    match connect_worker(&pool.socket_path).await {
        Ok(stream) => {
            let mut guard = pool.streams.lock().await;
            guard.push(stream);
        }
        Err(err) => eprintln!("native_submit_bridge_pool_replenish_failed:{err}"),
    }
}

async fn read_worker_response_line(
    reader: &mut TokioBufReader<&mut UnixStream>,
) -> Result<Vec<u8>, String> {
    let mut line = Vec::new();
    loop {
        let available = reader
            .fill_buf()
            .await
            .map_err(|_| "native_submit_bridge_worker_read_failed".to_string())?;
        if available.is_empty() {
            return if line.is_empty() {
                Err("native_submit_bridge_worker_closed".to_string())
            } else {
                Err("native_submit_bridge_worker_response_truncated".to_string())
            };
        }
        let take = match available.iter().position(|byte| *byte == b'\n') {
            Some(index) => index + 1,
            None => available.len(),
        };
        if line.len().saturating_add(take) > MAX_WORKER_RESPONSE_BYTES {
            return Err("native_submit_bridge_worker_response_too_large".to_string());
        }
        line.extend_from_slice(&available[..take]);
        reader.consume(take);
        if line.ends_with(b"\n") {
            line.pop();
            return Ok(line);
        }
    }
}

fn success_frame(receipt_json: Vec<u8>) -> Vec<u8> {
    frame(OK_TAG, &receipt_json)
}

fn error_frame(token: &str) -> Vec<u8> {
    let body = serde_json::to_vec(&json!({"ok": false, "error": token})).unwrap_or_else(|_| {
        b"{\"ok\":false,\"error\":\"native_submit_receiver_internal_error\"}".to_vec()
    });
    frame(ERR_TAG, &body)
}

fn frame(tag: u8, body: &[u8]) -> Vec<u8> {
    let body_len = u32::try_from(body.len()).expect("frame body exceeds u32 max");
    let mut out = Vec::with_capacity(1 + 4 + body.len());
    out.push(tag);
    out.extend_from_slice(&body_len.to_be_bytes());
    out.extend_from_slice(body);
    out
}
