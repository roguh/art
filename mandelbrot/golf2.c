#define S 3321
int main(i, x, y, t) {
    // Size is width=81, height=41, total is S=3321
    float r, m, R[S] = {0}, M[S] = {0}, C[S], D[S];

    // y is imaginary, x is real
    for (i = 0; i < S; i++) {
        // The boundaries go from x=real=-2 to 0.5, y=imag=-1 to 1
        // x = i % width
        C[i] = 2.5 * (i % 81) / 80. - 2;
        // y = i / width
        D[i] = 2 * (i / 81) / 40. - 1;
    }

    t = 0;
    while (t++ < 1063) {
        for (i = 0; i < S; i++) {
            // Compute previous_latice**2 + c
            // c**2 = (r + im)**2 = r**2 - m**2 + 2irm
            r = R[i];
            m = M[i];
            R[i] = r * r - m * m + C[i];
            M[i] = 2 * r * m + D[i];
        }
    }

    for (i = 0; i < S; i++) {
        // Compute the magnitude of this point
        // |c|**2 = r**2 + m**2
        // If the magnitude is less than 4, the point did not diverge
        printf(R[i] * R[i] + M[i] * M[i] < 4 ? "█" : "▒");
        i % 81 == 80 && puts("");
    }
}
