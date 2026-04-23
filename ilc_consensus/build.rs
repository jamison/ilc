fn main() -> Result<(), Box<dyn std::error::Error>> {
    // SEC-007a: vendor protoc so builds do not depend on a host-installed binary.
    std::env::set_var("PROTOC", protoc_bin_vendored::protoc_bin_path()?);
    tonic_build::configure()
        .build_server(true)
        .build_client(false) // ILC consensus only serves queries; Python engine acts as client.
        .compile(&["proto/ilc_app.proto"], &["proto"])?;
    Ok(())
}
