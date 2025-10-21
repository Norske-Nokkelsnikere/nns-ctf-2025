pub mod filesystem;
pub mod sqlite;

pub use filesystem::FilesystemBackend;
pub use sqlite::SqliteBackend;

pub use crate::{BackendError, Note, NoteBackend, NoteError, PartialNote, Result};
