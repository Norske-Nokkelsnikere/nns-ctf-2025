# kachow

The program is vulnerable to a race condition. 

Let's first try and just call `load_flag(buffer)` and then `print_buffer`. As expected, there is nothing printed because the buffer starts with a null-terminator, because `load_buffer` does `buffer[0]='\0'`.

However, the `print_buffer` runs on another thread with no synchronization. This means that we can start the print function on another thread and then load the flag into the buffer immediately after.

First we fill the buffer using `fill_buffer` with at least `flag_len` non-zero characters. Let's just fill it with 126 A's to be sure we do not miss any flag characters.

```
index:   0        1       ...       126      127
bytes:  'A'      'A'      ...       'A'      '\0'
```

`load_flag(buffer)` changes the buffer to:

```
index:   0        1         2         3       ... 
bytes:  '\0'    FLAG[0]   FLAG[1]   FLAG[2]   ...
```

One important thing to note is that on common libc implementations, `printf("Buffer content: %s\n", buffer)` effectively does two separate steps:

1. When it encounters `%s`, it will calculate the length of `buffer` similar to `strlen(buffer)`. This walks through the memory from `buffer[0]` until it sees a `\0`. 
2. Copies `len` bytes from `buffer` to stdout similar to `write(1, buffer, len)`.

We will name the print thread PRINT and `load_flag` LOAD. The race we want is:

1. PRINT starts the race before LOAD does `buffer[0] = '\0'`, so it sees `buffer[0]='A'` and continues running through 'A' after 'A' and computes the length `len=126`.
2. LOAD does `buffer[0] = '\0'`, but it's already too late; PRINT has already  passed index 0. LOAD then copies the flag into `buffer` starting at index 1. 
3. PRINT now performs the write using the cached `len`. It does no longer care if any character is `\0`. The first byte of the buffer is now `\0` and the bytes after contain the flag. If this happens, it will look something like `\x00NNS{...}\x00...`.

This means we have to do the following:

1. Fill buffer with `flag_len` characters.
2. Print buffer
3. Load flag
4. Repeat

> The odds of hitting the perfect race are slim — but we only need to win once. Ka-Chow!