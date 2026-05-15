fn main() -> Result<(), Box<dyn std::error::Error>> {
    // SEC-007a: use protox so builds do not depend on host protoc or vendored protoc binaries.
    let descriptors = protox::compile(["proto/ilc_app.proto"], ["proto"])?;
    tonic_prost_build::configure()
        .build_server(true)
        .build_client(false) // ILC consensus only serves queries; Python engine acts as client.
        .compile_fds(descriptors)?;
    Ok(())
}
