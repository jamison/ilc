fn main() -> Result<(), Box<dyn std::error::Error>> {
    tonic_build::configure()
        .build_server(true)
        .build_client(false) // ILC consensus only serves queries; Python engine acts as client.
        .compile(&["proto/ilc_app.proto"], &["proto"])?;
    Ok(())
}
