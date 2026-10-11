use ilc_consensus::native_submit_persist::RustTruthPrimitiveGraphStore;
use ilc_consensus::native_submit_validate::validate_native_submit_envelope;
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
use tokio::io::AsyncReadExt;
use tokio::sync::{OwnedSemaphorePermit, Semaphore};
use tokio::time::timeout;

const DEFAULT_BIND_ADDR: &str = "0.0.0.0:4433";
const ALPN: &[u8] = b"ilc-native-submit-v1";
const REQUEST_TAG: u8 = 0x01;
const OK_TAG: u8 = 0x81;
const ERR_TAG: u8 = 0xff;
const MAX_FRAME_BYTES: usize = 1_048_576;
const REQUEST_TIMEOUT: Duration = Duration::from_secs(30);
const DEFAULT_MAX_CONNECTIONS: usize = 128;
const DEFAULT_MAX_IN_FLIGHT: usize = 64;

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
    let graph_store_path = env::var("ILC_TRUTH_GRAPH_STORE_PATH")
        .map_err(|_| "native_submit_full_receiver_graph_store_path_missing".to_string())?;
    if graph_store_path.trim().is_empty() {
        return Err("native_submit_full_receiver_graph_store_path_missing".to_string());
    }
    let store = Arc::new(RustTruthPrimitiveGraphStore::open(&graph_store_path)?);
    let connection_slots = Arc::new(Semaphore::new(env_usize(
        "ILC_SUBMIT_RECEIVER_MAX_CONNECTIONS",
        DEFAULT_MAX_CONNECTIONS,
    )?));
    let in_flight_slots = Arc::new(Semaphore::new(env_usize(
        "ILC_SUBMIT_RECEIVER_MAX_IN_FLIGHT",
        DEFAULT_MAX_IN_FLIGHT,
    )?));

    let server_config = build_server_config(cert_path, key_path)?;
    let endpoint = Endpoint::server(server_config, bind_addr)
        .map_err(|_| "native_submit_receiver_endpoint_bind_failed".to_string())?;

    while let Some(incoming) = endpoint.accept().await {
        let connection_permit = match connection_slots.clone().acquire_owned().await {
            Ok(permit) => permit,
            Err(_) => return Err("native_submit_receiver_connection_limit_closed".to_string()),
        };
        let store = store.clone();
        let in_flight_slots = in_flight_slots.clone();
        tokio::spawn(async move {
            let _connection_permit = connection_permit;
            match incoming.await {
                Ok(connection) => {
                    while let Ok((send, recv)) = connection.accept_bi().await {
                        let stream_permit = match in_flight_slots.clone().acquire_owned().await {
                            Ok(permit) => permit,
                            Err(_) => break,
                        };
                        let store = store.clone();
                        tokio::spawn(async move {
                            if let Err(err) = handle_stream(send, recv, store, stream_permit).await
                            {
                                eprintln!("native_submit_full_receiver_stream_failed:{err}");
                            }
                        });
                    }
                }
                Err(err) => eprintln!("native_submit_full_receiver_connection_failed:{err}"),
            }
        });
    }
    Ok(())
}

async fn handle_stream(
    mut send: SendStream,
    mut recv: RecvStream,
    store: Arc<RustTruthPrimitiveGraphStore>,
    _stream_permit: OwnedSemaphorePermit,
) -> Result<(), String> {
    let response = match timeout(REQUEST_TIMEOUT, read_request_frame(&mut recv)).await {
        Ok(Ok(envelope_bytes)) => {
            let store = store.clone();
            match tokio::task::spawn_blocking(move || accept_envelope(store, envelope_bytes)).await
            {
                Ok(Ok(receipt)) => success_frame(receipt),
                Ok(Err(token)) => error_frame(&token),
                Err(_) => error_frame("native_submit_full_receiver_blocking_task_failed"),
            }
        }
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

fn accept_envelope(
    store: Arc<RustTruthPrimitiveGraphStore>,
    envelope_bytes: Vec<u8>,
) -> Result<Vec<u8>, String> {
    let validated = validate_native_submit_envelope(&envelope_bytes)?;
    let receipt = store.write_submission(&validated)?;
    serde_json::to_vec(&json!({
        "ok": true,
        "node_id": receipt.node_id,
        "nodes_written": receipt.nodes_written,
        "edges_written": receipt.edges_written,
        "native_submit_replay_written": receipt.native_submit_replay_written,
        "primitive": receipt.primitive,
        "version": receipt.version,
        "graph_persistence": "persisted",
        "gossip_delivery": "deferred",
        "receiver_profile": "native_quic_full_rust",
    }))
    .map_err(|_| "native_submit_full_receiver_receipt_encode_failed".to_string())
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

fn required_env_path(name: &str) -> Result<PathBuf, String> {
    let value =
        env::var(name).map_err(|_| "native_submit_receiver_tls_config_missing".to_string())?;
    if value.trim().is_empty() {
        return Err("native_submit_receiver_tls_config_missing".to_string());
    }
    Ok(PathBuf::from(value))
}

fn env_usize(name: &str, default_value: usize) -> Result<usize, String> {
    match env::var(name) {
        Ok(raw) => {
            let value = raw
                .parse::<usize>()
                .map_err(|_| "native_submit_receiver_limit_invalid".to_string())?;
            if value == 0 {
                Err("native_submit_receiver_limit_invalid".to_string())
            } else {
                Ok(value)
            }
        }
        Err(env::VarError::NotPresent) => Ok(default_value),
        Err(_) => Err("native_submit_receiver_limit_invalid".to_string()),
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
