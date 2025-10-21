use colored::Colorize;
use env_logger::Builder;
use log::LevelFilter;
use std::io::Write;

/// Sets up the logging configuration for the application.
///
/// Configures the logger to use colored output based on the log level.
/// Sets default log level to `Debug` and initializes the logger with a custom format.
pub fn setup_log() {
    let default_log_level = LevelFilter::Debug;
    let mut builder = Builder::from_default_env();

    builder
        .format(|buf, record| {
            let l = record.level();
            let colored_level = match l {
                log::Level::Error => l.to_string().red().bold(),
                log::Level::Warn => l.to_string().yellow().bold(),
                log::Level::Info => l.to_string().green().bold(),
                log::Level::Debug => l.to_string().blue().bold(),
                log::Level::Trace => l.to_string().purple().bold(),
            };
            writeln!(buf, "{} {}", colored_level, record.args())
        })
        .filter(None, default_log_level)
        .parse_default_env()
        .init();
}
