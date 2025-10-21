use super::{BackendError, Note, NoteBackend, NoteError, PartialNote, Result};
use log::trace;
use std::{
    fs::{self, File},
    io::{Read, Write},
    path::PathBuf,
};

#[derive(Debug)]
pub struct FilesystemBackend {
    base_path: PathBuf,
}

impl FilesystemBackend {
    /// Creates a new `FilesystemBackend` instance with the given base directory
    ///
    /// # Errors
    ///
    /// Returns `BackendError::DirectoryCreationError` if the base directory cannot be created
    pub fn new(path: &str) -> Result<Self> {
        let base_path = PathBuf::from(path);
        fs::create_dir_all(&base_path)
            .map_err(|e| NoteError::Backend(BackendError::DirectoryCreationError(e)))?;
        trace!("Created directory for notes: {}", &base_path.display());
        Ok(Self { base_path })
    }

    /// Constructs a filesystem path for the note file based on its ID
    fn note_path(&self, id: u16) -> PathBuf {
        self.base_path.join(format!("{id:05}.note"))
    }

    /// Lists all note files in the base directory
    ///
    /// # Errors
    ///
    /// Returns `BackendError::DirectoryReadError` if the directory cannot be read or a file entry cannot be processed
    fn list_note_files(&self) -> Result<Vec<PathBuf>> {
        let entries = fs::read_dir(&self.base_path)
            .map_err(BackendError::DirectoryReadError)
            .map_err(NoteError::Backend)?;

        let mut files = Vec::new();

        for entry_result in entries {
            let entry = entry_result
                .map_err(BackendError::DirectoryReadError)
                .map_err(NoteError::Backend)?;

            let file_type = entry
                .file_type()
                .map_err(BackendError::DirectoryReadError)
                .map_err(NoteError::Backend)?;

            if file_type.is_file() {
                files.push(entry.path());
            }
        }
        trace!("Found notes: {:?}", &files);
        Ok(files)
    }
}

impl NoteBackend for FilesystemBackend {
    /// Creates a new note by writing it to the filesystem as a file
    ///
    /// # Errors
    ///
    /// Returns:
    /// - `BackendError::Duplicate` if a note with the same ID already exists
    /// - `BackendError::FileCreationError` if the file cannot be created
    /// - `BackendError::FileWriteError` if writing to the file fails
    fn create(&self, note: Note) -> Result<u16> {
        let path = self.note_path(note.id);
        if path.exists() {
            return Err(NoteError::Backend(BackendError::Duplicate));
        }

        let mut file = File::create(&path)
            .map_err(|e| NoteError::Backend(BackendError::FileCreationError(e)))?;
        trace!("Created file: {}", &path.display());
        let data = format!("{}\n{}\n{}", note.name, note.owner, note.content);
        file.write_all(data.as_bytes())
            .map_err(|e| NoteError::Backend(BackendError::FileWriteError(e)))?;
        trace!("Wrote data to file:\n{}", &data);
        Ok(note.id)
    }

    /// Reads a note file by ID and returns the full note
    ///
    /// # Errors
    ///
    /// Returns:
    /// - `BackendError::NoteNotFound` if the note file does not exist
    /// - `BackendError::FileReadError` if the file cannot be read
    /// - `BackendError::NoteCorrupted` if the file does not contain at least three lines (name, owner and 1 line of content)
    fn read(&self, id: u16) -> Result<Note> {
        let path = self.note_path(id);
        let mut file =
            File::open(&path).map_err(|_| NoteError::Backend(BackendError::NoteNotFound(id)))?;
        trace!("Opened file for note #{} for reading", &id);

        let mut contents = String::new();
        file.read_to_string(&mut contents)
            .map_err(|e| NoteError::Backend(BackendError::FileReadError(e)))?;

        let mut lines = contents.lines();
        let name = lines
            .next()
            .ok_or(NoteError::Backend(BackendError::NoteCorrupted))?;
        let owner = lines
            .next()
            .ok_or(NoteError::Backend(BackendError::NoteCorrupted))?;
        let content = lines.collect::<Vec<&str>>().join("\n");

        if content.trim().is_empty() {
            return Err(NoteError::Backend(BackendError::NoteCorrupted));
        }

        Ok(Note {
            id,
            name: name.to_string(),
            owner: owner.to_string(),
            content,
        })
    }

    /// Reads only the ID, name, and owner of a note by ID
    ///
    /// # Errors
    ///
    /// Returns:
    /// - `BackendError::NoteNotFound` if the note file does not exist
    /// - `BackendError::FileReadError` if the file cannot be read
    /// - `BackendError::NoteCorrupted` if the file does not contain at least two lines (name and owner)
    fn read_partial(&self, id: u16) -> Result<PartialNote> {
        let path = self.note_path(id);
        let mut file =
            File::open(&path).map_err(|_| NoteError::Backend(BackendError::NoteNotFound(id)))?;

        let mut contents = String::new();
        file.read_to_string(&mut contents)
            .map_err(|e| NoteError::Backend(BackendError::FileReadError(e)))?;

        let mut lines = contents.lines();
        let name = lines
            .next()
            .ok_or(NoteError::Backend(BackendError::NoteCorrupted))?;
        let owner = lines
            .next()
            .ok_or(NoteError::Backend(BackendError::NoteCorrupted))?;

        Ok(PartialNote {
            id,
            name: name.to_string(),
            owner: owner.to_string(),
        })
    }

    /// Updates an existing note file with new name, owner, and content
    ///
    /// # Errors
    ///
    /// Returns:
    /// - `BackendError::NoteNotFound` if the note file does not exist
    /// - `BackendError::FileCreationError` if the file cannot be created and opened
    /// - `BackendError::FileWriteError` if writing to the file fails
    fn update(&self, note: Note) -> Result<()> {
        let path = self.note_path(note.id);
        if !path.exists() || path.is_dir() {
            return Err(NoteError::Backend(BackendError::NoteNotFound(note.id)));
        }

        let mut file = File::create(&path)
            .map_err(|e| NoteError::Backend(BackendError::FileCreationError(e)))?;
        let data = format!("{}\n{}\n{}", note.name, note.owner, note.content);
        file.write_all(data.as_bytes())
            .map_err(|e| NoteError::Backend(BackendError::FileWriteError(e)))?;
        Ok(())
    }

    /// Deletes a note file by ID
    ///
    /// # Errors
    ///
    /// Returns:
    /// - `BackenDError::PermissionDenied` if the file can't be deleted due to missing privileges
    /// - `BackendError::NoteNotFound` if the file does not exist or the path is a directory
    /// - `BackendError::Other` as a catch-all for other unexpected errors
    fn delete(&self, id: u16) -> Result<()> {
        use std::io::ErrorKind;

        let path = self.note_path(id);
        fs::remove_file(&path)
            .map_err(|e| match e.kind() {
                ErrorKind::PermissionDenied => BackendError::PermissionDenied,
                ErrorKind::IsADirectory | ErrorKind::NotFound => BackendError::NoteNotFound(id),
                _ => BackendError::Other(anyhow::anyhow!("Filesystem error: {:?}", e)),
            })
            .map_err(NoteError::Backend)
    }

    /// Lists all notes in the filesystem by parsing their filenames and reading partial metadata
    ///
    /// # Errors
    ///
    /// Returns an error if reading the list of note files fails
    ///
    /// # Note
    ///
    /// Silently skips corrupt or unreadable notes
    fn list(&self) -> Result<Vec<PartialNote>> {
        let mut notes = Vec::new();

        for file_path in self.list_note_files()? {
            if let Some(stem) = file_path.file_stem().and_then(|s| s.to_str()) {
                if let Ok(id) = stem.parse::<u16>() {
                    if let Ok(note) = self.read_partial(id) {
                        notes.push(note);
                    }
                }
            }
        }

        notes.sort_by_key(|n| n.id);
        Ok(notes)
    }
}
