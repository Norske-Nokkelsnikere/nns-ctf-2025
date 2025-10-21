use super::{MenuError, NoteError, PartialNote, Result};

use crate::ui::io::IO;
use colored::Colorize;
use log::trace;
use std::io::{self, Write};
use tabled::{settings::Style, Table};

pub struct Cli;

impl IO for Cli {
    /// Reads a single line of text, trims the trailing newline, and
    /// returns the resulting string.
    ///
    /// # Errors
    ///
    /// Returns an error if writing to stdout or reading from stdin fails.
    fn get_input(&self) -> Result<String> {
        let mut input = String::new();
        print!("> ");
        io::stdout()
            .flush()
            .map_err(|e| NoteError::Menu(MenuError::StdoutWriteError(e)))?;
        trace!("Flushed stdout");

        io::stdin()
            .read_line(&mut input)
            .map_err(|e| NoteError::Menu(MenuError::StdinReadError(e)))?;

        println!();

        input = input.trim().to_string();
        trace!("Got input: {input}");
        Ok(input)
    }

    /// Reads lines from stdin until a line exactly matching `stop_at` (trimmed) is entered,
    /// concatenates the preceding lines and returns it.
    ///
    /// # Parameters
    ///
    /// - `stop_at`: The sentinel string that terminates input collection.
    ///
    /// # Errors
    ///
    /// Returns an error if writing to stdout or reading from stdin fails.
    fn get_input_until(&self, stop_at: &str) -> Result<String> {
        // Prevent user from not being able to escape input
        // if stop_at is a whitespace character, as the input
        // has its whitespace trimmed away before matching
        assert_ne!(stop_at.trim(), "");

        let mut input = String::new();
        loop {
            print!("> ");
            io::stdout()
                .flush()
                .map_err(|e| NoteError::Menu(MenuError::StdoutWriteError(e)))?;
            trace!("Flushed stdout");

            let mut line = String::new();
            io::stdin()
                .read_line(&mut line)
                .map_err(|e| NoteError::Menu(MenuError::StdinReadError(e)))?;
            trace!("Got input: {}", line.trim_end());

            if line.trim() == stop_at {
                break;
            }
            input += &line;
        }
        println!();
        Ok(input)
    }

    /// Displays a numbered menu prompt with the given options.
    ///
    /// # Parameters
    ///
    /// - `options`: A slice of items implementing `Display`.
    fn show_menu(&self, options: &[impl std::fmt::Display]) {
        self.show_title("Choose an option");
        for o in options {
            println!("{o}");
        }
    }

    /// Renders a table of partial notes in `psql` style to stdout.
    ///
    /// # Parameters
    ///
    /// - `partial_notes`: A vector of `PartialNote` items to tabulate.
    fn show_notes_list(&self, partial_notes: Vec<PartialNote>) {
        let mut table = Table::new(partial_notes);
        table.with(Style::psql());
        println!("{table}\n");
    }

    /// Prints a bolded title followed by a blank line.
    ///
    /// # Parameters
    ///
    /// - `title`: The text to render as the title.
    fn show_title(&self, title: &str) {
        println!("{}\n", title.to_string().bold());
    }

    /// Prints plain text to stdout.
    ///
    /// # Parameters
    ///
    /// - `msg`: The message to display.
    fn show_text(&self, msg: &str) {
        println!("{msg}");
    }
}
