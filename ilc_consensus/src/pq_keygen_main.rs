/// pq_keygen_main.rs — Phase 838a post-quantum genesis keypair generator.
///
/// Generates the three key items required for a CDL-069-compliant agent genesis
/// record:
///
///   1. identity_seed   — 32 random bytes; permanent anchor for agent_id
///   2. ML-DSA-65 keypair (FIPS 204) — canonical root key; derived from a seed
///   3. SPHINCS+ keypair (SLH-DSA-SHA2-128s, FIPS 205) — recovery key; derived
///      from a seed
///
/// All three seeds are output as 24 BIP-39 mnemonic words — suitable for
/// titanium plate engraving or paper cold storage.
///
/// Additionally computes:
///   - blinding_factor  = SHA-384("ilc-recovery-blind-v1:" || identity_seed)
///   - genesis record template (four committed fields, all SHA-384 hashes)
///
/// SECURITY CONTRACT:
///   Secret key seeds are printed to stdout ONCE and never written to any file.
///   Use --pubkey-record <path> to write only the public material and genesis
///   record template to cold-storage media.
///
/// Usage:
///   pq_keygen                           Print full record to stdout
///   pq_keygen --pubkey-record <path>    Also write pubkey-only record to path
///
/// `pq_keygen_838a_binary_present`
use std::path::PathBuf;

// ---------------------------------------------------------------------------
// Crate imports
// ---------------------------------------------------------------------------

use bip39::Mnemonic;
use fips204::ml_dsa_65;
use fips204::traits::{KeyGen, SerDes as MldsaSerDes};
use fips205::slh_dsa_sha2_128s;
use fips205::traits::{KeyGen as SpxKeyGen, SerDes as SpxSerDes};
use getrandom::getrandom;

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const TOOL_VERSION: &str = "pq_keygen_838a.v0.1";
const AGENT_ID_DOMAIN: &[u8] = b"ilc-agent-id-v1:";
const BLIND_DOMAIN: &[u8] = b"ilc-recovery-blind-v1:";

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let pubkey_record_path = parse_args(&args);

    // 1. Generate identity_seed (32 random bytes)
    let mut identity_seed = [0u8; 32];
    getrandom(&mut identity_seed).expect("getrandom failed for identity_seed");

    // 2. Generate ML-DSA-65 canonical root keypair from a separate seed
    let mut mldsa_seed = [0u8; 32];
    getrandom(&mut mldsa_seed).expect("getrandom failed for mldsa_seed");
    let (mldsa_pk, _mldsa_sk) = ml_dsa_65::KG::try_keygen_with_rng(&mut SeedRng::new(&mldsa_seed))
        .expect("ML-DSA-65 keygen failed");

    // 3. Generate SPHINCS+ (SLH-DSA-SHA2-128s) recovery keypair from a separate seed
    let mut sphincs_seed = [0u8; 32];
    getrandom(&mut sphincs_seed).expect("getrandom failed for sphincs_seed");
    let (sphincs_pk, _sphincs_sk) =
        slh_dsa_sha2_128s::KG::try_keygen_with_rng(&mut SeedRng::new(&sphincs_seed))
            .expect("SPHINCS+ keygen failed");

    // 4. Derive blinding_factor from identity_seed deterministically
    let blinding_factor = sha384_hash(&[BLIND_DOMAIN, &identity_seed]);

    // 5. Compute agent_id = SHA-384("ilc-agent-id-v1:" || identity_seed)
    let agent_id_bytes = sha384_hash(&[AGENT_ID_DOMAIN, &identity_seed]);
    let agent_id = hex_encode(&agent_id_bytes);

    // 6. Compute genesis record commitment fields (all SHA-384)
    let mldsa_pk_bytes = mldsa_pk.clone().into_bytes();
    let sphincs_pk_bytes = sphincs_pk.clone().into_bytes();

    let identity_seed_commitment = hex_encode(&sha384_hash(&[&identity_seed]));

    // recovery_commitment = SHA-384(recovery_spec_bytes || blinding_factor)
    // Opening candidate recovery_spec for single_key_sphincs type:
    // recovery_spec = b"single_key_sphincs:" || sphincs_pk_bytes
    let recovery_spec: Vec<u8> = [b"single_key_sphincs:".as_ref(), &sphincs_pk_bytes].concat();
    let recovery_commitment_input: Vec<u8> =
        [recovery_spec.as_slice(), blinding_factor.as_slice()].concat();
    let recovery_commitment = hex_encode(&sha384_hash(&[&recovery_commitment_input]));

    // 7. Convert seeds to BIP-39 mnemonics (24 words each)
    let identity_seed_words = to_mnemonic(&identity_seed);
    let mldsa_seed_words = to_mnemonic(&mldsa_seed);
    let sphincs_seed_words = to_mnemonic(&sphincs_seed);

    // 8. Encode public keys as hex
    let mldsa_pk_hex = hex_encode(&mldsa_pk_bytes);
    let sphincs_pk_hex = hex_encode(&sphincs_pk_bytes);

    // 9. Print full record to stdout
    print_full_record(
        &identity_seed_words,
        &mldsa_seed_words,
        &sphincs_seed_words,
        &mldsa_pk_hex,
        &sphincs_pk_hex,
        &agent_id,
        &identity_seed_commitment,
        &recovery_commitment,
    );

    // 10. Optionally write pubkey-only record to cold-storage path
    if let Some(path) = pubkey_record_path {
        write_pubkey_record(
            &path,
            &mldsa_pk_hex,
            &sphincs_pk_hex,
            &agent_id,
            &identity_seed_commitment,
            &recovery_commitment,
        );
        eprintln!();
        eprintln!("  Pubkey record written to: {}", path.display());
        eprintln!("  (No secret seed material in this file.)");
    }
}

// ---------------------------------------------------------------------------
// Output
// ---------------------------------------------------------------------------

fn print_full_record(
    identity_seed_words: &str,
    mldsa_seed_words: &str,
    sphincs_seed_words: &str,
    mldsa_pk_hex: &str,
    sphincs_pk_hex: &str,
    agent_id: &str,
    identity_seed_commitment: &str,
    recovery_commitment: &str,
) {
    let sep = "=".repeat(72);
    println!("{sep}");
    println!("  GENESIS AGENT 1 PQ KEYGEN RECORD");
    println!("  tool:    {TOOL_VERSION}");
    println!("{sep}");
    println!();
    println!("  PUBLIC MATERIAL (safe to write to USB, repo, anywhere)");
    println!("  --------------------------------------------------------");
    println!("  agent_id:                    {agent_id}");
    println!("  mldsa_pk (hex):              {mldsa_pk_hex}");
    println!("  sphincs_pk (hex):            {sphincs_pk_hex}");
    println!("  identity_seed_commitment:    {identity_seed_commitment}");
    println!("  recovery_commitment:         {recovery_commitment}");
    println!();
    println!("  SECRET MATERIAL — WRITE DOWN EACH SECTION, THEN CLOSE THIS TERMINAL");
    println!("  ---------------------------------------------------------------------");
    println!();
    println!("  [PLATE 1] identity_seed — 24 words");
    println!("  LOW SENSITIVITY: derives agent_id and blinding_factor only.");
    println!("  Store separately from Plates 2 and 3.");
    println!();
    println!("  {identity_seed_words}");
    println!();
    println!("  [PLATE 2] ML-DSA-65 canonical root seed — 24 words");
    println!("  HIGH SENSITIVITY: re-derives your canonical signing key.");
    println!("  Keep with encrypted USB for operations; also engrave plate.");
    println!();
    println!("  {mldsa_seed_words}");
    println!();
    println!("  [PLATE 3] SPHINCS+ recovery seed — 24 words");
    println!("  CRITICAL: re-derives your recovery key.");
    println!("  Split across 3 separate physical locations (2-of-3 Shamir).");
    println!("  See Phase 838 operational guide for Shamir split procedure.");
    println!();
    println!("  {sphincs_seed_words}");
    println!();
    println!("  VERIFICATION");
    println!("  ------------");
    println!("  Re-derive agent_id from Plate 1 seed at any time to verify.");
    println!("  blinding_factor is derived deterministically from identity_seed.");
    println!("  You do NOT need to record the blinding_factor separately.");
    println!();
    println!("{sep}");
}

fn write_pubkey_record(
    path: &PathBuf,
    mldsa_pk_hex: &str,
    sphincs_pk_hex: &str,
    agent_id: &str,
    identity_seed_commitment: &str,
    recovery_commitment: &str,
) {
    if let Some(parent) = path.parent() {
        if !parent.as_os_str().is_empty() {
            std::fs::create_dir_all(parent).expect("cannot create output directory");
        }
    }

    let content = format!(
        "GENESIS AGENT 1 PUBKEY VERIFICATION RECORD\n\
         tool:                     {TOOL_VERSION}\n\
         \n\
         agent_id:                 {agent_id}\n\
         mldsa_pk_hex:             {mldsa_pk_hex}\n\
         sphincs_pk_hex:           {sphincs_pk_hex}\n\
         identity_seed_commitment: {identity_seed_commitment}\n\
         recovery_commitment:      {recovery_commitment}\n\
         \n\
         NOTE: No secret seed material is stored in this file.\n\
         Verify agent_id by re-deriving: SHA-384(\"ilc-agent-id-v1:\" || identity_seed)\n\
         \n\
         genesis_agent1_pubkey_record_838a\n\
         pq_keygen_838a_binary_present\n"
    );

    std::fs::write(path, content).expect("cannot write pubkey record file");
}

// ---------------------------------------------------------------------------
// Cryptographic utilities
// ---------------------------------------------------------------------------

/// SHA-384 over concatenated slices.
fn sha384_hash(parts: &[&[u8]]) -> [u8; 48] {
    sha2_384(parts)
}

fn sha2_384(parts: &[&[u8]]) -> [u8; 48] {
    // SHA-384 constants and compression function (pure Rust, no external dep).
    // Initial hash values (fractional parts of sqrt of 9th–14th primes):
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
    // Round constants (same as SHA-512)
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

    // Pre-processing: padding
    let bit_len = data.len() as u128 * 8;
    data.push(0x80);
    while (data.len() % 128) != 112 {
        data.push(0x00);
    }
    data.extend_from_slice(&bit_len.to_be_bytes());

    // Process blocks
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

    // SHA-384 truncates to first 6 words (48 bytes)
    let mut out = [0u8; 48];
    for (i, word) in h[..6].iter().enumerate() {
        out[i * 8..(i + 1) * 8].copy_from_slice(&word.to_be_bytes());
    }
    out
}

fn hex_encode(bytes: &[u8]) -> String {
    bytes.iter().map(|b| format!("{:02x}", b)).collect()
}

fn to_mnemonic(seed: &[u8; 32]) -> String {
    Mnemonic::from_entropy(seed)
        .expect("BIP-39 mnemonic generation failed")
        .to_string()
}

// ---------------------------------------------------------------------------
// Deterministic RNG seeded from a 32-byte seed (for key derivation)
// ---------------------------------------------------------------------------

/// A simple deterministic RNG seeded from 32 bytes, using a SHA-384-based
/// counter construction. Used to derive ML-DSA and SPHINCS+ keypairs from
/// a recorded seed, so the seed alone is sufficient to reconstruct the keypair.
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
            pos: 48, // exhausted — will refill on first call
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

// ---------------------------------------------------------------------------
// Argument parsing
// ---------------------------------------------------------------------------

fn parse_args(args: &[String]) -> Option<PathBuf> {
    let mut idx = 1;
    while idx < args.len() {
        let arg = args[idx].as_str();
        if arg == "--pubkey-record" {
            idx += 1;
            let path = args.get(idx).expect("--pubkey-record requires a path");
            return Some(PathBuf::from(path));
        } else if arg == "--help" || arg == "-h" {
            eprintln!("Usage: pq_keygen");
            eprintln!("       pq_keygen --pubkey-record <path>");
            std::process::exit(0);
        } else {
            eprintln!("Unknown argument: {arg}");
            std::process::exit(1);
        }
    }
    None
}
