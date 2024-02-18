#include <stdio.h>
#include <stdlib.h>

typedef float num;

num magnitude(num real, num imag) {
    return real * real + imag * imag;
}

num squared_re(num real, num imag) {
    return real * real - imag * imag;
}

num squared_im(num real, num imag) {
    return 2 * real * imag;
}

typedef struct args_t {
    size_t width;
    size_t height;
    size_t max_iterations;
    size_t color;
    num min_re;
    num max_re;
    num min_im;
    num max_im;
} args_t;

#define AE "\033["
const char* BCOLORS[16] = {
    AE "40m", AE "41m", AE "42m", AE "43m", AE "44m", AE "45m", AE "46m", AE "47m", AE "100m", AE "101m", AE "102m", AE "103m", AE "104m", AE "105m", AE "106m", AE "107m"
};
const char* FCOLORS[16] = {
    AE "30m", AE "31m", AE "32m", AE "33m", AE "34m", AE "35m", AE "36m", AE "37m", AE "90m", AE "91m", AE "92m", AE "93m", AE "94m", AE "95m", AE "96m", AE "97m"
};
const char* CLEAR_COLOR = AE "0m";

void mandelbrot(args_t args) {
    size_t size = args.width * args.height;
    num* lattice_re = calloc(size, sizeof(num));
    num* lattice_im = calloc(size, sizeof(num));
    num* c_re = calloc(size, sizeof(num));
    num* c_im = calloc(size, sizeof(num));
    // An array of unsigned ints
    size_t* iter_to_diverge = calloc(size, sizeof(size_t));

    // y is imaginary, x is real
    for (size_t y = 0; y < args.height; y++) {
        for (size_t x = 0; x < args.width; x++) {
            c_re[x + y * args.width] = (args.max_re - args.min_re) * x / (args.width - 1) + args.min_re;
            c_im[x + y * args.width] = (args.max_im - args.min_im) * y / (args.height - 1) + args.min_im;
        }
    }

    size_t iteration = 0;
    while (iteration < args.max_iterations) {
        for (size_t i = 0; i < size; i++) {
            num new_re = squared_re(lattice_re[i], lattice_im[i]) + c_re[i];
            num new_im = squared_im(lattice_re[i], lattice_im[i]) + c_im[i];
            lattice_re[i] = new_re;
            lattice_im[i] = new_im;
            if (magnitude(new_re, new_im) >= 2 * 2 && iter_to_diverge[i] == 0) {
                iter_to_diverge[i] = iteration;
            }
        }
        iteration++;
    }

    for (size_t y = 0; y < args.height; y++) {
        for (size_t x = 0; x < args.width; x++) {
            num r = lattice_re[x + y * args.width];
            num m = lattice_im[x + y * args.width];
            // Test if the value at the given point diverged
            if (magnitude(r, m) < 2 * 2) {
                if (args.color) {
                    // TODO: render higher resolution with braille chars
                    printf("%s█%s", FCOLORS[0], CLEAR_COLOR);
                } else {
                    printf("█");
                }
            } else {
                if (args.color) {
                    size_t i = iter_to_diverge[x + y * args.width] % 16;
                    // printf("%s%lx%s", BCOLORS[i], i, CLEAR_COLOR);
                    printf("%s%s %s", FCOLORS[(i + 2) % 16], BCOLORS[i], CLEAR_COLOR);
                } else {
                    printf("▒");
                }
            }
                //printf("%10.5f+%10.5fi  |c|=%10.5f\n", r, m, magnitude(r, m));
        }
        puts("");
    }
    
    free(lattice_re);
    free(lattice_im);
    free(c_re);
    free(c_im);
    free(iter_to_diverge);
}

int main(int argc, char* argv[]) {
    args_t args = {
        .width = 81,
        .height = 41,
        .max_iterations = 1063,
        .color = 1,
        .min_re = -2,
        .max_re = 0.5,
        .min_im = -1,
        .max_im = 1,
        // .min_re = -2 / 2,
        // .max_re = 0.5 / 2,
        // .min_im = -1,
        // .max_im = 0,
   };
    if (argc >= 3) args.width = strtol(argv[1], NULL, 0);
    if (argc >= 3) args.height = strtol(argv[2], NULL, 0);
    if (argc >= 4) args.max_iterations = strtol(argv[3], NULL, 0);
    mandelbrot(args);
    return 0;
}
