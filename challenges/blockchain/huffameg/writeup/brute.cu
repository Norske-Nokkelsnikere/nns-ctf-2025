#include <cuda_runtime.h>
#include <device_launch_parameters.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <time.h>

// type definitions from your working implementation
typedef unsigned char BYTE;
typedef unsigned int WORD;
typedef unsigned long long LONG;

#define KECCAK_ROUND 24
#define KECCAK_STATE_SIZE 25
#define KECCAK_Q_SIZE 192
#define MAX_STRING_LENGTH 32

__constant__ LONG CUDA_KECCAK_CONSTS[24] = {
    0x0000000000000001, 0x0000000000008082, 0x800000000000808a, 0x8000000080008000,
    0x000000000000808b, 0x0000000080000001, 0x8000000080008081, 0x8000000000008009,
    0x000000000000008a, 0x0000000000000088, 0x0000000080008009, 0x000000008000000a,
    0x000000008000808b, 0x800000000000008b, 0x8000000000008089, 0x8000000000008003,
    0x8000000000008002, 0x8000000000000080, 0x000000000000800a, 0x800000008000000a,
    0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008
};

typedef struct {
    BYTE sha3_flag;
    WORD digestbitlen;
    LONG rate_bits;
    LONG rate_BYTEs;
    LONG absorb_round;
    int64_t state[KECCAK_STATE_SIZE];
    BYTE q[KECCAK_Q_SIZE];
    LONG bits_in_queue;
} cuda_keccak_ctx_t;

// all the device functions from your working implementation
__device__ LONG cuda_keccak_leuint64(void* in) {
    LONG a;
    memcpy(&a, in, 8);
    return a;
}

__device__ int64_t cuda_keccak_MIN(int64_t a, int64_t b) {
    if (a > b) return b;
    return a;
}

__device__ LONG cuda_keccak_UMIN(LONG a, LONG b) {
    if (a > b) return b;
    return a;
}

__device__ void cuda_keccak_extract(cuda_keccak_ctx_t* ctx) {
    LONG len = ctx->rate_bits >> 6;
    int64_t a;
    int s = sizeof(LONG);
    for (int i = 0; i < len; i++) {
        a = cuda_keccak_leuint64((int64_t*)&ctx->state[i]);
        memcpy(ctx->q + (i * s), &a, s);
    }
}

__device__ __forceinline__ LONG cuda_keccak_ROTL64(LONG a, LONG b) {
    return (a << b) | (a >> (64 - b));
}

__device__ void cuda_keccak_permutations(cuda_keccak_ctx_t* ctx) {
    int64_t* A = ctx->state;
    int64_t* a00 = A, * a01 = A + 1, * a02 = A + 2, * a03 = A + 3, * a04 = A + 4;
    int64_t* a05 = A + 5, * a06 = A + 6, * a07 = A + 7, * a08 = A + 8, * a09 = A + 9;
    int64_t* a10 = A + 10, * a11 = A + 11, * a12 = A + 12, * a13 = A + 13, * a14 = A + 14;
    int64_t* a15 = A + 15, * a16 = A + 16, * a17 = A + 17, * a18 = A + 18, * a19 = A + 19;
    int64_t* a20 = A + 20, * a21 = A + 21, * a22 = A + 22, * a23 = A + 23, * a24 = A + 24;

    for (int i = 0; i < KECCAK_ROUND; i++) {
        // Theta
        int64_t c0 = *a00 ^ *a05 ^ *a10 ^ *a15 ^ *a20;
        int64_t c1 = *a01 ^ *a06 ^ *a11 ^ *a16 ^ *a21;
        int64_t c2 = *a02 ^ *a07 ^ *a12 ^ *a17 ^ *a22;
        int64_t c3 = *a03 ^ *a08 ^ *a13 ^ *a18 ^ *a23;
        int64_t c4 = *a04 ^ *a09 ^ *a14 ^ *a19 ^ *a24;

        int64_t d1 = cuda_keccak_ROTL64(c1, 1) ^ c4;
        int64_t d2 = cuda_keccak_ROTL64(c2, 1) ^ c0;
        int64_t d3 = cuda_keccak_ROTL64(c3, 1) ^ c1;
        int64_t d4 = cuda_keccak_ROTL64(c4, 1) ^ c2;
        int64_t d0 = cuda_keccak_ROTL64(c0, 1) ^ c3;

        *a00 ^= d1; *a05 ^= d1; *a10 ^= d1; *a15 ^= d1; *a20 ^= d1;
        *a01 ^= d2; *a06 ^= d2; *a11 ^= d2; *a16 ^= d2; *a21 ^= d2;
        *a02 ^= d3; *a07 ^= d3; *a12 ^= d3; *a17 ^= d3; *a22 ^= d3;
        *a03 ^= d4; *a08 ^= d4; *a13 ^= d4; *a18 ^= d4; *a23 ^= d4;
        *a04 ^= d0; *a09 ^= d0; *a14 ^= d0; *a19 ^= d0; *a24 ^= d0;

        // Rho pi
        c1 = cuda_keccak_ROTL64(*a01, 1);
        *a01 = cuda_keccak_ROTL64(*a06, 44); *a06 = cuda_keccak_ROTL64(*a09, 20);
        *a09 = cuda_keccak_ROTL64(*a22, 61); *a22 = cuda_keccak_ROTL64(*a14, 39);
        *a14 = cuda_keccak_ROTL64(*a20, 18); *a20 = cuda_keccak_ROTL64(*a02, 62);
        *a02 = cuda_keccak_ROTL64(*a12, 43); *a12 = cuda_keccak_ROTL64(*a13, 25);
        *a13 = cuda_keccak_ROTL64(*a19, 8); *a19 = cuda_keccak_ROTL64(*a23, 56);
        *a23 = cuda_keccak_ROTL64(*a15, 41); *a15 = cuda_keccak_ROTL64(*a04, 27);
        *a04 = cuda_keccak_ROTL64(*a24, 14); *a24 = cuda_keccak_ROTL64(*a21, 2);
        *a21 = cuda_keccak_ROTL64(*a08, 55); *a08 = cuda_keccak_ROTL64(*a16, 45);
        *a16 = cuda_keccak_ROTL64(*a05, 36); *a05 = cuda_keccak_ROTL64(*a03, 28);
        *a03 = cuda_keccak_ROTL64(*a18, 21); *a18 = cuda_keccak_ROTL64(*a17, 15);
        *a17 = cuda_keccak_ROTL64(*a11, 10); *a11 = cuda_keccak_ROTL64(*a07, 6);
        *a07 = cuda_keccak_ROTL64(*a10, 3); *a10 = c1;

        // Chi
        c0 = *a00 ^ (~*a01 & *a02); c1 = *a01 ^ (~*a02 & *a03);
        *a02 ^= ~*a03 & *a04; *a03 ^= ~*a04 & *a00; *a04 ^= ~*a00 & *a01;
        *a00 = c0; *a01 = c1;

        c0 = *a05 ^ (~*a06 & *a07); c1 = *a06 ^ (~*a07 & *a08);
        *a07 ^= ~*a08 & *a09; *a08 ^= ~*a09 & *a05; *a09 ^= ~*a05 & *a06;
        *a05 = c0; *a06 = c1;

        c0 = *a10 ^ (~*a11 & *a12); c1 = *a11 ^ (~*a12 & *a13);
        *a12 ^= ~*a13 & *a14; *a13 ^= ~*a14 & *a10; *a14 ^= ~*a10 & *a11;
        *a10 = c0; *a11 = c1;

        c0 = *a15 ^ (~*a16 & *a17); c1 = *a16 ^ (~*a17 & *a18);
        *a17 ^= ~*a18 & *a19; *a18 ^= ~*a19 & *a15; *a19 ^= ~*a15 & *a16;
        *a15 = c0; *a16 = c1;

        c0 = *a20 ^ (~*a21 & *a22); c1 = *a21 ^ (~*a22 & *a23);
        *a22 ^= ~*a23 & *a24; *a23 ^= ~*a24 & *a20; *a24 ^= ~*a20 & *a21;
        *a20 = c0; *a21 = c1;

        // Iota
        *a00 ^= CUDA_KECCAK_CONSTS[i];
    }
}

__device__ void cuda_keccak_absorb(cuda_keccak_ctx_t* ctx, BYTE* in) {
    LONG offset = 0;
    for (LONG i = 0; i < ctx->absorb_round; ++i) {
        ctx->state[i] ^= cuda_keccak_leuint64(in + offset);
        offset += 8;
    }
    cuda_keccak_permutations(ctx);
}

__device__ void cuda_keccak_pad(cuda_keccak_ctx_t* ctx) {
    ctx->q[ctx->bits_in_queue >> 3] |= (1L << (ctx->bits_in_queue & 7));

    if (++(ctx->bits_in_queue) == ctx->rate_bits) {
        cuda_keccak_absorb(ctx, ctx->q);
        ctx->bits_in_queue = 0;
    }

    LONG full = ctx->bits_in_queue >> 6;
    LONG partial = ctx->bits_in_queue & 63;
    LONG offset = 0;

    for (int i = 0; i < full; ++i) {
        ctx->state[i] ^= cuda_keccak_leuint64(ctx->q + offset);
        offset += 8;
    }

    if (partial > 0) {
        LONG mask = (1L << partial) - 1;
        ctx->state[full] ^= cuda_keccak_leuint64(ctx->q + offset) & mask;
    }

    ctx->state[(ctx->rate_bits - 1) >> 6] ^= 9223372036854775808ULL;
    cuda_keccak_permutations(ctx);
    cuda_keccak_extract(ctx);
    ctx->bits_in_queue = ctx->rate_bits;
}

__device__ void cuda_keccak_init(cuda_keccak_ctx_t* ctx, WORD digestbitlen) {
    memset(ctx, 0, sizeof(cuda_keccak_ctx_t));
    ctx->sha3_flag = 0;
    ctx->digestbitlen = digestbitlen;
    ctx->rate_bits = 1600 - ((ctx->digestbitlen) << 1);
    ctx->rate_BYTEs = ctx->rate_bits >> 3;
    ctx->absorb_round = ctx->rate_bits >> 6;
    ctx->bits_in_queue = 0;
}

__device__ void cuda_keccak_update(cuda_keccak_ctx_t* ctx, BYTE* in, LONG inlen) {
    int64_t BYTEs = ctx->bits_in_queue >> 3;
    int64_t count = 0;
    while (count < inlen) {
        if (BYTEs == 0 && count <= ((int64_t)(inlen - ctx->rate_BYTEs))) {
            do {
                cuda_keccak_absorb(ctx, in + count);
                count += ctx->rate_BYTEs;
            } while (count <= ((int64_t)(inlen - ctx->rate_BYTEs)));
        }
        else {
            int64_t partial = cuda_keccak_MIN(ctx->rate_BYTEs - BYTEs, inlen - count);
            memcpy(ctx->q + BYTEs, in + count, partial);
            BYTEs += partial;
            count += partial;
            if (BYTEs == ctx->rate_BYTEs) {
                cuda_keccak_absorb(ctx, ctx->q);
                BYTEs = 0;
            }
        }
    }
    ctx->bits_in_queue = BYTEs << 3;
}

__device__ void cuda_keccak_final(cuda_keccak_ctx_t* ctx, BYTE* out) {
    if (ctx->sha3_flag) {
        int mask = (1 << 2) - 1;
        ctx->q[ctx->bits_in_queue >> 3] = (BYTE)(0x02 & mask);
        ctx->bits_in_queue += 2;
    }

    cuda_keccak_pad(ctx);
    LONG i = 0;

    while (i < ctx->digestbitlen) {
        if (ctx->bits_in_queue == 0) {
            cuda_keccak_permutations(ctx);
            cuda_keccak_extract(ctx);
            ctx->bits_in_queue = ctx->rate_bits;
        }

        LONG partial_block = cuda_keccak_UMIN(ctx->bits_in_queue, ctx->digestbitlen - i);
        memcpy(out + (i >> 3), ctx->q + (ctx->rate_BYTEs - (ctx->bits_in_queue >> 3)), partial_block >> 3);
        ctx->bits_in_queue -= partial_block;
        i += partial_block;
    }
}

// generate function call format from index (a(), b(), ..., aa(), ab(), ...)
__device__ void generate_function_call(uint64_t idx, char* result, int* length) {
    char func_name[MAX_STRING_LENGTH];
    int pos = 0;
    uint64_t temp = idx;

    if (temp == 0) {
        func_name[0] = 'a';
        pos = 1;
    }
    else {
        while (temp > 0 && pos < MAX_STRING_LENGTH - 3) {
            func_name[pos++] = 'a' + (temp % 26);
            temp /= 26;
        }
    }

    // format as function call: name()
    for (int i = 0; i < pos; i++) {
        result[i] = func_name[i];
    }
    result[pos] = '(';
    result[pos + 1] = ')';
    result[pos + 2] = '\0';
    *length = pos + 2;
}

// brute force kernel with progress tracking
__global__ void bruteforce_kernel_optimized(
    uint64_t start_idx,
    uint64_t batch_size,
    int* found,
    char* result,
    BYTE* full_hash,
    uint64_t* progress,
    char* latest_guess,
    BYTE* latest_hash
) {
    uint64_t idx = blockIdx.x * blockDim.x + threadIdx.x + start_idx;
    uint64_t thread_id = blockIdx.x * blockDim.x + threadIdx.x;

    if (thread_id >= batch_size || *found) return;

    // generate function call
    char function_call[MAX_STRING_LENGTH];
    int length;
    generate_function_call(idx, function_call, &length);

    // compute keccak-256 hash
    cuda_keccak_ctx_t ctx;
    BYTE hash[32];
    cuda_keccak_init(&ctx, 256);
    cuda_keccak_update(&ctx, (BYTE*)function_call, length);
    cuda_keccak_final(&ctx, hash);

    // check first 4 bytes for target (modify TARGET_BYTES as needed)
    uint32_t first_four = (hash[0] << 24) | (hash[1] << 16) | (hash[2] << 8) | hash[3];
    const uint32_t TARGET_BYTES = 0x890d6908; // Change this to your target

    if (first_four == TARGET_BYTES) {
        *found = 1;
        memcpy(result, function_call, length + 1);
        memcpy(full_hash, hash, 32);
    }

    // update progress (every thread increments)
    atomicAdd((unsigned long long*)progress, 1ULL);

    // sample latest guesses from some threads for display
    if (thread_id % 100000 == 0) {
        memcpy(latest_guess + (thread_id / 100000) * MAX_STRING_LENGTH, function_call, length + 1);
        memcpy(latest_hash + (thread_id / 100000) * 32, hash, 32);
    }
}

void print_progress(uint64_t current_progress, uint64_t current_index, time_t start_time) {
    time_t current_time = time(NULL);
    double elapsed = difftime(current_time, start_time);

    if (elapsed > 0) {
        double rate_mhs = (current_progress / 1000000.0) / elapsed;
        printf("\rprogress: %llu function calls | %.2f MH/s | elapsed: %.0fs",
            current_progress, rate_mhs, elapsed);
        fflush(stdout);
    }
}

int main() {
    const uint32_t TARGET_BYTES = 0x00000000; // Change this to your 4-byte target
    const uint64_t batch_size = 10000000;     // 10M per batch
    const int threads = 256;
    const int blocks = (batch_size + threads - 1) / threads;

    printf("cuda keccak-256 function call brute force\n");
    printf("target: 0x%08x (first 4 bytes)\n", TARGET_BYTES);
    printf("searching for function calls: a(), b(), c(), ..., aa(), ab(), ...\n\n");

    // GPU memory allocation
    int* d_found, h_found = 0;
    char* d_result, * h_result;
    BYTE* d_full_hash, * h_full_hash;
    uint64_t* d_progress, h_progress = 0;
    char* d_latest_guess, * h_latest_guess;
    BYTE* d_latest_hash, * h_latest_hash;

    cudaMalloc(&d_found, sizeof(int));
    cudaMalloc(&d_result, MAX_STRING_LENGTH + 3);
    cudaMalloc(&d_full_hash, 32);
    cudaMalloc(&d_progress, sizeof(uint64_t));
    cudaMalloc(&d_latest_guess, MAX_STRING_LENGTH * 100); // Sample from 100 threads
    cudaMalloc(&d_latest_hash, 32 * 100);

    h_result = (char*)malloc(MAX_STRING_LENGTH + 3);
    h_full_hash = (BYTE*)malloc(32);
    h_latest_guess = (char*)malloc(MAX_STRING_LENGTH * 100);
    h_latest_hash = (BYTE*)malloc(32 * 100);

    cudaMemset(d_found, 0, sizeof(int));
    cudaMemset(d_progress, 0, sizeof(uint64_t));

    time_t start_time = time(NULL);
    uint64_t current_index = 0;

    printf("Starting brute force...\n");

    while (h_found == 0) {
        bruteforce_kernel_optimized << <blocks, threads >> > (
            current_index, batch_size, d_found, d_result, d_full_hash, d_progress,
            d_latest_guess, d_latest_hash);

        cudaDeviceSynchronize();

        cudaMemcpy(&h_found, d_found, sizeof(int), cudaMemcpyDeviceToHost);
        cudaMemcpy(&h_progress, d_progress, sizeof(uint64_t), cudaMemcpyDeviceToHost);

        print_progress(h_progress, current_index, start_time);

        // show latest guesses periodically
        if (current_index % (batch_size * 5) == 0 && current_index > 0) {
            cudaMemcpy(h_latest_guess, d_latest_guess, MAX_STRING_LENGTH * 5, cudaMemcpyDeviceToHost);
            cudaMemcpy(h_latest_hash, d_latest_hash, 32 * 5, cudaMemcpyDeviceToHost);

            printf("\nlatest samples:\n");
            for (int i = 0; i < 5; i++) {
                printf("   %s -> ", h_latest_guess + i * MAX_STRING_LENGTH);
                for (int j = 0; j < 8; j++) { // show first 8 bytes of hash
                    printf("%02x", h_latest_hash[i * 32 + j]);
                }
                printf("...\n");
            }
        }

        if (h_found) {
            cudaMemcpy(h_result, d_result, MAX_STRING_LENGTH + 3, cudaMemcpyDeviceToHost);
            cudaMemcpy(h_full_hash, d_full_hash, 32, cudaMemcpyDeviceToHost);

            // skip if result is "solve()"
            if (strcmp(h_result, "solve()") == 0) {
                printf("Skipping 'solve()'\n");
                h_found = 0;
                cudaMemset(d_found, 0, sizeof(int));
                current_index += batch_size;
                continue;
            }

            printf("\n\n*** verified match found! ***\n");
            printf("function call: %s\n", h_result);
            printf("full keccak-256 hash: ");
            for (int i = 0; i < 32; i++) {
                printf("%02x", h_full_hash[i]);
            }
            printf("\n");

            uint32_t first_four = (h_full_hash[0] << 24) | (h_full_hash[1] << 16) |
                (h_full_hash[2] << 8) | h_full_hash[3];
            printf("first 4 bytes: 0x%08x (target: 0x%08x)\n", first_four, TARGET_BYTES);
            break;
        }

        current_index += batch_size;

        if (current_index > 50000000000ULL) {
            printf("\n\nreached 50B attempts limit.\n");
            break;
        }
    }

    time_t end_time = time(NULL);
    double total_time = difftime(end_time, start_time);
    printf("\n\nstats:\n");
    printf("tested: %llu function calls\n", h_progress);
    printf("time: %.2f seconds\n", total_time);
    if (total_time > 0) {
        printf("rate: %.2f MH/s\n", (h_progress / 1000000.0) / total_time);
    }

    // Cleanup
    cudaFree(d_found); cudaFree(d_result); cudaFree(d_full_hash);
    cudaFree(d_progress); cudaFree(d_latest_guess); cudaFree(d_latest_hash);
    free(h_result); free(h_full_hash); free(h_latest_guess); free(h_latest_hash);

    return 0;
}