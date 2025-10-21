use super::{MenuError, NoteError, PartialNote, Result};
use crate::app::NoteService;
use crate::ui::cli;

use colored::Colorize;
use log::{error, info, trace, warn};
use std::fmt;

/// Abstraction for input/output
pub trait IO {
    /// Read a single line of input from stdin, trim trailing newline, and return it
    ///
    /// # Errors
    ///
    /// Returns an Err variant if writing the prompt or reading from stdin fails
    fn get_input(&self) -> Result<String>;

    /// Read lines from stdin until a line exactly matching `stop_at` (after trimming)
    /// is entered, concatenate all preceding lines, trim trailing whitespace, and return
    /// resulting text.
    ///
    /// # Parameters
    ///
    /// - `stop_at`: The sentinel string that stops input collection when entered alone. Can't be whitespace
    ///
    /// # Errors
    ///
    /// Returns an Err variant if writing the prompt or reading from stdin fails
    fn get_input_until(&self, stop_at: &str) -> Result<String>;

    /// Display a selection menu to the user
    ///
    /// # Parameters
    ///
    /// - `options`: A slice of displayable items representing the menu entries
    fn show_menu(&self, options: &[impl std::fmt::Display]);

    /// Render a terrific title
    ///
    /// # Parameters
    ///
    /// - `title`: The text to display as the menu or section title
    fn show_title(&self, title: &str);

    /// Render a beautiful list of notes
    ///
    /// # Parameters
    ///
    /// - `table`: A vector of `PartialNote` structs to display in rows
    fn show_notes_list(&self, table: Vec<PartialNote>);

    /// Show arbitrary text
    ///
    /// # Parameters
    ///
    /// - `msg`: The message string to output
    fn show_text(&self, msg: &str);
}

/// CRUD and listing actions available in the menu
#[derive(Debug, Clone, Copy)]
pub enum MenuOption {
    Create = 1,
    Read = 2,
    Update = 3,
    Delete = 4,
    List = 5,
    AddFlag = 6,
}

/// All menu options in display order
pub const ALL_MENU_OPTIONS: [MenuOption; 6] = [
    MenuOption::Create,
    MenuOption::Read,
    MenuOption::Update,
    MenuOption::Delete,
    MenuOption::List,
    MenuOption::AddFlag,
];

/// Convert a numeric choice into a `MenuOption`
///
/// # Errors
///
/// Returns `Err(())` if the value does not map to a valid variant
impl TryFrom<u8> for MenuOption {
    type Error = ();

    fn try_from(n: u8) -> std::result::Result<Self, Self::Error> {
        match n {
            1 => Ok(Self::Create),
            2 => Ok(Self::Read),
            3 => Ok(Self::Update),
            4 => Ok(Self::Delete),
            5 => Ok(Self::List),
            6 => Ok(Self::AddFlag),
            _ => Err(()),
        }
    }
}

/// Show the option number and label, e.g. `(1) Create note`
impl fmt::Display for MenuOption {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let label = match self {
            Self::Create => "Create note",
            Self::Read => "Read note",
            Self::Update => "Update note",
            Self::Delete => "Delete note",
            Self::List => "List notes",
            Self::AddFlag => "Add note with flag",
        };
        write!(f, "({}) {}", *self as u8, label)
    }
}

/// Dispatch chosen `MenuOption` to its handler
///
/// # Parameters
///
/// - `io`: I/O implementation
/// - `service`: Note service backend
/// - `option`: Selected menu option
fn handle_menu_option(io: &impl IO, service: &NoteService, option: MenuOption) {
    match option {
        MenuOption::Create => handle_create(io, service),
        MenuOption::Read => handle_read(io, service),
        MenuOption::Update => handle_update(io, service),
        MenuOption::Delete => handle_delete(io, service),
        MenuOption::List => handle_list(io, service),
        MenuOption::AddFlag => handle_add_flag(service),
    }
}

/// Initialize logging, parse args, and enters the main menu loop
///
/// # Panics
///
/// Unreachable branch when an unexpected `NoteError` occurs
///
/// # Errors
///
/// Logs `MenuError` variants but never returns
pub fn run(service: &NoteService) {
    let io = cli::Cli;
    println!();

    loop {
        io.show_menu(&ALL_MENU_OPTIONS);
        match get_menu_input(&io) {
            Ok(opt) => handle_menu_option(&io, service, opt),
            Err(NoteError::Menu(e)) => error!("{e}\n"),
            Err(_) => unreachable!(),
        }
    }
}

/// Try parsing input as `MenuOption` or return an error
///
/// # Parameters
///
/// - `io`: I/O implementation
///
/// # Returns
///
/// The chosen `MenuOption` on success
///
/// # Errors
///
/// Returns `NoteError::Menu(MenuError::ParseError)` if input is not an integer
/// Returns `NoteError::Menu(MenuError::InvalidOption)` if integer is out of range
fn get_menu_input(io: &impl IO) -> Result<MenuOption> {
    println!();
    let raw = io.get_input()?;

    raw.parse::<u8>()
        .map_err(|_| NoteError::Menu(MenuError::ParseError(raw.clone())))
        .and_then(|n| {
            MenuOption::try_from(n).map_err(|()| NoteError::Menu(MenuError::InvalidOption(n)))
        })
}

/// Prompt for note creation and invoke service
///
/// # Parameters
///
/// - `io`: I/O implementation
/// - `service`: Note service backend
///
/// # Panics
///
/// If reading name or content fails unexpectedly
fn handle_create(io: &impl IO, service: &NoteService) {
    io.show_title("Create note");

    let name: String = loop {
        io.show_text("Name:");
        let input = io.get_input().expect("Failed getting note name");
        match NoteService::validate_name(&input, service.max_name_size) {
            Ok(()) => {
                trace!("Got valid name: {input}\n");
                break input;
            }
            Err(e) => error!("{e}\n"),
        }
    };

    let content: String = loop {
        // Stop when getting a "." alone on a line
        io.show_text("Content (end with '.' on last line):");
        let input = io
            .get_input_until(".")
            .expect("Failed getting note content");
        match NoteService::validate_content(&input, service.max_content_size) {
            Ok(()) => {
                trace!("Got valid content: {input}\n");
                break input;
            }
            Err(e) => error!("Got invalid content: {e}\n"),
        }
    };

    match service.create_note(name, content) {
        Ok(id) => info!("Note saved with ID: {id}\n"),
        Err(e) => error!("{e}\n"),
    }
}

/// Prompt for a note ID, fetch and display the note
///
/// # Parameters
///
/// - `io`: I/O implementation
/// - `service`: Note service backend
///
/// # Panics
///
/// If reading the ID fails unexpectedly
fn handle_read(io: &impl IO, service: &NoteService) {
    io.show_title("Read note");

    let id: u16 = loop {
        io.show_text("ID:");
        let input = io.get_input().expect("Failed getting note ID");
        match input.parse::<u16>() {
            Ok(id) => {
                trace!("Got valid ID: {id}\n");
                break id;
            }
            Err(e) => error!("Got invalid ID: {e}\n"),
        }
    };

    match service.read_note(id) {
        Ok(note) => {
            let title_text = format!("#{}: {}", note.id, note.name).bold();

            io.show_text(&"-".repeat(20));
            io.show_text(&title_text);
            io.show_text("");
            io.show_text(&note.content);
            io.show_text(&"-".repeat(20));
            io.show_text("");
        }
        Err(e) => error!("{e}\n"),
    }
}

/// Prompt for note ID, updated fields, and apply update
///
/// # Parameters
///
/// - `io`: I/O implementation
/// - `service`: Note service backend
///
/// # Panics
///
/// If reading name or content fails unexpectedly
fn handle_update(io: &impl IO, service: &NoteService) {
    io.show_title("Update note");

    let mut note = loop {
        io.show_text("ID:");
        let input = io.get_input().expect("Failed getting note ID");
        let id = match input.parse::<u16>() {
            Ok(id) => id,
            Err(e) => {
                error!("{e}");
                continue;
            }
        };
        match service.read_note(id) {
            Ok(note) => break note,
            Err(e) => error!("{e}\n"),
        }
    };

    let name: String = loop {
        io.show_text("Name:");
        let input = io.get_input().expect("Failed getting note name");
        match NoteService::validate_name(&input, service.max_name_size) {
            Ok(()) => {
                trace!("Got valid name: {input}\n");
                break input;
            }
            Err(e) => error!("Got invalid name: {e}\n"),
        }
    };

    let content: String = loop {
        // Stop when getting a "." alone on a line
        io.show_text("Content (end with '.' on last line):");
        let input = io
            .get_input_until(".")
            .expect("Failed getting note content");
        match NoteService::validate_content(&input, service.max_content_size) {
            Ok(()) => {
                trace!("Got valid content: {input}\n");
                break input;
            }
            Err(e) => error!("Got invalid content: {e}\n"),
        }
    };

    note.name = name;
    note.content = content;

    match service.update_note(note) {
        Ok(()) => info!("Successfully updated note\n"),
        Err(e) => error!("{e}\n"),
    }
}

/// Prompt for note ID, confirm deletion, and delete
///
/// # Parameters
///
/// - `io`: I/O implementation
/// - `service`: Note service backend
///
/// # Panics
///
/// If reading confirmation fails unexpectedly
fn handle_delete(io: &impl IO, service: &NoteService) {
    io.show_title("Delete note");

    let id: u16 = loop {
        io.show_text("ID:");
        let input = io.get_input().expect("Failed getting note ID");
        match input.parse::<u16>() {
            Ok(id) => break id,
            Err(e) => error!("{e}\n"),
        }
    };

    loop {
        io.show_text("Are you absolutely sure? (y/n):");
        let input = io.get_input().expect("Failed getting delete confirmation");
        match input.to_lowercase().as_str() {
            "y" | "ye" | "yes" | "ya" | "yuh" | "yarr" | "fuck yeah" => break,
            "n" | "nu uh" | "no" | "nah" | "hell naw" | "get yo bitchass outta here" => {
                info!("Exiting. Not deleting note with ID: {id}\n");
                return;
            }
            _ => warn!("Invalid input. Please enter 'y' or 'n'\n"),
        }
    }

    match service.delete_note(id) {
        Ok(()) => info!("Successfully deleted note with ID: {id}\n"),
        Err(e) => error!("{e}\n"),
    }
}

/// Fetch all notes and display in a table
///
/// # Parameters
///
/// - `io`: Console I/O implementation
/// - `service`: Note service backend
fn handle_list(io: &impl IO, service: &NoteService) {
    let partial_notes: Vec<PartialNote> = match service.list_notes() {
        Ok(n) => n,
        Err(e) => {
            error!("{e}\n");
            return;
        }
    };
    io.show_notes_list(partial_notes);
}

/// Create a note containing the flag via service
///
/// # Parameters
///
/// - `service`: Note service backend
fn handle_add_flag(service: &NoteService) {
    match service.create_flag_note() {
        Ok(id) => info!("Successfully added note containing flag, with ID: {id}\n"),
        Err(e) => error!("Failed adding note containing flag: {e}\n"),
    }
}
