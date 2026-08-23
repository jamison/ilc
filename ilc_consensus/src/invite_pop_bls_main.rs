use blst::min_pk::{PublicKey, SecretKey, Signature};
use std::env;
use std::fs;
use std::io::{self, Read};
use std::path::PathBuf;

const ILC_INVITE_POP_DST: &[u8] = b"ILC_INVITE_POP_V1_BLS12381G2_XMD:SHA-256_SSWU_RO_";

fn main() {
    if let Err(err) = run() {
        eprintln!("{}", err);
        std::process::exit(1);
    }
}

fn run() -> Result<(), String> {
    let mut args = env::args().skip(1);
    let command = args.next().ok_or("missing command: sign or verify")?;
    let message = read_message_hex_from_stdin()?;
    match command.as_str() {
        "sign" => {
            let key_path = parse_required_arg(&mut args, "--secret-key")?;
            ensure_no_extra_args(args)?;
            let sk = load_secret_key(&PathBuf::from(key_path))?;
            let sig = sk.sign(&message, ILC_INVITE_POP_DST, &[]);
            println!("{}", hex_encode(&sig.to_bytes()));
            Ok(())
        }
        "verify" => {
            let public_key_hex = parse_required_arg(&mut args, "--public-key-hex")?;
            let signature_hex = parse_required_arg(&mut args, "--signature-hex")?;
            ensure_no_extra_args(args)?;
            let pk_bytes = hex_decode_exact(&public_key_hex, 48)?;
            let sig_bytes = hex_decode_exact(&signature_hex, 96)?;
            let pk = PublicKey::from_bytes(&pk_bytes).map_err(|_| "invalid public key bytes")?;
            let sig = Signature::from_bytes(&sig_bytes).map_err(|_| "invalid signature bytes")?;
            pk.validate().map_err(|_| "invalid public key subgroup")?;
            sig.validate(true)
                .map_err(|_| "invalid signature subgroup or infinity")?;
            let result = sig.verify(true, &message, ILC_INVITE_POP_DST, &[], &pk, true);
            if result == blst::BLST_ERROR::BLST_SUCCESS {
                println!("invite_pop_bls_valid");
                Ok(())
            } else {
                Err("invite_pop_bls_invalid".to_string())
            }
        }
        _ => Err("unknown command: expected sign or verify".to_string()),
    }
}

fn read_message_hex_from_stdin() -> Result<Vec<u8>, String> {
    const SHA384_HEX_CHARS: usize = 96;
    const MAX_STDIN_BYTES: usize = 128;
    let mut stdin = String::new();
    io::stdin()
        .take((MAX_STDIN_BYTES + 1) as u64)
        .read_to_string(&mut stdin)
        .map_err(|e| format!("stdin read failed: {}", e))?;
    if stdin.len() > MAX_STDIN_BYTES {
        return Err("message hex input exceeds 128 bytes".to_string());
    }
    let value = stdin.trim();
    if value.len() != SHA384_HEX_CHARS {
        return Err(format!(
            "message hex length mismatch: expected {} chars, got {}",
            SHA384_HEX_CHARS,
            value.len()
        ));
    }
    hex_decode_exact(value, 48)
}

fn parse_required_arg(
    args: &mut impl Iterator<Item = String>,
    name: &str,
) -> Result<String, String> {
    let flag = args.next().ok_or_else(|| format!("missing {}", name))?;
    if flag != name {
        return Err(format!("expected {}, got {}", name, flag));
    }
    args.next()
        .ok_or_else(|| format!("missing value for {}", name))
}

fn ensure_no_extra_args(mut args: impl Iterator<Item = String>) -> Result<(), String> {
    if let Some(extra) = args.next() {
        return Err(format!("unexpected extra argument {}", extra));
    }
    Ok(())
}

fn load_secret_key(path: &PathBuf) -> Result<SecretKey, String> {
    let raw = fs::read_to_string(path)
        .map_err(|e| format!("cannot read secret key '{}': {}", path.display(), e))?;
    let bytes = hex_decode_exact(raw.trim(), 32)?;
    SecretKey::from_bytes(&bytes).map_err(|_| "invalid BLS secret key bytes".to_string())
}

fn hex_decode_exact(value: &str, expected_len: usize) -> Result<Vec<u8>, String> {
    if value.len() != expected_len * 2 {
        return Err(format!(
            "hex length mismatch: expected {} chars, got {}",
            expected_len * 2,
            value.len()
        ));
    }
    if !value
        .bytes()
        .all(|byte| matches!(byte, b'0'..=b'9' | b'a'..=b'f'))
    {
        return Err("hex must be lowercase".to_string());
    }
    let mut out = Vec::with_capacity(expected_len);
    let bytes = value.as_bytes();
    for index in (0..bytes.len()).step_by(2) {
        let hi = hex_nibble(bytes[index])?;
        let lo = hex_nibble(bytes[index + 1])?;
        out.push((hi << 4) | lo);
    }
    Ok(out)
}

fn hex_nibble(byte: u8) -> Result<u8, String> {
    match byte {
        b'0'..=b'9' => Ok(byte - b'0'),
        b'a'..=b'f' => Ok(byte - b'a' + 10),
        _ => Err("hex must be lowercase".to_string()),
    }
}

fn hex_encode(bytes: &[u8]) -> String {
    const HEX: &[u8; 16] = b"0123456789abcdef";
    let mut out = String::with_capacity(bytes.len() * 2);
    for byte in bytes {
        out.push(HEX[(byte >> 4) as usize] as char);
        out.push(HEX[(byte & 0x0f) as usize] as char);
    }
    out
}
