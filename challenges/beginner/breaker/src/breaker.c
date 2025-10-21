#include <stdio.h>
#include <stdlib.h>

// Equivalent of check_1 to check_6
int check_1(int y) { return y; }
int check_2(int y) { return y + 0 - 0; }
int check_3(int y) { return y * 1 / 1; }
int check_4(int y) { return (y ^ 0) | 0; }
int check_5(int y) { return y & 0xFF; }
int check_6(int y) { return y; }  // Only integers here

int wieytoieytoie(int x) {
    int y = check_1(x);
    y = check_2(y);
    y = check_3(y);
    y = check_4(y);
    y = check_5(y);
    y = check_6(y);
    return y;
}

int temp_flag_store(int x) {
    int y = x;
    return y;
}

// XOR two arrays and print each decoded letter
void jvkanciuhfasiduhfisd(int *flag_list, int flag_len, int *key_list, int key_len) {
    for (int i = 0; i < flag_len; i++) {
        int flag_val = wieytoieytoie(flag_list[i]);
        int key_val = wieytoieytoie(key_list[i % key_len]);
        int xored = flag_val ^ key_val;
        temp_flag_store(xored);
    }
}

const char* banner =
".#####...#####...######...####...##..##..######..#####..   \n"
".##..##..##..##..##......##..##..##.##...##......##..##. \n"
".#####...#####...####....######..####....####....#####..  \n"
".##..##..##..##..##......##..##..##.##...##......##..##. \n"
".#####...##..##..######..##..##..##..##..######..##..##. \n";


int main() {
    int flag[] = {32, 47, 33, 91, 5, 14, 24, 69, 20, 62, 13, 27, 75, 4, 51, 6, 4, 71, 20, 11, 7, 45, 66, 20, 21, 127, 1, 0, 4, 93, 32, 47, 33, 91, 5, 14, 24, 69, 20, 62, 13, 27, 75, 4, 51, 6, 4, 71, 20, 11, 7, 45, 66, 20, 21, 127, 1, 0, 4, 93, 32, 47, 33, 91, 5, 14, 24, 69, 20, 62, 13, 27, 75, 4, 51, 6, 4, 71, 20, 11, 7, 45, 66, 20, 21, 127, 1, 0, 4, 93};
    int key[] = {110, 97, 114, 32, 104, 97, 110, 32, 103, 97, 97, 114, 32, 97, 108, 108, 101, 32, 115, 110, 117, 114, 32, 97, 97, 32, 115, 101, 114, 32, 112, 97, 32, 104, 97, 110, 13, 10, 105, 107, 107, 106, 101, 32, 108, 111, 101, 121, 101, 32, 100, 101, 116, 32, 115, 97, 97, 32, 115, 116, 121, 103, 103, 101, 32, 115, 111, 109, 32, 104, 97, 110, 32, 101, 114, 13, 10};

    int flag_len = sizeof(flag) / sizeof(flag[0]);
    int key_len = sizeof(key) / sizeof(key[0]);

    printf("%s\n", banner);
    printf("I'm gonna break all prograjflknsafkjsncsmdcsmlkcsadslcmsadcmsadmcsajdnckansdlkcnskdnc");

    // Second XOR: flag ^ temp_key -> final_flag
    jvkanciuhfasiduhfisd(flag, flag_len, key, key_len);

    return 0;
}
