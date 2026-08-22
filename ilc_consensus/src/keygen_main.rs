/// keygen_main.rs — M-011 BLS12-381 validator keypair generator.
///
/// Generates a BLS12-381 G1 keypair suitable for use in genesis.json and
/// validator node configs. Uses blst::min_pk (same crate used by the
/// consensus runtime) so keys are compatible with runtime verification.
///
/// Output:
///   - Public key:  96 hex chars (48 bytes, G1 compressed) → for genesis.json validator_key
///   - Secret key:  64 hex chars (32 bytes) → for validator_consensus_key_path file
///
/// Usage:
///   keygen --out <path>           Write secret key hex to <path>; print pubkey to stdout.
///   keygen --print                Print both keys to stdout (for piping / testing).
///   keygen --pubkey-from-ikm-hex-stdin
///                                Read 64hex IKM from stdin; print only the derived public key.
///   keygen --help
///
/// `m011_keygen_binary_present`
use std::fs;
use std::io::{self, Read};
use std::path::PathBuf;

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let config = match parse_args(&args) {
        Ok(c) => c,
        Err(e) => {
            eprintln!("Error: {}", e);
            eprintln!("Usage: keygen --out <path> | keygen --print");
            std::process::exit(1);
        }
    };

    match config.mode {
        Mode::WriteFile(path) => {
            let (sk_hex, pk_hex) = generate_keypair();
            // Write secret key to file (64 hex chars, no newline issues — write with newline
            // so the file is easily cat-able; load_node_config trims whitespace).
            if let Err(e) = fs::write(&path, format!("{}\n", sk_hex)) {
                eprintln!(
                    "Error: cannot write secret key to '{}': {}",
                    path.display(),
                    e
                );
                std::process::exit(1);
            }
            // Public key goes to stdout for the operator to copy into genesis.json.
            println!("{}", pk_hex);
            eprintln!("[keygen] secret key written to '{}'", path.display());
            eprintln!(
                "[keygen] public key (96 hex chars, BLS12-381 G1 compressed): {}",
                pk_hex
            );
        }
        Mode::Print => {
            let (sk_hex, pk_hex) = generate_keypair();
            println!("sk={}", sk_hex);
            println!("pk={}", pk_hex);
        }
        Mode::PubkeyFromIkmHexStdin => {
            let mut ikm_hex = String::new();
            if let Err(err) = io::stdin().read_to_string(&mut ikm_hex) {
                eprintln!("Error: failed to read IKM from stdin: {}", err);
                std::process::exit(1);
            }
            match public_key_from_ikm_hex(ikm_hex.trim()) {
                Ok(pk_hex) => println!("{}", pk_hex),
                Err(err) => {
                    eprintln!("Error: {}", err);
                    std::process::exit(1);
                }
            }
        }
    }
}

// ---------------------------------------------------------------------------
// Keypair generation
// ---------------------------------------------------------------------------

/// Generate a BLS12-381 G1 keypair using a 32-byte random IKM.
/// Returns (sk_hex, pk_hex).
fn generate_keypair() -> (String, String) {
    // 32 bytes of cryptographically secure random material for the IKM.
    let mut ikm = [0u8; 32];
    getrandom::getrandom(&mut ikm).expect("getrandom failed");

    // blst key_gen derives a secret key from IKM using BLS12-381 key derivation.
    // The DST ("BLS-SIG-KEYGEN-SALT-") is part of the IETF BLS key gen spec.
    let sk = blst::min_pk::SecretKey::key_gen(&ikm, &[])
        .expect("blst key_gen failed — IKM too short (should not happen with 32 bytes)");

    let pk = sk.sk_to_pk();

    let sk_bytes = sk.to_bytes(); // 32 bytes
    let pk_bytes = pk.compress(); // 48 bytes, G1 compressed

    let sk_hex = hex_encode(&sk_bytes);
    let pk_hex = hex_encode(&pk_bytes);

    (sk_hex, pk_hex)
}

fn public_key_from_ikm_hex(ikm_hex: &str) -> Result<String, String> {
    let ikm = decode_32_byte_hex(ikm_hex)?;
    let sk = blst::min_pk::SecretKey::key_gen(&ikm, &[])
        .map_err(|_| "blst key_gen failed for supplied IKM".to_string())?;
    Ok(hex_encode(&sk.sk_to_pk().compress()))
}

fn decode_32_byte_hex(value: &str) -> Result<[u8; 32], String> {
    if value.len() != 64 {
        return Err(format!(
            "--pubkey-from-ikm-hex-stdin input requires exactly 64 lowercase hex chars, got {}",
            value.len()
        ));
    }
    if !value
        .bytes()
        .all(|byte| matches!(byte, b'0'..=b'9' | b'a'..=b'f'))
    {
        return Err("--pubkey-from-ikm-hex-stdin input must be lowercase hex".to_string());
    }
    let mut out = [0u8; 32];
    for index in 0..32 {
        out[index] = u8::from_str_radix(&value[index * 2..index * 2 + 2], 16)
            .map_err(|_| "--pubkey-from-ikm-hex-stdin input must be lowercase hex".to_string())?;
    }
    if out == [0u8; 32] {
        return Err("--pubkey-from-ikm-hex-stdin input must not be all zero".to_string());
    }
    Ok(out)
}

fn hex_encode(bytes: &[u8]) -> String {
    bytes.iter().map(|b| format!("{:02x}", b)).collect()
}

// ---------------------------------------------------------------------------
// Argument parsing
// ---------------------------------------------------------------------------

enum Mode {
    WriteFile(PathBuf),
    Print,
    PubkeyFromIkmHexStdin,
}

struct Config {
    mode: Mode,
}

fn parse_args(args: &[String]) -> Result<Config, String> {
    let mut i = 1;
    let mut mode: Option<Mode> = None;

    while i < args.len() {
        match args[i].as_str() {
            "--out" => {
                i += 1;
                let path = args.get(i).ok_or("--out requires a path argument")?;
                mode = Some(Mode::WriteFile(PathBuf::from(path)));
            }
            "--print" => {
                mode = Some(Mode::Print);
            }
            "--pubkey-from-ikm-hex-stdin" => {
                mode = Some(Mode::PubkeyFromIkmHexStdin);
            }
            "--help" | "-h" => {
                eprintln!("Usage: keygen --out <path>   # write sk to file, print pk to stdout");
                eprintln!("       keygen --print        # print both keys to stdout");
                eprintln!("       keygen --pubkey-from-ikm-hex-stdin    # read IKM from stdin, print public key only");
                std::process::exit(0);
            }
            other => {
                return Err(format!("Unknown argument: {}", other));
            }
        }
        i += 1;
    }

    Ok(Config {
        mode: mode.unwrap_or(Mode::Print),
    })
}
