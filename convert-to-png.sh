#!/bin/sh
set -eo pipefail
set -x
INPUT="$1"
OUTPUT="${1%.*}.png"
BACKGROUND="#080810"
set -x
time convert -colorspace sRGB -density 300 "$INPUT" -background "$BACKGROUND" -flatten -units pixelsperinch -density 400 "$OUTPUT"
echo "$OUTPUT"
