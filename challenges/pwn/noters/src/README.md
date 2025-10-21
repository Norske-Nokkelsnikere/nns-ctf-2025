# Noters

## Features

- CRUD
- List notes
- Cross platform
- Inline note references
- 100% safe Rust = no memory errors
- Privacy thanks to separation of ownership

## Available backends

- Filesystem
- SQLite

## Usage

The security that the `--user` flag provides is nullified if the user has access to restart the program as another user (or if they have access to read the contents of the backend directly).

```sh
noters --user "$USER" sqlite --path "notes.db"
noters --user "$USER" filesystem --path "./notes"
```
