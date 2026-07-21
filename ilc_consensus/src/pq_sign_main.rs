/// pq_sign_main.rs — Phase 1142s Genesis Agent 1 ML-DSA-65 signing tool.
///
/// SECURITY CONTRACT:
/// - Secret seed material is read from stdin only.
/// - Secret seed material is never accepted as a CLI argument.
/// - Secret seed material is never written to disk.
/// - The derived public key must match the committed Genesis Agent 1 public key
///   before any signature is emitted.
///
/// Usage:
///   pq_sign --input-file out/genesis_signing_root_envelope_v0.1.json
///   pq_sign verify --input-file out/genesis_signing_root_envelope_v0.1.json --signature-hex <hex>
///
/// `pq_sign_1142s_binary_present`
use std::fs;
use std::io::{self, Read};
use std::path::PathBuf;
use std::process::{Command as ProcessCommand, Stdio};

use bip39::Mnemonic;
use fips204::ml_dsa_65;
use fips204::traits::{KeyGen, SerDes as MldsaSerDes, Signer, Verifier};
use getrandom::getrandom;
use zeroize::Zeroize;

const SIGNING_CONTEXT: &[u8] = b"ILC_GENESIS_ROOT_ENVELOPE_V1";
const DEFAULT_PUBKEY_RECORD: &str = "docs/genesis/genesis_agent1_pubkey_record_838a.txt";

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let result = match parse_args(&args) {
        Command::Sign {
            input_file,
            pubkey_record,
        } => sign_command(&input_file, &pubkey_record),
        Command::Verify {
            input_file,
            pubkey_record,
            signature_hex,
        } => verify_command(&input_file, &pubkey_record, &signature_hex),
        Command::Help => {
            print_usage();
            Ok(())
        }
    };
    if let Err(err) = result {
        eprintln!("{err}");
        std::process::exit(1);
    }
}

enum Command {
    Sign {
        input_file: PathBuf,
        pubkey_record: PathBuf,
    },
    Verify {
        input_file: PathBuf,
        pubkey_record: PathBuf,
        signature_hex: String,
    },
    Help,
}

fn parse_args(args: &[String]) -> Command {
    if args.iter().any(|arg| arg == "--help" || arg == "-h") {
        return Command::Help;
    }
    let mut idx = 1;
    let mut mode = "sign";
    if args.get(idx).is_some_and(|arg| arg == "verify") {
        mode = "verify";
        idx += 1;
    }
    let mut input_file: Option<PathBuf> = None;
    let mut pubkey_record = PathBuf::from(DEFAULT_PUBKEY_RECORD);
    let mut signature_hex: Option<String> = None;
    while idx < args.len() {
        match args[idx].as_str() {
            "--input-file" => {
                idx += 1;
                let Some(path) = args.get(idx) else {
                    fail("--input-file requires a path");
                };
                input_file = Some(PathBuf::from(path));
            }
            "--pubkey-record" => {
                idx += 1;
                let Some(path) = args.get(idx) else {
                    fail("--pubkey-record requires a path");
                };
                pubkey_record = PathBuf::from(path);
            }
            "--signature-hex" => {
                idx += 1;
                let Some(sig) = args.get(idx) else {
                    fail("--signature-hex requires a value");
                };
                signature_hex = Some(sig.clone());
            }
            "--seed" | "--seed-hex" | "--mnemonic" => {
                fail("secret key material must be provided via stdin, not CLI args");
            }
            other => {
                fail(&format!("unknown argument: {other}"));
            }
        }
        idx += 1;
    }
    let Some(input_file) = input_file else {
        fail("--input-file is required");
    };
    match mode {
        "sign" => Command::Sign {
            input_file,
            pubkey_record,
        },
        "verify" => {
            let Some(signature_hex) = signature_hex else {
                fail("verify requires --signature-hex");
            };
            Command::Verify {
                input_file,
                pubkey_record,
                signature_hex,
            }
        }
        _ => unreachable!(),
    }
}

fn sign_command(input_file: &PathBuf, pubkey_record: &PathBuf) -> Result<(), String> {
    let expected_pk_hex = read_mldsa_pk_hex(pubkey_record)?;
    eprintln!("Enter Plate 2 ML-DSA-65 seed as 24 BIP-39 words or 64-char hex, then press Ctrl-D:");
    let seed = read_seed_from_stdin()?;
    let (pk, sk) = ml_dsa_65::KG::try_keygen_with_rng(&mut SeedRng::new(&seed))
        .map_err(|err| format!("ML-DSA-65 key derivation failed: {err}"))?;
    let derived_pk_hex = hex_encode(&pk.clone().into_bytes());
    if derived_pk_hex != expected_pk_hex {
        return Err("derived_mldsa_public_key_does_not_match_repo_record".to_string());
    }
    let message = fs::read(input_file).map_err(|err| format!("cannot read input file: {err}"))?;
    let sig = sk
        .try_sign_with_rng(&mut OsRandom, &message, SIGNING_CONTEXT)
        .map_err(|err| format!("ML-DSA-65 signing failed: {err}"))?;
    println!("{}", hex_encode(&sig));
    Ok(())
}

fn verify_command(
    input_file: &PathBuf,
    pubkey_record: &PathBuf,
    signature_hex: &str,
) -> Result<(), String> {
    let pk_hex = read_mldsa_pk_hex(pubkey_record)?;
    let pk_bytes_vec = hex_decode(&pk_hex)?;
    let pk_bytes: [u8; 1952] = pk_bytes_vec
        .try_into()
        .map_err(|_| "mldsa_public_key_wrong_length".to_string())?;
    let pk = ml_dsa_65::PublicKey::try_from_bytes(pk_bytes)
        .map_err(|err| format!("ML-DSA-65 public key parse failed: {err}"))?;
    let sig_vec = hex_decode(signature_hex.trim())?;
    let sig: [u8; 3309] = sig_vec
        .try_into()
        .map_err(|_| "mldsa_signature_wrong_length".to_string())?;
    let message = fs::read(input_file).map_err(|err| format!("cannot read input file: {err}"))?;
    if !pk.verify(&message, &sig, SIGNING_CONTEXT) {
        return Err("mldsa_signature_verification_failed".to_string());
    }
    println!("signature_verified");
    Ok(())
}

fn read_seed_from_stdin() -> Result<[u8; 32], String> {
    let _echo_guard = TerminalEchoGuard::disable();
    let mut input = String::new();
    let result = io::stdin()
        .read_to_string(&mut input)
        .map_err(|err| format!("cannot read stdin: {err}"))
        .and_then(|_| parse_seed(input.trim()));
    input.zeroize();
    result
}

fn parse_seed(input: &str) -> Result<[u8; 32], String> {
    let word_count = input.split_whitespace().count();
    if word_count == 24 {
        let mnemonic =
            Mnemonic::parse(input).map_err(|err| format!("invalid BIP-39 mnemonic: {err}"))?;
        let entropy = mnemonic.to_entropy();
        return entropy
            .try_into()
            .map_err(|_| "mnemonic_entropy_must_be_32_bytes".to_string());
    }
    if input.chars().any(|ch| ch.is_ascii_alphabetic()) {
        return Err(format!("mnemonic_word_count_must_be_24_got_{word_count}"));
    }
    let bytes = hex_decode(input)?;
    bytes
        .try_into()
        .map_err(|_| "hex_seed_must_be_32_bytes".to_string())
}

fn read_mldsa_pk_hex(path: &PathBuf) -> Result<String, String> {
    let text =
        fs::read_to_string(path).map_err(|err| format!("cannot read pubkey record: {err}"))?;
    for line in text.lines() {
        if let Some((key, value)) = line.split_once(':') {
            if key.trim() == "mldsa_pk_hex" {
                let value = value.trim().to_string();
                if value.is_empty() {
                    return Err("empty_mldsa_pk_hex".to_string());
                }
                return Ok(value);
            }
        }
    }
    Err("mldsa_pk_hex_not_found_in_pubkey_record".to_string())
}

fn hex_decode(input: &str) -> Result<Vec<u8>, String> {
    let input = input.trim();
    if input.len() % 2 != 0 {
        return Err("hex_input_odd_length".to_string());
    }
    let mut out = Vec::with_capacity(input.len() / 2);
    let bytes = input.as_bytes();
    let mut idx = 0;
    while idx < bytes.len() {
        let hi = hex_value(bytes[idx])?;
        let lo = hex_value(bytes[idx + 1])?;
        out.push((hi << 4) | lo);
        idx += 2;
    }
    Ok(out)
}

fn hex_value(byte: u8) -> Result<u8, String> {
    match byte {
        b'0'..=b'9' => Ok(byte - b'0'),
        b'a'..=b'f' => Ok(byte - b'a' + 10),
        b'A'..=b'F' => Ok(byte - b'A' + 10),
        _ => Err("invalid_hex_character".to_string()),
    }
}

fn hex_encode(bytes: &[u8]) -> String {
    bytes.iter().map(|byte| format!("{:02x}", byte)).collect()
}

fn print_usage() {
    eprintln!("Usage:");
    eprintln!("  pq_sign --input-file <path>");
    eprintln!("  pq_sign verify --input-file <path> --signature-hex <hex>");
    eprintln!("Secret seed material is read from stdin only.");
}

fn fail(message: &str) -> ! {
    eprintln!("{message}");
    std::process::exit(1);
}

struct TerminalEchoGuard {
    restore: bool,
}

impl TerminalEchoGuard {
    fn disable() -> Self {
        let restore = run_stty(&["-echo"]);
        Self { restore }
    }
}

impl Drop for TerminalEchoGuard {
    fn drop(&mut self) {
        if self.restore {
            let _ = run_stty(&["echo"]);
            eprintln!();
        }
    }
}

fn run_stty(args: &[&str]) -> bool {
    ProcessCommand::new("stty")
        .args(args)
        .stdin(Stdio::inherit())
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status()
        .is_ok_and(|status| status.success())
}

struct OsRandom;

impl rand_core::RngCore for OsRandom {
    fn next_u32(&mut self) -> u32 {
        let mut buf = [0u8; 4];
        self.fill_bytes(&mut buf);
        u32::from_be_bytes(buf)
    }

    fn next_u64(&mut self) -> u64 {
        let mut buf = [0u8; 8];
        self.fill_bytes(&mut buf);
        u64::from_be_bytes(buf)
    }

    fn fill_bytes(&mut self, dest: &mut [u8]) {
        getrandom(dest).expect("getrandom failed");
    }

    fn try_fill_bytes(&mut self, dest: &mut [u8]) -> Result<(), rand_core::Error> {
        getrandom(dest).map_err(rand_core::Error::new)
    }
}

impl rand_core::CryptoRng for OsRandom {}

/// Must match Phase 838a exactly. Do not replace with `keygen_from_seed()`:
/// the committed public key was generated using this deterministic RNG wrapper.
struct SeedRng {
    seed: [u8; 32],
    counter: u64,
    buffer: [u8; 48],
    pos: usize,
}

impl SeedRng {
    fn new(seed: &[u8; 32]) -> Self {
        let mut rng = SeedRng {
            seed: *seed,
            counter: 0,
            buffer: [0u8; 48],
            pos: 48,
        };
        rng.refill();
        rng
    }

    fn refill(&mut self) {
        let counter_bytes = self.counter.to_be_bytes();
        self.buffer = sha2_384(&[&self.seed, &counter_bytes]);
        self.counter += 1;
        self.pos = 0;
    }
}

impl rand_core::RngCore for SeedRng {
    fn next_u32(&mut self) -> u32 {
        let mut buf = [0u8; 4];
        self.fill_bytes(&mut buf);
        u32::from_be_bytes(buf)
    }

    fn next_u64(&mut self) -> u64 {
        let mut buf = [0u8; 8];
        self.fill_bytes(&mut buf);
        u64::from_be_bytes(buf)
    }

    fn fill_bytes(&mut self, dest: &mut [u8]) {
        let mut written = 0;
        while written < dest.len() {
            if self.pos >= self.buffer.len() {
                self.refill();
            }
            let available = self.buffer.len() - self.pos;
            let needed = dest.len() - written;
            let n = available.min(needed);
            dest[written..written + n].copy_from_slice(&self.buffer[self.pos..self.pos + n]);
            self.pos += n;
            written += n;
        }
    }

    fn try_fill_bytes(&mut self, dest: &mut [u8]) -> Result<(), rand_core::Error> {
        self.fill_bytes(dest);
        Ok(())
    }
}

impl rand_core::CryptoRng for SeedRng {}

fn sha2_384(parts: &[&[u8]]) -> [u8; 48] {
    const H0: [u64; 8] = [
        0xcbbb9d5dc1059ed8,
        0x629a292a367cd507,
        0x9159015a3070dd17,
        0x152fecd8f70e5939,
        0x67332667ffc00b31,
        0x8eb44a8768581511,
        0xdb0c2e0d64f98fa7,
        0x47b5481dbefa4fa4,
    ];
    const K: [u64; 80] = [
        0x428a2f98d728ae22,
        0x7137449123ef65cd,
        0xb5c0fbcfec4d3b2f,
        0xe9b5dba58189dbbc,
        0x3956c25bf348b538,
        0x59f111f1b605d019,
        0x923f82a4af194f9b,
        0xab1c5ed5da6d8118,
        0xd807aa98a3030242,
        0x12835b0145706fbe,
        0x243185be4ee4b28c,
        0x550c7dc3d5ffb4e2,
        0x72be5d74f27b896f,
        0x80deb1fe3b1696b1,
        0x9bdc06a725c71235,
        0xc19bf174cf692694,
        0xe49b69c19ef14ad2,
        0xefbe4786384f25e3,
        0x0fc19dc68b8cd5b5,
        0x240ca1cc77ac9c65,
        0x2de92c6f592b0275,
        0x4a7484aa6ea6e483,
        0x5cb0a9dcbd41fbd4,
        0x76f988da831153b5,
        0x983e5152ee66dfab,
        0xa831c66d2db43210,
        0xb00327c898fb213f,
        0xbf597fc7beef0ee4,
        0xc6e00bf33da88fc2,
        0xd5a79147930aa725,
        0x06ca6351e003826f,
        0x142929670a0e6e70,
        0x27b70a8546d22ffc,
        0x2e1b21385c26c926,
        0x4d2c6dfc5ac42aed,
        0x53380d139d95b3df,
        0x650a73548baf63de,
        0x766a0abb3c77b2a8,
        0x81c2c92e47edaee6,
        0x92722c851482353b,
        0xa2bfe8a14cf10364,
        0xa81a664bbc423001,
        0xc24b8b70d0f89791,
        0xc76c51a30654be30,
        0xd192e819d6ef5218,
        0xd69906245565a910,
        0xf40e35855771202a,
        0x106aa07032bbd1b8,
        0x19a4c116b8d2d0c8,
        0x1e376c085141ab53,
        0x2748774cdf8eeb99,
        0x34b0bcb5e19b48a8,
        0x391c0cb3c5c95a63,
        0x4ed8aa4ae3418acb,
        0x5b9cca4f7763e373,
        0x682e6ff3d6b2b8a3,
        0x748f82ee5defb2fc,
        0x78a5636f43172f60,
        0x84c87814a1f0ab72,
        0x8cc702081a6439ec,
        0x90befffa23631e28,
        0xa4506cebde82bde9,
        0xbef9a3f7b2c67915,
        0xc67178f2e372532b,
        0xca273eceea26619c,
        0xd186b8c721c0c207,
        0xeada7dd6cde0eb1e,
        0xf57d4f7fee6ed178,
        0x06f067aa72176fba,
        0x0a637dc5a2c898a6,
        0x113f9804bef90dae,
        0x1b710b35131c471b,
        0x28db77f523047d84,
        0x32caab7b40c72493,
        0x3c9ebe0a15c9bebc,
        0x431d67c49c100d4c,
        0x4cc5d4becb3e42b6,
        0x597f299cfc657e2a,
        0x5fcb6fab3ad6faec,
        0x6c44198c4a475817,
    ];
    let mut data: Vec<u8> = Vec::new();
    for part in parts {
        data.extend_from_slice(part);
    }
    let bit_len = data.len() as u128 * 8;
    data.push(0x80);
    while (data.len() % 128) != 112 {
        data.push(0x00);
    }
    data.extend_from_slice(&bit_len.to_be_bytes());

    let mut h = H0;
    for block in data.chunks(128) {
        let mut w = [0u64; 80];
        for i in 0..16 {
            let b = &block[i * 8..(i + 1) * 8];
            w[i] = u64::from_be_bytes([b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7]]);
        }
        for i in 16..80 {
            let s0 = w[i - 15].rotate_right(1) ^ w[i - 15].rotate_right(8) ^ (w[i - 15] >> 7);
            let s1 = w[i - 2].rotate_right(19) ^ w[i - 2].rotate_right(61) ^ (w[i - 2] >> 6);
            w[i] = w[i - 16]
                .wrapping_add(s0)
                .wrapping_add(w[i - 7])
                .wrapping_add(s1);
        }
        let [mut a, mut b, mut c, mut d, mut e, mut f, mut g, mut hh] = h;
        for i in 0..80 {
            let s1 = e.rotate_right(14) ^ e.rotate_right(18) ^ e.rotate_right(41);
            let ch = (e & f) ^ ((!e) & g);
            let temp1 = hh
                .wrapping_add(s1)
                .wrapping_add(ch)
                .wrapping_add(K[i])
                .wrapping_add(w[i]);
            let s0 = a.rotate_right(28) ^ a.rotate_right(34) ^ a.rotate_right(39);
            let maj = (a & b) ^ (a & c) ^ (b & c);
            let temp2 = s0.wrapping_add(maj);
            hh = g;
            g = f;
            f = e;
            e = d.wrapping_add(temp1);
            d = c;
            c = b;
            b = a;
            a = temp1.wrapping_add(temp2);
        }
        h[0] = h[0].wrapping_add(a);
        h[1] = h[1].wrapping_add(b);
        h[2] = h[2].wrapping_add(c);
        h[3] = h[3].wrapping_add(d);
        h[4] = h[4].wrapping_add(e);
        h[5] = h[5].wrapping_add(f);
        h[6] = h[6].wrapping_add(g);
        h[7] = h[7].wrapping_add(hh);
    }

    let mut out = [0u8; 48];
    for (i, word) in h[..6].iter().enumerate() {
        out[i * 8..(i + 1) * 8].copy_from_slice(&word.to_be_bytes());
    }
    out
}
