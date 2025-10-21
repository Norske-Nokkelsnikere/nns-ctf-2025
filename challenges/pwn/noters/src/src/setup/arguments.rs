use crate::app::NoteService;
use crate::backends::{FilesystemBackend, SqliteBackend};
use crate::{NoteBackend, Result};

use clap::{Parser, Subcommand};

#[derive(Parser, Debug)]
#[command(version, about, long_about)]
struct Args {
    #[arg(short, long)]
    user: String,
    #[arg(long, default_value_t = 32)]
    max_name_size: u8,
    #[arg(long, default_value_t = 1024)]
    max_content_size: u16,
    #[arg(long, default_value_t = 100)]
    max_note_count: u16,
    #[command(subcommand)]
    backend: Backend,
}

#[derive(Subcommand, Debug)]
enum Backend {
    Filesystem {
        #[arg(short, long)]
        path: String,
    },
    Sqlite {
        #[arg(short, long)]
        path: String,
    },
}

/// Parses command-line arguments and initializes a `NoteService` based on the provided arguments.
///
/// # Returns
///
/// A `NoteService` instance initialized with the parsed arguments.
///
/// # Errors
///
/// - `NoteValidationError::UsernameTooLong` if the username length exceeds 32 characters
/// - Tries creating a `NoteBackend` instance based on the specified backend type and initializes a `NoteService` with it. Any errors are forwarded
pub fn handle_args() -> Result<NoteService> {
    let args = Args::parse();

    // Allow any struct that implements NoteBackend, and store on heap because size is unknown at compile time
    let repo: Box<dyn NoteBackend> = match args.backend {
        Backend::Filesystem { path } => Box::new(FilesystemBackend::new(&path)?),
        Backend::Sqlite { path } => Box::new(SqliteBackend::new(&path)?),
    };

    Ok(NoteService::new(
        repo,
        args.user,
        args.max_name_size,
        args.max_content_size,
        args.max_note_count,
    ))
}
