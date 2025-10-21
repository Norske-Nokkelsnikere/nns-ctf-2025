#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <windows.h>
#include <wininet.h>

#define COLOR_GREEN 10
#define COLOR_WHITE 15

const char *banner = 
"██╗    ██╗ █████╗ ███╗   ██╗███╗   ██╗ █████╗ ██████╗ ███████╗ █████╗ ██╗     ███████╗██╗      █████╗  ██████╗ \n"
"██║    ██║██╔══██╗████╗  ██║████╗  ██║██╔══██╗██╔══██╗██╔════╝██╔══██╗██║     ██╔════╝██║     ██╔══██╗██╔════╝ \n"
"██║ █╗ ██║███████║██╔██╗ ██║██╔██╗ ██║███████║██████╔╝█████╗  ███████║██║     █████╗  ██║     ███████║██║  ███╗\n"
"██║███╗██║██╔══██║██║╚██╗██║██║╚██╗██║██╔══██║██╔══██╗██╔══╝  ██╔══██║██║     ██╔══╝  ██║     ██╔══██║██║   ██║\n"
"╚███╔███╔╝██║  ██║██║ ╚████║██║ ╚████║██║  ██║██║  ██║███████╗██║  ██║███████╗██║     ███████╗██║  ██║╚██████╔╝\n"
" ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝ ╚═════╝ \n";

void rc4_init(unsigned char* S, const unsigned char* key, int key_len) {
    int i, j = 0;
    unsigned char T[256];
    unsigned char temp;

    for (i = 0; i < 256; i++) {
        S[i] = i;
        T[i] = key[i % key_len];
    }

    for (i = 0; i < 256; i++) {
        j = (j + S[i] + T[i]) % 256;
        temp = S[i];
        S[i] = S[j];
        S[j] = temp;
    }
}

void rc4_crypt(unsigned char* S, const unsigned char* input, unsigned char* output, int data_len) {
    int i = 0, j = 0, k;
    unsigned char temp;

    for (k = 0; k < data_len; k++) {
        i = (i + 1) % 256;
        j = (j + S[i]) % 256;
        temp = S[i];
        S[i] = S[j];
        S[j] = temp;
        output[k] = input[k] ^ S[(S[i] + S[j]) % 256];
    }
}

int hex_to_bytes(const char* hex_string, unsigned char* bytes) {
    int len = strlen(hex_string);
    if (len % 2 != 0) return -1;
    
    int byte_len = len / 2;
    for (int i = 0; i < byte_len; i++) {
        sscanf(hex_string + 2*i, "%2hhx", &bytes[i]);
    }
    return byte_len;
}

void expand_hex_string(const char* input, char* output) {
    int input_len = strlen(input);
    int output_pos = 0;
    
    for (int i = 0; i < input_len; i += 2) {
        output[output_pos++] = input[i];
        if (i + 1 < input_len) {
            output[output_pos++] = input[i + 1];
        }
        output[output_pos++] = '0';
        output[output_pos++] = '0';
    }
    output[output_pos] = '\0';
}

int main() {

    SetConsoleOutputCP(CP_UTF8);

    HANDLE hConsole = GetStdHandle(STD_OUTPUT_HANDLE);

    SetConsoleTextAttribute(hConsole, COLOR_GREEN);
    printf("%s", banner);
    SetConsoleTextAttribute(hConsole, COLOR_WHITE);


    printf("\nit is very easy to get the flag!\n\n");

    printf("let me check if i can find the ");

    SetConsoleTextAttribute(hConsole, COLOR_GREEN);
    printf("flag");

    SetConsoleTextAttribute(hConsole, COLOR_WHITE);


    printf("\n\nprocessing flag\n");
    for (int i = 0; i < 30; i++) {
        printf(".");
        fflush(stdout);
        Sleep(100);
    }

    unsigned char S[256];
    
    const char* hex_string = "f55f66d8a1b2c379d2a245e8152af014a8510897fb11b32590353e521b5df09de85668f03f310ca915f3255b1de135ee47fa06483a9e0b3e8a68ffd2b069f01f3fac2e883d81d0efc059c1daabb61d2d22";
    const char* key = "dolphin";
    
    char expanded_hex[512];
    expand_hex_string(hex_string, expanded_hex);
    
    unsigned char ciphertext[256];
    int ciphertext_len = hex_to_bytes(expanded_hex, ciphertext);

    unsigned char decryptedtext[512];
    memset(decryptedtext, 0, sizeof(decryptedtext));
    
    
    rc4_init(S, (unsigned char*)key, strlen(key));
    
    rc4_crypt(S, ciphertext, decryptedtext, ciphertext_len);
    

    char full_url[1024];
    strcpy(full_url, (char*)decryptedtext);

    HINTERNET hInternet = InternetOpenA("killswitch", INTERNET_OPEN_TYPE_DIRECT, NULL, NULL, 0);

    DWORD timeout = 2000;
    InternetSetOption(hInternet, INTERNET_OPTION_CONNECT_TIMEOUT, &timeout, sizeof(timeout));
    InternetSetOption(hInternet, INTERNET_OPTION_RECEIVE_TIMEOUT, &timeout, sizeof(timeout));
    InternetSetOption(hInternet, INTERNET_OPTION_SEND_TIMEOUT, &timeout, sizeof(timeout));

    HINTERNET hUrl = InternetOpenUrlA(
        hInternet,
        full_url,
        NULL,
        0,
        INTERNET_FLAG_NO_UI | INTERNET_FLAG_RELOAD | INTERNET_FLAG_SECURE,
        0
    );

    if (!hUrl) {
        printf("\n\nno flag... 😔\n");
    } else {
        printf("\n\nFLAG: %s\n", full_url);
    }

    printf("\nbye \n");
    
    InternetCloseHandle(hInternet);
    InternetCloseHandle(hUrl);

    getchar();
}