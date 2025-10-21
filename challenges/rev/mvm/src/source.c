#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

int SBNZ4(int pc, int *R, int B, int A, int J) {
    int r = B - A;
    if (R != NULL) {
        *R = r;
    }
    if (r != 0) {
        return J;
    } else {
        return pc + 4;
    }
}

int mov(int x) {
    int negx;
    int y;
    SBNZ4(0, &negx, 0, x, 0);
    SBNZ4(0, &y,    0, negx, 0);
    return y;
}

int sub_raw(int a, int b) {
    int r;
    SBNZ4(0, &r, b, a, 0);
    return r;
}

int add(int a, int b) {
    int nega;
    int r;
    SBNZ4(0, &nega, 0, a, 0);
    SBNZ4(0, &r,    b, nega, 0);
    return r;
}

int dec1(int x) {
    int r;
    SBNZ4(0, &r, x, 1, 0);
    return r;
}

int inc1(int x) {
    int r;
    SBNZ4(0, &r, x, -1, 0);
    return r;
}

int is_zero(int x) {
    int t;
    int ret = SBNZ4(0, &t, x, 0, 0);
    if (ret != 0) {
        return 1;
    } else {
        return 0;
    }
}

int geq(int a, int b) {
    int ta = mov(a);
    int tb = mov(b);
    while (!is_zero(ta) && !is_zero(tb)) {
        ta = dec1(ta);
        tb = dec1(tb);
    }
    if (is_zero(tb)) {
        return 1;
    } else {
        return 0;
    }
}

int mul(int a, int b) {
    int x = mov(a);
    int y = mov(b);
    if (geq(a, b)) {
        int t = x; x = y; y = t;
    }
    int acc = 0;
    while (!is_zero(x)) {
        acc = add(acc, y);
        x = dec1(x);
    }
    return acc;
}

int mod_small(int a, int b) {
    int x = mov(a);
    while (geq(x, b)) {
        x = sub_raw(b, x);
    }
    return x;
}

int div_small(int a, int b) {
    int x = mov(a);
    int q = 0;
    while (geq(x, b)) {
        x = sub_raw(b, x);
        q = inc1(q);
    }
    return q;
}

int xor32(int a, int b) {
    int res = 0;
    int place = 1;
    int two = 2;

    while (!is_zero(add(a, b))) {
        int abit = mod_small(a, two);
        int bbit = mod_small(b, two);
        int sum  = add(abit, bbit);

        int tmp;
        int ret = SBNZ4(0, &tmp, sum, 1, 0);
        if (ret != 0) {
            res = add(res, place);
        }

        a = div_small(a, two);
        b = div_small(b, two);
        place = add(place, place);
    }
    return res;
}

int and32(int a, int b) {
    int res = 0;
    int place = 1;
    int two = 2;

    while (!is_zero(add(a, b))) {
        int abit = mod_small(a, two);
        int bbit = mod_small(b, two);
        int prod = mul(abit, bbit);
        int addend = mul(prod, place);
        res = add(res, addend);

        a = div_small(a, two);
        b = div_small(b, two);
        place = add(place, place);
    }
    return res;
}

int sub_wr(int x, int y) {
    return sub_raw(y, x);
}

// vm
#define FLAG_LEN 64
#define NUM_REGS 8
#define OP_LDI   144
#define OP_NEXT  128
#define OP_ADD   161
#define OP_SUB   162
#define OP_XOR   68
#define OP_JNZ   184
#define OP_HALT  254

typedef struct {
    int regs[NUM_REGS];
    const unsigned char *in;
    int in_len;
    int in_idx;
} VM;

static const int PROGRAM[] = {
    144,3,7,     // R3 = 7
    144,4,64,    // R4 = 64
    144,2,0,     // R2 = index
    144,1,0,     // R1 = accumilator
    144,7,1,     // R7 = 1

    // label L:
    128,0,0,     // NEXT  R0
    68,0,6,      // XOR   R0, R6   (loads key[i])
    68,0,3,      // XOR   R0, R3   (^7)
    68,0,2,      // XOR   R0, R2   (^index)
    68,0,1,      // XOR   R0, R1   (^acc)
    162,0,5,     // SUB   R0, R5   (loads ct[i], R0 = ct - t)
    184,0,16,    // JNZ   R0, +16  FAIL if no match

    68,6,1,      // XOR   R6, R1
    184,6,4,     // if R6 != 0 jump to B
    68,6,1,      // A:
    68,1,6,      //   acc ^= key
    184,7,2,     //   unconditional jump (since R7==1)
    68,6,1,      // B:
    68,1,2,      //   acc ^= index      
    68,1,6,      //   acc ^= key
    68,1,2,      //   acc ^= index

    161,2,7,     // index++
    144,5,0,     // R5 = 0
    161,5,2,     // R5 = R2 (copy)
    162,5,4,     // R5 = 64 - R2
    184,5,-20,   // if R2 != 64, jump back to label "L"
    254,1,0,     // HALT 1 (success)
    254,0,0      // FAIL: HALT 0
};


// 128 byte blob: key || ct
static const unsigned char BLOB[] = {
    // key
    187, 84, 170, 196, 184, 157, 200, 104, 186, 55, 15, 230, 147, 189, 100, 151,
    230, 93, 21, 36, 218, 94, 132, 52, 11, 235, 215, 44, 187, 35, 108, 136,
    174, 181, 132, 4, 27, 30, 98, 121, 65, 206, 124, 239, 191, 31, 140, 5,
    112, 128, 106, 100, 180, 66, 190, 108, 0, 44, 174, 246, 43, 233, 39, 123,
    // ct
    242, 167, 19, 254, 10, 200, 94, 91, 128, 233, 248, 91, 138, 49, 64, 130,
    125, 32, 104, 124, 173, 227, 104, 73, 72, 138, 29, 53, 204, 197, 145, 76,
    178, 108, 167, 181, 240, 176, 138, 181, 190, 35, 96, 224, 7, 4, 207, 142,
    230, 113, 76, 47, 157, 128, 102, 97, 82, 44, 196, 40, 93, 189, 153, 161
};

// interpreter
int run_program_words(const int *prog, int nwords, VM *vm) {
    if (nwords % 3 != 0) { 
        return -1; 
    }
    int ninstr = nwords / 3;
    int pc = 0;
    
    for (int i = 0; i < NUM_REGS; i++) {
        vm->regs[i] = 0; 
    }
    vm->in_idx = 0;
    while (pc >= 0 && pc < ninstr) {
        int op = prog[3*pc+0];
        int a  = prog[3*pc+1];
        int b  = prog[3*pc+2];

        if (op == OP_LDI) {
            vm->regs[a] = mov(b);
            pc = inc1(pc);
            continue;
        }
        if (op == OP_NEXT) {
            vm->regs[a] = vm->in[vm->in_idx];
            vm->in_idx = inc1(vm->in_idx);
            pc = inc1(pc);
            continue;
        }
        if (op == OP_ADD) {
            vm->regs[a] = add(vm->regs[a], vm->regs[b]);
            pc = inc1(pc);
            continue;
        }
        if (op == OP_SUB) {
            if (b == 5) {
                int idx  = dec1(vm->in_idx); 
                int off  = add(64, idx);  
                vm->regs[5] = BLOB[off];
            }
            vm->regs[a] = sub_wr(vm->regs[a], vm->regs[b]);
            pc = inc1(pc);
            continue;
        }
        if (op == OP_XOR) {
            if (b == 6) {
                int idx = dec1(vm->in_idx); 
                int off = mov(idx);   
                vm->regs[6] = BLOB[off];
            }
            vm->regs[a] = xor32(vm->regs[a], vm->regs[b]);
            pc = inc1(pc);
            continue;
        }
        if (op == OP_JNZ) {
            if (!is_zero(vm->regs[a])) { 
                pc = add(pc, b); 
            } else { 
                pc = inc1(pc); 
            }
            continue;
        }
        if (op == OP_HALT) {
            int code = and32(a, 1);
            return code;
        }
        return -1;
    }
    return -1;
}

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "usage: %s <flag>\n", argv[0]);
        return 1;
    }

    size_t len = strlen(argv[1]);
    if ((int)len != FLAG_LEN) {
        fprintf(stderr, "wrong length\n");
        return 1;
    }

    VM vm;
    vm.in = (const unsigned char *)argv[1];
    vm.in_len = (int)len;

    int rc = run_program_words(PROGRAM, (int)(sizeof(PROGRAM) / sizeof(PROGRAM[0])), &vm);

    if (rc == 1) {
        puts("correct");
        return 0;
    } else {
        puts("incorrect");
        return 1;
    }
}
