#!/bin/sh
set -eo pipefail
set -x
BACKGROUND="#080810"
time convert -colorspace sRGB -density 300 "$1" -background "$BACKGROUND" -flatten -units pixelsperinch -density 400 "$1.png"
viewnior "$1.png"
