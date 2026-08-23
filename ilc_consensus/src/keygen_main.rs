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
///   keygen --keypair-from-ikm-hex-stdin --out <path>
///                                Read 64hex IKM from stdin; write derived secret key; print public key.
///   keygen --help
///
/// `m011_keygen_binary_present`
use std::fs::{self, OpenOptions};
use std::io::{self, Read, Write};
use std::path::PathBuf;
use zeroize::Zeroize;

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let config = match parse_args(&args) {
        Ok(c) => c,
        Err(e) => {
            eprintln!("Error: {}", e);
            print_usage();
            std::process::exit(1);
        }
    };

    match config.mode {
        Mode::WriteFile(path) => {
            let (mut sk_hex, pk_hex) = generate_keypair();
            if let Err(e) = write_secret_key_file(&path, &sk_hex) {
                eprintln!(
                    "Error: cannot write secret key to '{}': {}",
                    path.display(),
                    e
                );
                std::process::exit(1);
            }
            sk_hex.zeroize();
            // Public key goes to stdout for the operator to copy into genesis.json.
            println!("{}", pk_hex);
            eprintln!("[keygen] secret key written to '{}'", path.display());
            eprintln!(
                "[keygen] public key (96 hex chars, BLS12-381 G1 compressed): {}",
                pk_hex
            );
        }
        Mode::Print => {
            let (mut sk_hex, pk_hex) = generate_keypair();
            println!("sk={}", sk_hex);
            println!("pk={}", pk_hex);
            sk_hex.zeroize();
        }
        Mode::PubkeyFromIkmHexStdin => {
            let mut ikm_hex = match read_ikm_hex_from_stdin() {
                Ok(value) => value,
                Err(err) => {
                    eprintln!("Error: {}", err);
                    std::process::exit(1);
                }
            };
            let result = public_key_from_ikm_hex(ikm_hex.trim());
            ikm_hex.zeroize();
            match result {
                Ok(pk_hex) => println!("{}", pk_hex),
                Err(err) => {
                    eprintln!("Error: {}", err);
                    std::process::exit(1);
                }
            }
        }
        Mode::KeypairFromIkmHexStdin(path) => {
            let mut ikm_hex = match read_ikm_hex_from_stdin() {
                Ok(value) => value,
                Err(err) => {
                    eprintln!("Error: {}", err);
                    std::process::exit(1);
                }
            };
            let result = keypair_from_ikm_hex(ikm_hex.trim());
            ikm_hex.zeroize();
            match result {
                Ok((mut sk_hex, pk_hex)) => {
                    if let Err(e) = write_secret_key_file(&path, &sk_hex) {
                        eprintln!(
                            "Error: cannot write secret key to '{}': {}",
                            path.display(),
                            e
                        );
                        std::process::exit(1);
                    }
                    sk_hex.zeroize();
                    println!("{}", pk_hex);
                    eprintln!("[keygen] secret key written to '{}'", path.display());
                }
                Err(err) => {
                    eprintln!("Error: {}", err);
                    std::process::exit(1);
                }
            }
        }
    }
}

fn read_ikm_hex_from_stdin() -> Result<String, String> {
    const MAX_IKM_STDIN_BYTES: usize = 128;
    let mut ikm_hex = String::new();
    if let Err(err) = io::stdin()
        .take((MAX_IKM_STDIN_BYTES + 1) as u64)
        .read_to_string(&mut ikm_hex)
    {
        return Err(format!("failed to read IKM from stdin: {}", err));
    }
    if ikm_hex.len() > MAX_IKM_STDIN_BYTES {
        return Err("--pubkey-from-ikm-hex-stdin input exceeds 128 bytes".to_string());
    }
    Ok(ikm_hex)
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

    let mut sk_bytes = sk.to_bytes(); // 32 bytes
    let pk_bytes = pk.compress(); // 48 bytes, G1 compressed

    let sk_hex = hex_encode(&sk_bytes);
    let pk_hex = hex_encode(&pk_bytes);

    ikm.zeroize();
    sk_bytes.zeroize();
    (sk_hex, pk_hex)
}

fn public_key_from_ikm_hex(ikm_hex: &str) -> Result<String, String> {
    let (mut sk_hex, pk_hex) = keypair_from_ikm_hex(ikm_hex)?;
    sk_hex.zeroize();
    Ok(pk_hex)
}

fn keypair_from_ikm_hex(ikm_hex: &str) -> Result<(String, String), String> {
    let mut ikm = decode_32_byte_hex(ikm_hex)?;
    let sk = blst::min_pk::SecretKey::key_gen(&ikm, &[])
        .map_err(|_| "blst key_gen failed for supplied IKM".to_string())?;
    let mut sk_bytes = sk.to_bytes();
    let result = (hex_encode(&sk_bytes), hex_encode(&sk.sk_to_pk().compress()));
    ikm.zeroize();
    sk_bytes.zeroize();
    Ok(result)
}

fn write_secret_key_file(path: &PathBuf, sk_hex: &str) -> io::Result<()> {
    let mut options = OpenOptions::new();
    options.write(true).create_new(true);
    #[cfg(unix)]
    {
        use std::os::unix::fs::OpenOptionsExt;
        options.mode(0o600);
    }
    let mut file = options.open(path)?;
    file.write_all(sk_hex.as_bytes())?;
    file.write_all(b"\n")?;
    file.sync_all()?;
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        fs::set_permissions(path, fs::Permissions::from_mode(0o600))?;
    }
    Ok(())
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
        // Safe after the byte-level lowercase-hex validation above.
        out[index] = u8::from_str_radix(&value[index * 2..index * 2 + 2], 16).unwrap();
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

#[derive(Debug)]
enum Mode {
    WriteFile(PathBuf),
    Print,
    PubkeyFromIkmHexStdin,
    KeypairFromIkmHexStdin(PathBuf),
}

#[derive(Debug)]
enum ModeFlag {
    Print,
    PubkeyFromIkmHexStdin,
    KeypairFromIkmHexStdin,
}

#[derive(Debug)]
struct Config {
    mode: Mode,
}

fn parse_args(args: &[String]) -> Result<Config, String> {
    let mut i = 1;
    let mut mode_flag: Option<ModeFlag> = None;
    let mut out_path: Option<PathBuf> = None;

    while i < args.len() {
        match args[i].as_str() {
            "--out" => {
                if out_path.is_some() {
                    return Err("--out specified more than once".to_string());
                }
                i += 1;
                let path = args.get(i).ok_or("--out requires a path argument")?;
                out_path = Some(PathBuf::from(path));
            }
            "--print" => {
                set_mode_flag(&mut mode_flag, ModeFlag::Print)?;
            }
            "--pubkey-from-ikm-hex-stdin" => {
                set_mode_flag(&mut mode_flag, ModeFlag::PubkeyFromIkmHexStdin)?;
            }
            "--keypair-from-ikm-hex-stdin" => {
                set_mode_flag(&mut mode_flag, ModeFlag::KeypairFromIkmHexStdin)?;
            }
            "--help" | "-h" => {
                print_usage();
                std::process::exit(0);
            }
            other => {
                return Err(format!("Unknown argument: {}", other));
            }
        }
        i += 1;
    }

    let mode = match (mode_flag, out_path) {
        (None, Some(path)) => Mode::WriteFile(path),
        (None, None) => Mode::Print,
        (Some(ModeFlag::Print), None) => Mode::Print,
        (Some(ModeFlag::Print), Some(_)) => {
            return Err("--print cannot be combined with --out".to_string())
        }
        (Some(ModeFlag::PubkeyFromIkmHexStdin), None) => Mode::PubkeyFromIkmHexStdin,
        (Some(ModeFlag::PubkeyFromIkmHexStdin), Some(_)) => {
            return Err("--pubkey-from-ikm-hex-stdin cannot be combined with --out".to_string())
        }
        (Some(ModeFlag::KeypairFromIkmHexStdin), Some(path)) => Mode::KeypairFromIkmHexStdin(path),
        (Some(ModeFlag::KeypairFromIkmHexStdin), None) => {
            return Err("--keypair-from-ikm-hex-stdin requires --out <path>".to_string())
        }
    };
    Ok(Config { mode })
}

fn set_mode_flag(target: &mut Option<ModeFlag>, next: ModeFlag) -> Result<(), String> {
    if target.is_some() {
        return Err("conflicting keygen mode flags".to_string());
    }
    *target = Some(next);
    Ok(())
}

fn print_usage() {
    eprintln!("Usage: keygen --out <path>   # write random sk to file, print pk to stdout");
    eprintln!("       keygen --print        # print random keypair to stdout");
    eprintln!("       keygen --pubkey-from-ikm-hex-stdin");
    eprintln!("       keygen --keypair-from-ikm-hex-stdin --out <path>");
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::process;

    #[test]
    fn test_ikm_public_key_matches_keypair_public_key() {
        let ikm_hex = "11".repeat(32);

        let public_only = public_key_from_ikm_hex(&ikm_hex).unwrap();
        let (sk_hex, public_from_keypair) = keypair_from_ikm_hex(&ikm_hex).unwrap();
        let sk_bytes = hex_decode_exact_vec(&sk_hex, 32).unwrap();
        let sk = blst::min_pk::SecretKey::from_bytes(&sk_bytes).unwrap();

        assert_eq!(public_only, public_from_keypair);
        assert_eq!(public_only, hex_encode(&sk.sk_to_pk().compress()));
    }

    #[test]
    fn test_decode_32_byte_hex_rejects_uppercase_and_all_zero() {
        assert!(decode_32_byte_hex(&"AA".repeat(32))
            .unwrap_err()
            .contains("lowercase hex"));
        assert!(decode_32_byte_hex(&"00".repeat(32))
            .unwrap_err()
            .contains("must not be all zero"));
    }

    #[test]
    fn test_parse_args_rejects_conflicting_modes() {
        let args = vec![
            "keygen".to_string(),
            "--print".to_string(),
            "--pubkey-from-ikm-hex-stdin".to_string(),
        ];

        assert_eq!(
            parse_args(&args).unwrap_err(),
            "conflicting keygen mode flags"
        );
    }

    #[test]
    fn test_parse_args_requires_out_for_ikm_keypair_mode() {
        let args = vec![
            "keygen".to_string(),
            "--keypair-from-ikm-hex-stdin".to_string(),
        ];

        assert!(parse_args(&args).unwrap_err().contains("requires --out"));
    }

    #[test]
    fn test_write_secret_key_file_uses_restrictive_permissions() {
        let path = std::env::temp_dir().join(format!(
            "ilc_keygen_test_{}_{}.hex",
            process::id(),
            "restrictive"
        ));
        let _ = fs::remove_file(&path);

        write_secret_key_file(&path, &"12".repeat(32)).unwrap();
        let written = fs::read_to_string(&path).unwrap();
        assert_eq!(written, format!("{}\n", "12".repeat(32)));

        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            let mode = fs::metadata(&path).unwrap().permissions().mode() & 0o777;
            assert_eq!(mode, 0o600);
        }

        fs::remove_file(&path).unwrap();
    }

    #[test]
    fn test_write_secret_key_file_rejects_existing_path() {
        let path = std::env::temp_dir().join(format!(
            "ilc_keygen_test_{}_{}.hex",
            process::id(),
            "existing"
        ));
        let _ = fs::remove_file(&path);
        fs::write(&path, "existing\n").unwrap();

        let err = write_secret_key_file(&path, &"34".repeat(32)).unwrap_err();

        assert_eq!(err.kind(), io::ErrorKind::AlreadyExists);
        assert_eq!(fs::read_to_string(&path).unwrap(), "existing\n");
        fs::remove_file(&path).unwrap();
    }

    fn hex_decode_exact_vec(hex: &str, expected_len: usize) -> Result<Vec<u8>, String> {
        if hex.len() != expected_len * 2 {
            return Err("bad length".to_string());
        }
        (0..hex.len())
            .step_by(2)
            .map(|i| u8::from_str_radix(&hex[i..i + 2], 16).map_err(|err| err.to_string()))
            .collect()
    }
}
