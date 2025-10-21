#include "dsp.h"
#include <zephyr/kernel.h>
#include <string.h>

size_t conv(const uint16_t* a, size_t a_len, const uint32_t* b, size_t b_len, uint32_t* out)
{
    // out[n] = sum k = -inf to inf a[k] b[n - k]

    size_t out_len = a_len + b_len - 1;

    for (size_t n = 0; n < out_len; n++)
    {
        size_t sum = 0;
        for (size_t k = 0; k < a_len; k++)
        {
            if (n - k < 0 || n - k >= b_len) continue;
            sum += a[k] * b[n - k];
        }
        out[n] = sum;
    }

    return out_len;
}

const uint32_t target_convolution[] = {9360, 9906, 24936, 37415, 46360, 68595, 76396, 86722, 95222, 96664, 106958, 102069, 110217, 109082, 121930, 142873, 136572, 162669, 167382, 190314, 208310, 221270, 222461, 245982, 248875, 256643, 268493, 265773, 266114, 294814, 278405, 285790, 284782, 269811, 252955, 233798, 224376, 218452, 227839, 215615, 221736, 208057, 195885, 191432, 188359, 158370, 160078, 142219, 120578, 110044, 110803, 86508, 81798, 70485, 62077, 56312, 48734, 31900, 13625};

const uint32_t convolution_system[] = {120, 7, 185, 98, 110, 203, 145, 99, 86, 18, 83, 77, 49, 29, 104, 124, 123, 188, 85, 177, 198, 169, 34, 168, 79, 107, 72, 63, 112, 211, 168, 109};

bool is_flag(const uint16_t* buffer, size_t length)
{
    uint32_t out_buffer[ARRAY_SIZE(target_convolution)];

    conv(buffer, length, convolution_system, ARRAY_SIZE(convolution_system), out_buffer);

    return !memcmp(out_buffer, target_convolution, sizeof(target_convolution));
}