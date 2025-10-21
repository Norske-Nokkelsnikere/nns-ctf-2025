use log::error;
use noters::{
    setup::{arguments, logging},
    ui::io,
};

fn main() {
    logging::setup_log();
    dotenv::dotenv().ok();
    let service = arguments::handle_args().unwrap_or_else(|e| {
        error!("Failed initializing backend: {e}");
        panic!()
    });

    io::run(&service)
}
