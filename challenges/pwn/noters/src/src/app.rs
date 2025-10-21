use crate::{Note, NoteBackend, NoteError, NoteValidationError, PartialNote, Result};
use log::debug;
use std::collections::HashSet;

pub struct NoteService {
    pub repo: Box<dyn NoteBackend>,
    pub user: String,
    pub max_name_size: u8,
    pub max_content_size: u16,
    pub max_note_count: u16,
}

impl NoteService {
    #[must_use]
    pub fn new(
        repo: Box<dyn NoteBackend>,
        user: String,
        max_name_size: u8,
        max_content_size: u16,
        max_note_count: u16,
    ) -> Self {
        Self {
            repo,
            user,
            max_name_size,
            max_content_size,
            max_note_count,
        }
    }

    /// List all notes visible to the current user.
    ///
    /// # Errors
    ///
    /// Returns an error if the underlying repository fails to retrieve the notes.
    pub fn list_notes(&self) -> Result<Vec<PartialNote>> {
        self.repo.list()
    }

    /// Create a new note with the given name and content.
    ///
    /// # Errors
    ///
    /// Returns an error if validation fails or the note could not be saved.
    ///
    /// # Panics
    ///
    /// Panics if no available note ID is found, which should not happen unless there's memory corruption or a logic error.    // Create a new note after validation and reference checks
    pub fn create_note(&self, name: String, content: String) -> Result<u16> {
        Self::validate_name(&name, self.max_name_size)?;
        Self::validate_content(&content, self.max_content_size)?;

        // Make sure not too many notes are created
        let notes = self.repo.list()?;
        if notes.len() >= self.max_note_count as usize {
            return Err(NoteValidationError::NoteCountLimit {
                max: self.max_note_count,
            }
            .into());
        }

        // Find next free ID
        let used_ids: HashSet<u16> = notes.into_iter().map(|note| note.id).collect();
        let Some(available_id) = (0..self.max_note_count).find(|id| !used_ids.contains(id)) else {
            unreachable!();
        };

        // Make sure all referenced notes actually exist
        // Search for references in this format: " [[1]] " where 1 is the id of the referenced note
        for id in self.get_references(&content) {
            if !used_ids.contains(&id) {
                return Err(NoteValidationError::ReferenceNotFound(id).into());
            }

            let partial_note: PartialNote = Self::get_partial_note(self, id)?;
            if partial_note.owner != self.user {
                return Err(NoteValidationError::PermissionDenied(id).into());
            }
        }

        let note = Note {
            id: available_id,
            // The creator is the owner
            owner: self.user.clone(),
            name,
            content,
        };

        self.repo.create(note)
    }

    /// Reads a full note and expands any references in the content (e.g. `[[1]]` becomes the full text of note #1).
    ///
    /// # Errors
    ///
    /// Returns:
    /// - `NoteValidationError::PermissionDenied` if the user does not own the note or a referenced note.
    /// - `NoteValidationError::ReferenceNotFound` if a referenced note does not exist.
    /// - Other repository errors if reading from the backend fails.
    pub fn read_note(&self, id: u16) -> Result<Note> {
        let mut note = self.repo.read(id)?;

        // Only allow owner read access
        if self.user != note.owner {
            return Err(NoteValidationError::PermissionDenied(id).into());
        }

        // Mapping references to note contents: [[1]] -> "Some content"
        let placeholders = self
            .get_references(&note.content)
            .into_iter()
            .map(|rid| match self.repo.read(rid) {
                Ok(ref_note) => {
                    let placeholder = format!("[[{rid}]]");
                    let expansion = format!(
                        ">>> #{} {}\n>\n> {}",
                        ref_note.id,
                        ref_note.name,
                        ref_note.content.replace('\n', "\n> ")
                    );
                    Ok((placeholder, expansion))
                }
                Err(_) => Err(NoteValidationError::ReferenceNotFound(rid).into()),
            })
            .collect::<Result<Vec<(String, String)>>>()?;

        // Expanding references: [[1]] -> Note #1's content
        let expanded = placeholders
            .into_iter()
            .fold(note.content, |txt, (ph, exp)| txt.replace(&ph, &exp));

        note.content = expanded;
        Ok(note)
    }

    /// Updates an existing note, replacing its name and content.
    ///
    /// # Errors
    ///
    /// Returns:
    /// - `NoteValidationError::NameEmpty` or `NameTooLarge` if the new name is invalid.
    /// - `NoteValidationError::ContentEmpty` or `ContentTooLarge` if the new content is invalid.
    /// - `NoteValidationError::ReferenceNotFound` if a referenced note ID does not exist.
    /// - `NoteValidationError::PermissionDenied` if the user is not the owner of a referenced note.
    /// - `NoteValidationError::NoteNotFound` if the note to update doesn't exist.
    /// - Other backend errors if the repository operation fails.
    pub fn update_note(&self, note: Note) -> Result<()> {
        Self::validate_name(&note.name, self.max_name_size)?;
        Self::validate_content(&note.content, self.max_content_size)?;

        let notes = self.repo.list()?;
        let used_ids: HashSet<u16> = notes.into_iter().map(|note| note.id).collect();

        // Make sure all referenced notes actually exist
        // Search for references in this format: " [[1]] " where 1 is the id of the referenced note
        for id in self.get_references(&note.content) {
            if !used_ids.contains(&id) {
                return Err(NoteValidationError::ReferenceNotFound(id).into());
            }

            // Make sure the user is allowed to read the referenced note
            let partial_note: PartialNote = Self::get_partial_note(self, id)?;
            if partial_note.owner != self.user {
                return Err(NoteValidationError::PermissionDenied(id).into());
            }
        }

        // Make sure the note we are updating actually exist
        if used_ids.contains(&note.id) {
            self.repo.update(note)
        } else {
            Err(NoteValidationError::NoteNotFound(note.id).into())
        }
    }

    /// Deletes a note by ID, but only if no other notes reference it.
    ///
    /// # Errors
    ///
    /// Returns:
    /// - `NoteValidationError::NoteIsReferenced` if other notes reference the note being deleted.
    /// - Backend errors if the note cannot be read or deleted.
    pub fn delete_note(&self, id: u16) -> Result<()> {
        // Check if any other note references this note (expensive)
        // and do not stop at the first backlink, find all of them
        let mut backlinks: Vec<u16> = Vec::new();
        for partial_note in self.list_notes()? {
            // Do not prevent deletion if note refers to itself
            if partial_note.id == id {
                // While we're here: Check if user is the owner of the note
                // Make sure they can't delete a note they don't own
                if partial_note.owner != self.user {
                    return Err(NoteValidationError::PermissionDenied(partial_note.id).into());
                }
                continue;
            }

            // Read content and find all references
            // Save ID to Vec if it contains a backlink
            // to the note we're trying to delete
            let content = self.repo.read(id)?.content;
            let references = self.get_references(&content);
            if references.contains(&id) {
                backlinks.push(partial_note.id);
            }
        }

        let num_backlinks = backlinks.len();
        match num_backlinks {
            0 => self.repo.delete(id),
            _ => Err(NoteError::Validation(
                NoteValidationError::NoteIsReferenced(backlinks),
            )),
        }
    }

    /// Creates a special "flag" note owned by a specialist group of elite hackers
    ///
    /// # Errors
    ///
    /// Returns:
    /// - `NoteValidationError::NoteCountLimit` if the number of notes has exceeded th pre-configured limit.
    /// - Other repository errors if note creation fails.
    ///
    /// # Panics
    ///
    /// Panics if no available note ID is found, which should be logically impossible unless data corruption occurred.
    pub fn create_flag_note(&self) -> Result<u16> {
        use std::env;

        let flag = env::var("FLAG").unwrap_or_else(|_| {
            debug!("The `FLAG` environment variable isn't set. Using placeholder value.");
            "NNS{placeholder}".to_string()
        });

        // Make sure not too many notes are created
        let notes = self.repo.list()?;
        if notes.len() >= self.max_note_count as usize {
            return Err(NoteValidationError::NoteCountLimit {
                max: self.max_note_count,
            }
            .into());
        }

        // Find next free ID
        let used_ids: HashSet<u16> = notes.into_iter().map(|note| note.id).collect();
        let available_id = (0..self.max_note_count)
            .find(|id| !used_ids.contains(id))
            .expect("Available ID not found despite more space for more notes");

        // The creator is the owner
        let note = Note {
            id: available_id,
            owner: "Norske Nøkkelsnikere".to_string(),
            name: "flag".to_string(),
            content: flag,
        };

        self.repo.create(note)
    }

    // --- small helpers ---

    /// Validates a note name against length and emptiness.
    ///
    /// # Errors
    ///
    /// Returns:
    /// - `NoteValidationError::NameEmpty` if the name is only whitespace.
    /// - `NoteValidationError::NameTooLarge` if the name exceeds the given length.
    pub fn validate_name(name: &str, max: u8) -> Result<()> {
        if name.trim().is_empty() {
            Err(NoteValidationError::NameEmpty.into())
        } else if name.len() > max as usize {
            Err(NoteValidationError::NameTooLarge {
                max,
                got: name.len(),
            }
            .into())
        } else {
            Ok(())
        }
    }

    /// Validates a note's content against length and emptiness.
    ///
    /// # Errors
    ///
    /// Returns:
    /// - `NoteValidationError::ContentEmpty` if the content is only whitespace.
    /// - `NoteValidationError::ContentTooLarge` if the content exceeds the given length.
    pub fn validate_content(content: &str, max: u16) -> Result<()> {
        if content.trim().is_empty() {
            Err(NoteValidationError::ContentEmpty.into())
        } else if content.len() > max as usize {
            Err(NoteValidationError::ContentTooLarge {
                max,
                got: content.len(),
            }
            .into())
        } else {
            Ok(())
        }
    }

    /// Extracts referenced note IDs in the form of `[[id]]` from the given string.
    ///
    /// # Returns
    ///
    /// A vector of note IDs found inside double brackets.
    #[allow(clippy::unused_self)]
    fn get_references(&self, s: &str) -> Vec<u16> {
        s.split_whitespace()
            .filter_map(|tok| {
                if tok.starts_with("[[") && tok.ends_with("]]") {
                    tok[2..tok.len() - 2].parse().ok()
                } else {
                    None
                }
            })
            .collect()
    }

    /// Reads a note partially (e.g., ID and owner) without full content.
    ///
    /// # Errors
    ///
    /// Returns an error if the note cannot be found or read from the repository.
    fn get_partial_note(&self, id: u16) -> Result<PartialNote> {
        self.repo.read_partial(id)
    }
}
