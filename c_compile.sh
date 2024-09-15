#!/bin/sh
# gcc or tcc
CC="${CC:-gcc}"

# $1  - input .c file
# -o  - Output filename
# -W  - Turn on various types of warnings

set -x
if [ "$CC" = "gcc" ]; then
    # -Oz - Optimize for code size
    # -g  - Debug symbols
    # -fsanitize... - Show lots of nice colorful info when stack smashing is detected
    gcc $CCARGS "${1}" -o "${1%.c}.bin" -Wall -Wpedantic -Oz -g -fsanitize=address
elif [ "$CC" = "gcc-fast" ]; then
    # -Oz - Optimize for code size
    # -g  - Debug symbols
    # -fsanitize... - Show lots of nice colorful info when stack smashing is detected
    gcc $CCARGS "${1}" -o "${1%.c}.bin" -Wall -Wpedantic -O2
elif [ "$CC" = "tcc" ]; then
    tcc $CCARGS "${1}" -o "${1%.c}.bin" -Wall -Wpedantic -Oz -g
fi
