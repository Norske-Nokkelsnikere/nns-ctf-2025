#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>

void ignore_buffering() {
	setbuf(stdout, NULL);
	setbuf(stdin, NULL);
}

void fill_buffer(char *addr) {
	write(1, "Content: ", 9);
	fgets(addr, 128, stdin); // Null-terminated :)
}

void load_flag(char *addr) {
	char *flagptr = getenv("FLAG");

	if (!flagptr) { // Remember to create a FLAG env var when testing locally
		printf("Failed to find FLAG environment variable.\n");
		return;
	}

	addr[0] = '\0'; // now getting the flag is impossible
	strncpy(addr+1, flagptr, 127);
	printf("Successfully placed flag in buffer.\n");
}

void *print_buffer(void *addr) {
	printf("Buffer content: %s\n", (char *)addr);
	return 0;
}


void main_menu() {
	printf("Welcome to my flag printer. I'm still working on it though, so it doesn't actually print flags yet.\n");
	printf("1. Fill buffer\n");
	printf("2. Load flag into buffer\n");
	printf("3. Print buffer contents\n");
	printf("4. Exit\n");
	printf("> ");
}

int main() {
	char buffer[128];
	char choice = ' ';
	pthread_t thread;

	ignore_buffering();
	do {
		main_menu();
		scanf("%c", &choice);
		getchar();

		switch (choice) {
			case '1':
				fill_buffer(buffer);
				break;
			case '2':
				load_flag(buffer);
				break;
			case '3':
				pthread_create(&thread, NULL, print_buffer, buffer); // Creating new thread for extra security
				break;
		}
	} while (choice != '4');

	return 0;
}
