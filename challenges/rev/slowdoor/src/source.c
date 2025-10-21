#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/bn.h>

static uint64_t fmod_naive(uint64_t n, uint64_t m) {
    if (m == 0) return 0;
    if (n <= 1) return n % m;
    return (fmod_naive(n - 1, m) + fmod_naive(n - 2, m)) % m;
}

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "usage: %s <N>\n", argv[0]);
        return 1;
    }

    const uint64_t C = 313333333337ULL;
    const uint64_t Dword = 31333333333337ULL;
    const uint64_t Bword = 3133333337ULL;

    // ciphertext
    static const unsigned char CT[24] = {
        0x42,0x54,0x8d,0x65,0x93,0xf5,0xb9,0x24,
        0xfa,0xbf,0xa2,0x91,0xc1,0x9c,0xf0,0xdb,
        0x72,0xd7,0x7f,0x72,0xf5,0x48,0x4a,0xf6
    };

    // parse input N
    char *end = NULL;
    uint64_t N = strtoull(argv[1], &end, 10);
    if (!argv[1][0] || (end && *end != '\0')) {
        fprintf(stderr, "invalid number\n");
        return 2;
    }

    // base = fib(N) mod C (naive)
    uint64_t base_mod = fmod_naive(N, C);

    // only decrypt for the intended N, otherwise print fibonacci number mod C 
    if (N != 31333337ULL) {
        printf("%llu\n", (unsigned long long)base_mod);
        return 0;
    }

    // k = 1337 * pow(base_mod, B, D^4)
    BN_CTX *ctx = BN_CTX_new();
    if (!ctx) return 3;

    BIGNUM *bn_base = BN_new();
    BIGNUM *bn_exp  = BN_new();
    BIGNUM *bn_D    = BN_new();
    BIGNUM *bn_mod  = BN_new();
    BIGNUM *bn_res  = BN_new();
    BIGNUM *bn_four = BN_new();

    if (!bn_base || !bn_exp || !bn_D || !bn_mod || !bn_res || !bn_four) {
        return 4;
    }

    BN_set_word(bn_base, (BN_ULONG)base_mod);
    BN_set_word(bn_exp,  (BN_ULONG)Bword);
    BN_set_word(bn_D,    (BN_ULONG)Dword);
    BN_set_word(bn_four, 4);

    // bn_mod = D^4
    if (BN_exp(bn_mod, bn_D, bn_four, ctx) != 1) {
        return 5;
    }

    // bn_res = base^B mod (D^4)
    if (BN_mod_exp(bn_res, bn_base, bn_exp, bn_mod, ctx) != 1) {
        return 6;
    }

    // k = 1337 * bn_res  (no mod)
    if (BN_mul_word(bn_res, 1337) != 1) {
        return 7;
    }

    // export k to minimal big-endian bytes (long_to_bytes)
    int key_len = BN_num_bytes(bn_res);
    unsigned char *key = NULL;
    if (key_len == 0) {
        key_len = 1;
        key = (unsigned char*)malloc(1);
        if (!key) return 8;
        key[0] = 0x00;
    } else {
        key = (unsigned char*)malloc((size_t)key_len);
        if (!key) return 8;
        BN_bn2bin(bn_res, key);
    }

    // repeat key to XOR with ct 
    unsigned char pt[sizeof(CT) + 1];
    for (size_t i = 0; i < sizeof(CT); ++i) {
        unsigned char kbyte = key[i % key_len];
        pt[i] = CT[i] ^ kbyte;
    }
    pt[sizeof(CT)] = '\0';

    fwrite(pt, 1, sizeof(CT), stdout);
    fputc('\n', stdout);

    free(key);
    BN_free(bn_base);
    BN_free(bn_exp);
    BN_free(bn_D);
    BN_free(bn_mod);
    BN_free(bn_res);
    BN_free(bn_four);
    BN_CTX_free(ctx);
    return 0;
}
