#include <stdio.h>
#include <string.h>

const char tore_tang[] =
"Når han går, alle snur å ser på han\n"
"Ikkje løye det, så stygge som han er.\n"
"Han forstår, de kan'kje akkseptera han\n"
"Han har ingen fortid å se tilbake på.\n"
"Han seie det: At med døden får eg fred\n"
"Då ska ingen plaga meg igjen\n"
"Eg ska ha ro, der som eg og Jesus ska bo\n"
"Tore Tang, ein gammal mann,\n"
"Heile byen kjenne han,\n"
"Han som leve av gammalt brød og vann.\n"
"Kor han komme fra vett bare han,\n"
"Tore Tang.\n"
"År har gått siden Tore Tang var spelemann,\n"
"Det er den einaste jobben han har hatt.\n"
"Når Tang er død, går arven til guitaren hans,\n"
"Det er den einaste vennen han har hatt.\n"
"Han vente på den dagen han ska få, tror han\n"
"Egen hybelleilighet.\n"
"Kor tid det blir, det er det endå ingen som vett.\n"
"Tore Tang, ein gammal mann,\n"
"Heile byen kjenne han,\n"
"Han som leve av gammalt brød og vann.\n"
"Kor han komme fra vett bare han,\n"
"Tore Tang.\n"
"Når han går, alle snur å ser på han,\n"
"Ikkje løye det, så stygge som han er.\n"
"Han forstår, de kan'kje akkseptera han,\n"
"Har ingen fortid å se tilbake på.\n"
"Han seie det: At med døden får eg fred\n"
"Då ska ingen plaga meg igjen\n"
"Eg ska ha ro, der som eg og Jesus ska bo\n"
"Tore Tang, ein gammal mann,\n"
"Heile byen kjenne han,\n"
"Han som leve av gammalt brød og vann.\n"
"Kor han komme fra vett bare han,\n"
"Tore Tang.\n"
"Tore Tang, ein gammal mann.\n"
"Heile byen kjenne han,\n"
"Han som leve av gammalt brød og vann.\n"
"Kor han komme fra vett bare han,\n"
"Tore Tang.\n"
"Tore Tang, ein gammal mann.\n"
"Heile byen kjenne han,\n"
"Han som leve av gammalt brød og vann.\n"
"Kor han komme fra vett bare han,\n"
"Tore Tang.\n"
"Tore Tang, ein gammal mann.\n"
"Heile byen kjenne han,\n"
"Han som leve av gammalt brød og vann.\n"
"Kor han komme fra vett bare han,\n"
"Tore Tang.\n"
"Tore Tang, ein gammal mann.\n"
"Heile byen kjenne han,\n"
"Han som leve av gammalt brød og vann.\n"
"Kor han komme fra vett bare han,\n"
"Tore Tang.\n";

unsigned char d4[] = {
    0x79, 0x79, 0x64, 0x4c, 0x40, 0x7, 0x40, 0x68, 0x6, 0x68, 0x5b, 0x7, 0x41, 0x4, 0x68, 0x45, 0x4, 0x41, 0x4, 0x45, 0x44, 0x6, 0x59, 0x50, 0x4a
};

int main() {
    char x7[128];
    char z9[64];

    for (int i = 0; i < sizeof(d4); i++) {
        z9[i] = d4[i] ^ 0x37;
    }

    z9[sizeof(d4)] = '\0';

    printf("enter flag: ");
    scanf("%127s", x7);

    if (strcmp(x7, z9) == 0) {
        printf("correct!\n");
    } else {
        printf("wrong flag, try again.\n");
    }

    return 0;
}
