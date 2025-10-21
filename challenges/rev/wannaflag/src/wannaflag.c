#include <windows.h>
#include <wininet.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>

#pragma comment(lib, "wininet.lib")

#define COLOR_RED 12
#define COLOR_WHITE 15

void xor_decode(unsigned char* data, size_t length, const unsigned char* key, size_t keylen) {
    for (size_t i = 0; i < length; i++) {
        data[i] ^= key[i % keylen];
    }
}

int base64_decode(const char* input, uint8_t* output, size_t outlen) {
    static const unsigned char d[] = {
        64,64,64,64,64,64,64,64,64,64,64,64,64,64,64,64,
        64,64,64,64,64,64,64,64,64,64,64,64,64,64,64,64,
        64,64,64,64,64,64,64,64,64,64,64,62,64,64,64,63,
        52,53,54,55,56,57,58,59,60,61,64,64,64, 0,64,64,
        64, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,
        15,16,17,18,19,20,21,22,23,24,25,64,64,64,64,64,
        64,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,
        41,42,43,44,45,46,47,48,49,50,51,64,64,64,64,64
    };

    size_t len = strlen(input), i, j;
    uint32_t v = 0;
    int valb = -8;
    for (i = 0, j = 0; i < len && j < outlen; i++) {
        unsigned char c = input[i];
        if (c > 127 || d[c] == 64) continue;
        v = (v << 6) + d[c];
        valb += 6;
        if (valb >= 0) {
            output[j++] = (v >> valb) & 0xFF;
            valb -= 8;
        }
    }
    return (int)j;
}

const char* banner =
"██╗    ██╗ █████╗ ███╗   ██╗███╗   ██╗ █████╗ ███████╗██╗      █████╗  ██████╗ \n"
"██║    ██║██╔══██╗████╗  ██║████╗  ██║██╔══██╗██╔════╝██║     ██╔══██╗██╔════╝ \n"
"██║ █╗ ██║███████║██╔██╗ ██║██╔██╗ ██║███████║█████╗  ██║     ███████║██║  ███╗\n"
"██║███╗██║██╔══██║██║╚██╗██║██║╚██╗██║██╔══██║██╔══╝  ██║     ██╔══██║██║   ██║\n"
"╚███╔███╔╝██║  ██║██║ ╚████║██║ ╚████║██║  ██║██║     ███████╗██║  ██║╚██████╔╝\n"
" ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝ ╚═════╝ \n";


int main(void) {
    SetConsoleOutputCP(CP_UTF8);

    // Get console handle
    HANDLE hConsole = GetStdHandle(STD_OUTPUT_HANDLE);

    // Set text color to Red
    SetConsoleTextAttribute(hConsole, COLOR_RED);
    printf("%s\n", banner);

    // Reset color to normal (white) after banner
    SetConsoleTextAttribute(hConsole, COLOR_WHITE);


    printf("you thought it would be so easy to get the flag, huh!\n\n");

    printf("now get infected with this ");

    SetConsoleTextAttribute(hConsole, COLOR_RED);
    printf("flagsomware");

    printf("!!!\n\n");

    // Reset color to normal (white) after banner
    SetConsoleTextAttribute(hConsole, COLOR_WHITE);


    printf("stealing flags\n");
    for (int i = 0; i < 30; i++) {
        printf(".");
        fflush(stdout);
        Sleep(100);
    }

    const unsigned char key[] = { 0x42, 0x7A, 0xE1, 0x13 };

    unsigned char b64_xored[] =
        "\x23\x32\xb3\x23\x21\x3e\x8e\x65\x0e\x48\x8d\x22\x21\x2d\xb7\x6a"
        "\x18\x14\xaf\x65\x18\x32\xa0\x26\x23\x2d\xbb\x62\x1b\x22\xa3\x65"
        "\x21\x48\xb3\x7e\x23\x17\x89\x7d\x20\x49\xaf\x22\x21\x17\x8d\x62"
        "\x18\x17\xa7\x7f\x26\x49\xab\x20\x18\x22\xab\x7d\x26\x48\xb7\x7b"
        "\x0e\x17\xd4\x65\x0e\x0d\xdc\x2e";


    size_t b64_len = sizeof(b64_xored) - 1;

    xor_decode(b64_xored, b64_len, key, sizeof(key));

    // Null-terminate the base64 string
    char* b64_clean = (char*)malloc(b64_len + 1);
    memcpy(b64_clean, b64_xored, b64_len);
    b64_clean[b64_len] = '\0';

    unsigned char decoded_url[256] = { 0 };
    int url_len = base64_decode(b64_clean, decoded_url, sizeof(decoded_url) - 1);
    free(b64_clean);

    if (url_len <= 0) {
        return 1;
    }

    decoded_url[url_len] = '\0';

    HINTERNET hInternet = InternetOpenA("killswitch", INTERNET_OPEN_TYPE_DIRECT, NULL, NULL, 0);
    if (!hInternet) {
        return 1;
    }

    DWORD timeout = 2000;
    InternetSetOption(hInternet, INTERNET_OPTION_CONNECT_TIMEOUT, &timeout, sizeof(timeout));
    InternetSetOption(hInternet, INTERNET_OPTION_RECEIVE_TIMEOUT, &timeout, sizeof(timeout));
    InternetSetOption(hInternet, INTERNET_OPTION_SEND_TIMEOUT, &timeout, sizeof(timeout));

    HINTERNET hUrl = InternetOpenUrlA(
        hInternet,
        (const char*)decoded_url,
        NULL,
        0,
        INTERNET_FLAG_NO_UI | INTERNET_FLAG_RELOAD | INTERNET_FLAG_SECURE,
        0
    );

    if (hUrl) {
        InternetCloseHandle(hUrl);
        printf("\n\nABORTED!\n");
        printf("okay, you're safe for now 💀\n");
    }

    InternetCloseHandle(hInternet);
    printf("\nbye \n");
    getchar();
}