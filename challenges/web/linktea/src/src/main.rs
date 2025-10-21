use std::error::Error;
use tracing::{info, level_filters::LevelFilter};

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    tracing_subscriber::fmt()
        .with_max_level(LevelFilter::DEBUG)
        .init();

    info!("Linktea CTF challenge");

    linktea::serve(&std::env::var("FLAG").unwrap_or("NNS{wow_such_a_cool_header}".to_string()))
        .await;

    Ok(())
}
