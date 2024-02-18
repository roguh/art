#!/bin/sh
COMPILER="${COMPILER:-tcc}"

# $1  - input .c file
# -o  - Output filename
# -W  - Turn on various types of warnings

set -x
if [ "$COMPILER" = "gcc" ]; then
    # -Oz - Optimize for code size
    # -g  - Debug symbols
    # -fsanitize... - Show lots of nice colorful info when stack smashing is detected
    gcc "${1}" -o "${1%.c}.bin" -Wall -Wpedantic -Oz -g -fsanitize=address
else
    tcc "${1}" -o "${1%.c}.bin" -Wall -Wpedantic -Oz -g
fi
