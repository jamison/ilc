use serde::Deserialize;
use std::env;

const MAX_REQUEST_JSON_BYTES: usize = 140_000;
const MAX_ENDPOINT_ID_CHARS: usize = 256;
const MAX_PAYLOAD_BYTES: usize = 65_536;

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct SendRequest {
    endpoint_id: String,
    payload_hex: String,
}

fn main() {
    if let Err(err) = run() {
        eprintln!("{err}");
        std::process::exit(1);
    }
}

fn run() -> Result<(), String> {
    let args: Vec<String> = env::args().collect();
    if args.len() == 2 && args[1] == "--help" {
        print_help();
        return Ok(());
    }
    if args.len() != 4 || args[1] != "send" || args[2] != "--request-json" {
        return Err("usage: ilc_p2p_bridge send --request-json <json>".to_string());
    }
    let request = validate_send_request(&args[3])?;
    let response = serde_json::json!({
        "endpoint_id": request.endpoint_id,
        "payload_bytes": request.payload_hex.len() / 2,
        "status": "accepted",
    });
    println!("{response}");
    Ok(())
}

fn validate_send_request(raw: &str) -> Result<SendRequest, String> {
    if raw.len() > MAX_REQUEST_JSON_BYTES {
        return Err("rust_p2p_bridge_request_json_too_large".to_string());
    }
    let request: SendRequest = serde_json::from_str(raw)
        .map_err(|err| format!("rust_p2p_bridge_request_json_invalid:{err}"))?;
    require_endpoint_id(&request.endpoint_id)?;
    require_payload_hex(&request.payload_hex)?;
    Ok(request)
}

fn require_endpoint_id(value: &str) -> Result<(), String> {
    let clean = value.trim();
    if clean.is_empty()
        || clean.len() != value.len()
        || clean.len() > MAX_ENDPOINT_ID_CHARS
        || clean.as_bytes().contains(&0)
    {
        return Err("rust_p2p_bridge_invalid_endpoint_id".to_string());
    }
    Ok(())
}

fn require_payload_hex(value: &str) -> Result<(), String> {
    if value.len() > MAX_PAYLOAD_BYTES * 2 {
        return Err("rust_p2p_bridge_payload_too_large".to_string());
    }
    if value.len() % 2 != 0
        || !value
            .bytes()
            .all(|byte| matches!(byte, b'0'..=b'9' | b'a'..=b'f'))
    {
        return Err("rust_p2p_bridge_payload_hex_invalid".to_string());
    }
    Ok(())
}

fn print_help() {
    println!("usage: ilc_p2p_bridge send --request-json <json>");
    println!("request JSON fields: endpoint_id, payload_hex");
    println!("runtime status: active");
}

#[cfg(test)]
mod tests {
    use super::*;

    fn valid_request() -> String {
        r#"{"endpoint_id":"validator-1","payload_hex":"7061796c6f6164"}"#.to_string()
    }

    #[test]
    fn validates_expected_send_request_shape() {
        let request = validate_send_request(&valid_request()).unwrap();
        assert_eq!(request.endpoint_id, "validator-1");
        assert_eq!(request.payload_hex, "7061796c6f6164");
    }

    #[test]
    fn rejects_unknown_fields() {
        let err = validate_send_request(
            r#"{"endpoint_id":"validator-1","payload_hex":"00","extra":true}"#,
        )
        .unwrap_err();
        assert!(err.starts_with("rust_p2p_bridge_request_json_invalid:"));
    }

    #[test]
    fn rejects_padded_or_empty_endpoint_id() {
        assert_eq!(
            validate_send_request(r#"{"endpoint_id":" validator-1","payload_hex":"00"}"#)
                .unwrap_err(),
            "rust_p2p_bridge_invalid_endpoint_id"
        );
        assert_eq!(
            validate_send_request(r#"{"endpoint_id":"","payload_hex":"00"}"#).unwrap_err(),
            "rust_p2p_bridge_invalid_endpoint_id"
        );
    }

    #[test]
    fn rejects_payload_hex_errors_and_oversize() {
        assert_eq!(
            validate_send_request(r#"{"endpoint_id":"validator-1","payload_hex":"0"}"#)
                .unwrap_err(),
            "rust_p2p_bridge_payload_hex_invalid"
        );
        assert_eq!(
            validate_send_request(r#"{"endpoint_id":"validator-1","payload_hex":"GG"}"#)
                .unwrap_err(),
            "rust_p2p_bridge_payload_hex_invalid"
        );
        let oversized = format!(
            r#"{{"endpoint_id":"validator-1","payload_hex":"{}"}}"#,
            "00".repeat(MAX_PAYLOAD_BYTES + 1)
        );
        assert_eq!(
            validate_send_request(&oversized).unwrap_err(),
            "rust_p2p_bridge_payload_too_large"
        );
    }
}
