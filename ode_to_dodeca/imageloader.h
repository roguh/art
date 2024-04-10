#include "stdlib.h"

typedef struct Image {
    size_t width;
    size_t height;
    unsigned char* pixels;
} Image;

int loadBMP(const char* filename, Image* image);
