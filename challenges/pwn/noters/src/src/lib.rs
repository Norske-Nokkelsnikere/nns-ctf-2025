#![deny(clippy::cargo)]
#![deny(clippy::complexity)]
#![deny(clippy::correctness)]
#![deny(clippy::nursery)]
#![deny(clippy::perf)]
#![deny(clippy::style)]
#![deny(clippy::suspicious)]
#![deny(clippy::pedantic)]

use std::io;
use tabled::Tabled;
use thiserror::Error;

pub mod app;
pub mod backends;
pub mod setup;
pub mod ui;

// More convenient Result type
pub type Result<T> = std::result::Result<T, NoteError>;

#[derive(Tabled, Debug)]
pub struct Note {
    pub id: u16,
    pub owner: String,
    pub name: String,
    pub content: String,
}

// Partial note data. Displayed in lists and for shallow reads
#[derive(Tabled)]
pub struct PartialNote {
    pub id: u16,
    pub owner: String,
    pub name: String,
}

/// Trait to be implemented by all backends that manage storing and retrieving notes
pub trait NoteBackend {
    /// Stores a new note in the backend and returns the note ID
    ///
    /// # Errors
    ///
    /// Returns an error if the note could not be inserted
    fn create(&self, note: Note) -> Result<u16>;

    /// Fetches the full contents of a note by ID
    ///
    /// # Errors
    ///
    /// Returns an error if the note does not exist or the query fails
    fn read(&self, id: u16) -> Result<Note>;

    /// Fetches a partial view of a note (ID, name, owner) by ID
    ///
    /// # Errors
    ///
    /// Returns an error if the note does not exist or the query fails
    fn read_partial(&self, id: u16) -> Result<PartialNote>;

    /// Updates an existing note, replacing name, owner, and content
    ///
    /// # Errors
    ///
    /// Returns an error if the update fails or the note is not found
    fn update(&self, note: Note) -> Result<()>;

    /// Deletes a note by ID from the backend
    ///
    /// # Errors
    ///
    /// Returns an error if the note is not found or the deletion fails
    fn delete(&self, id: u16) -> Result<()>;

    /// Returns a list of all notes in the backend with partial details (ID, name, owner)
    ///
    /// # Errors
    ///
    /// Returns an error if the query fails
    fn list(&self) -> Result<Vec<PartialNote>>;
}

// Enum for all possible validation or repository-related errors
#[derive(Debug, Error)]
pub enum NoteError {
    #[error(transparent)]
    Validation(#[from] NoteValidationError),

    #[error(transparent)]
    Backend(#[from] BackendError),

    #[error(transparent)]
    Menu(#[from] MenuError),
}

// Enum for all possible menu input errors
#[derive(Debug, Error)]
pub enum MenuError {
    #[error("Failed to read from stdin: {0}")]
    StdinReadError(io::Error),

    #[error("Couldn't convert '{0}' to a number. Please enter a number 1-6")]
    ParseError(String),

    #[error("Couldn't convert '{0}' to a MenuOption. Please enter a number 1-6")]
    InvalidOption(u8),

    #[error("Failed writing to stdout")]
    StdoutWriteError(io::Error),
}

// Enum for all possible data and input validation errors
#[derive(Debug, Error)]
pub enum NoteValidationError {
    #[error("Name is empty")]
    NameEmpty,

    #[error("Content is empty")]
    ContentEmpty,

    #[error("Name is too large. Max: {max}, Got: {got}")]
    NameTooLarge { max: u8, got: usize },

    #[error("Content is too large. Max: {max}, Got: {got}")]
    ContentTooLarge { max: u16, got: usize },

    #[error("You've hit the limit for how many notes you can have. Max: {max}")]
    NoteCountLimit { max: u16 },

    #[error("Sorry! You're not the owner the note with ID: {0}")]
    PermissionDenied(u16),

    #[error("Note not found with ID: {0}")]
    NoteNotFound(u16),

    #[error("Note is referenced by: {0:?}")]
    NoteIsReferenced(Vec<u16>),

    #[error("Reference not found with ID: {0}")]
    ReferenceNotFound(u16),
}

// Enum for all possible repository/backend errors
#[derive(Debug, Error)]
pub enum BackendError {
    #[error("Database file not found")]
    DatabaseCreationError,

    #[error("Failed creating `notes` table in database")]
    TableCreationError,

    #[error("Failed creating directory for notes")]
    DirectoryCreationError(io::Error),

    #[error("Failed creating file for note data")]
    FileCreationError(io::Error),

    #[error("Failed writing note data to file")]
    FileWriteError(io::Error),

    #[error("Failed reading note data from file")]
    FileReadError(io::Error),

    #[error("Failed reading directory contents")]
    DirectoryReadError(io::Error),

    #[error("Note is improperly formatted. Failed reading all fields")]
    NoteCorrupted,

    #[error("Note already exists")]
    Duplicate,

    #[error("Database is locked or busy")]
    DatabaseBusy,

    #[error("Database corruption or file I/O error")]
    DatabaseCorruptOrIo,

    #[error("SQL logic error or misuse of SQLite")]
    SqlLogicError,

    #[error("Backend connection timed out")]
    Timeout,

    #[error("Database file is not a valid SQLite databasee")]
    NotADatabase,

    #[error("Database schema has changed unexpectedly")]
    SchemaChanged,

    #[error("No notes with ID: {0}")]
    NoteNotFound(u16),

    #[error("No notes found")]
    NoNotesFound,

    #[error("Insufficient permissions")]
    PermissionDenied,

    #[error(transparent)]
    Other(#[from] anyhow::Error), // Used as fallback
}
