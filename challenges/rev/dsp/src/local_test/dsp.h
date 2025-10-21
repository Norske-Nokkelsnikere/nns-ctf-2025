#pragma once
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

size_t conv(const uint16_t* a, size_t a_len, const uint32_t* b, size_t b_len, uint32_t* out);
bool is_flag(const uint16_t* buffer, size_t length);