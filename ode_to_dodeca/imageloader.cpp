#include "stdlib.h"
#include "imageloader.h"

int loadBMP(const char* filename, Image* image) {
    image->width = 256;
    image->height = 256;
    image->pixels = (unsigned char*)calloc(image->width * image->height, 3);
    for (int i = 0; i < 256 * 256; i++) {
        image->pixels[i * 3] = 255;
        image->pixels[i * 3 + 1] = 127;
    }
    return 0;
}
