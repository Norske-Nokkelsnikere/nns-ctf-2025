#include "dsp.h"
#include <stdint.h>
#include <stdio.h>

uint16_t flag_i16[] = {78, 78, 83, 123, 116, 104, 49, 53, 95, 102, 108, 52, 103, 95, 49, 115, 95, 99, 48, 110, 118, 111, 49, 117, 116, 51, 100, 125};
uint16_t not_flag[] = {78, 78, 83, 123, 116, 104, 49, 53, 95, 102, 108, 52, 101, 95, 49, 115, 95, 99, 48, 110, 118, 111, 49, 117, 116, 51, 100, 125};

int main()
{
    printf("Is flag? %d\n", is_flag(flag_i16, sizeof(flag_i16) / 2));
    printf("Is flag? %d\n", is_flag(not_flag, sizeof(flag_i16) / 2));
}
