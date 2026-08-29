use blst::min_pk::{PublicKey, Signature};
use std::env;
use std::io::{self, Read};

const ILC_INVITE_POP_DST: &[u8] = b"ILC_INVITE_POP_V1_BLS12381G2_XMD:SHA-256_SSWU_RO_";
const ILC_RELAY_ADMISSION_DST: &[u8] = b"ILC_RELAY_ADMISSION_V1_BLS12381G2_XMD:SHA-256_SSWU_RO_";
const ILC_RELAY_LIFECYCLE_DST: &[u8] = b"ILC_RELAY_LIFECYCLE_V1_BLS12381G2_XMD:SHA-256_SSWU_RO_";
const ILC_RELAY_BOOTSTRAP_RECORD_DST: &[u8] =
    b"ILC_RELAY_BOOTSTRAP_RECORD_V1_BLS12381G2_XMD:SHA-256_SSWU_RO_";
const ILC_RELAY_BOOTSTRAP_CAPSULE_DST: &[u8] =
    b"ILC_RELAY_BOOTSTRAP_CAPSULE_V1_BLS12381G2_XMD:SHA-256_SSWU_RO_";

fn main() {
    if let Err(err) = run() {
        eprintln!("{}", err);
        std::process::exit(1);
    }
}

fn run() -> Result<(), String> {
    let mut args = env::args().skip(1);
    let public_key_hex = parse_required_arg(&mut args, "--public-key-hex")?;
    let signature_hex = parse_required_arg(&mut args, "--signature-hex")?;
    let suite = parse_required_arg(&mut args, "--suite")?;
    ensure_no_extra_args(args)?;

    let digest = read_digest_hex_from_stdin()?;
    let pk_bytes = hex_decode_exact(&public_key_hex, 48)?;
    let sig_bytes = hex_decode_exact(&signature_hex, 96)?;

    let pk = match PublicKey::from_bytes(&pk_bytes) {
        Ok(value) => value,
        Err(_) => {
            println!("false");
            return Ok(());
        }
    };
    if pk.validate().is_err() {
        println!("false");
        return Ok(());
    }

    let sig = match Signature::from_bytes(&sig_bytes) {
        Ok(value) => value,
        Err(_) => {
            println!("false");
            return Ok(());
        }
    };
    if sig.validate(true).is_err() {
        println!("false");
        return Ok(());
    }

    let dst = dst_for_suite(&suite)?;
    let result = sig.verify(true, &digest, dst, &[], &pk, true);
    println!(
        "{}",
        if result == blst::BLST_ERROR::BLST_SUCCESS {
            "true"
        } else {
            "false"
        }
    );
    Ok(())
}

fn read_digest_hex_from_stdin() -> Result<Vec<u8>, String> {
    const SHA384_HEX_CHARS: usize = 96;
    const MAX_STDIN_BYTES: usize = 128;
    let mut stdin = String::new();
    io::stdin()
        .take((MAX_STDIN_BYTES + 1) as u64)
        .read_to_string(&mut stdin)
        .map_err(|e| format!("stdin read failed: {}", e))?;
    if stdin.len() > MAX_STDIN_BYTES {
        return Err("digest hex input exceeds 128 bytes".to_string());
    }
    let value = stdin.trim();
    if value.len() != SHA384_HEX_CHARS {
        return Err(format!(
            "digest hex length mismatch: expected {} chars, got {}",
            SHA384_HEX_CHARS,
            value.len()
        ));
    }
    hex_decode_exact(value, 48)
}

fn dst_for_suite(suite: &str) -> Result<&'static [u8], String> {
    match suite {
        "invite_pop" => Ok(ILC_INVITE_POP_DST),
        "relay_admission" => Ok(ILC_RELAY_ADMISSION_DST),
        "relay_lifecycle" => Ok(ILC_RELAY_LIFECYCLE_DST),
        "relay_bootstrap_record" => Ok(ILC_RELAY_BOOTSTRAP_RECORD_DST),
        "relay_bootstrap_capsule" => Ok(ILC_RELAY_BOOTSTRAP_CAPSULE_DST),
        _ => Err("unknown BLS verification suite".to_string()),
    }
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
