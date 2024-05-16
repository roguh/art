#!/usr/bin/env python3
"""Draw geometric art based on heptagons (7-sided polygons) in 
2D Euclidean space using Python's Turtle module.

Recursive, overlapping tiling pattern with an organic appearance at higher recursion depths.

There would be no overlapping in Minkowski or Hyperbolic space :)

FELINA@FELINA.ART
"""
import argparse
from collections import defaultdict
import json
import pprint
import random
import sys
import time
from typing import Callable, Literal
import zipfile

try:
    import tqdm
except ImportError:
    tqdm = None

try:
    import turtle
except ImportError as exc:
    print(
        """Try installing the tk library with:
    sudo pacman -S tk
    sudo apt install tk
    sudo dnf install tk
"""
    )
    raise exc

CHILD_SIZING_ALGORITHMS: dict[str, Callable[[float, int], float]] = {
    "id": lambda s, _: s,
    "p67": lambda s, _: s ** (6 / 7),
    "p97": lambda s, _: s ** (9 / 7),
    "m57": lambda s, _: s * 5 / 7,
    "m37": lambda s, _: s * 3 / 7,  # VERY NICE alignment
    "1m37": lambda s, _: s * 3 / 7 if int(s) == s else s,  # VERY NICE alignment
    "Mm37": lambda s, _: s * 3 / 7 if s > 20 else s,  # VERY NICE alignment
    "m97": lambda s, _: s * 9 / 7,
    "m117": lambda s, _: s * 11 / 7,
    "m57_97": lambda s, l: s * (7 + (2 * (-1) ** l)) / 7,
    "m37_117": lambda s, l: s * (7 + (4 * (-1) ** l)) / 7,
    "m37_77": lambda s, l: s * (5 + (4 * (-1) ** l)) / 7,
    "m57_77": lambda s, l: s * (6 + (1 * (-1) ** l)) / 7,
}

COLOR_CHOICES = []
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--filename",
    type=str,
    default="heptagon_tile_euclidean_TIME_ARGS.eps",
    help="Screenshot name (TIME and ARGS are templated).",
)
parser.add_argument(
    "--levels", type=int, required=True, help="Maximum recursion depth."
)
parser.add_argument("--size", type=int, default=50, help="Side length.")
color_args = parser.add_mutually_exclusive_group(required=True)
parser.add_argument(
    "--childsizing",
    choices=CHILD_SIZING_ALGORITHMS.keys(),
    default="id",
    help="How to determine side length.",
)
color_args.add_argument(
    "--colors", help="REQUIRED or use --list-colors to print available."
)
color_args.add_argument("--list-colors", action="store_true", help="Print all themes.")
parser.add_argument(
    "--reverse-colors", action="store_true", help="Reverse the theme's sequence."
)
parser.add_argument(
    "--light-mode",
    action="store_true",
    help="Light background color. Note background color is not saved to screenshots.",
)
parser.add_argument(
    "--skip2",
    action="store_true",
    help="Skip drawing 2 edges in every septagon. Results in interesting shapes and faster rendering.",
)
parser.add_argument("--random-angle", action="store_true")
parser.add_argument("--quit", action="store_true")
parser.add_argument("--write", action="store_true")

STATS = {"SIZES": {}, "TOTAL": 0, "SIDES": 0, "TOTAL_PER": defaultdict(lambda: 0)}
guy: turtle.Turtle | None = None


# Example: ['YlGnBu']['9']
RawBrewerDictType = dict[str, dict[str, list[str]]]
ColorType = tuple[int, int, int]
BrewerSubThemeType = Literal["3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
BrewerDictType = dict[str, dict[BrewerSubThemeType, list[ColorType]]]
# 3456789


def load_themes(filename: str = "colorbrewer_rgb_3int.json.zip") -> BrewerDictType:
    """Parse colorbrewer.json file with accurate type hints."""
    with zipfile.ZipFile(filename) as zf:
        data: RawBrewerDictType = json.loads(zf.read(name="colorbrewer_rgb_3int.json"))
    return data


def print_side_number(side: int, color: ColorType, font_size: int = 13):
    """Label each of the 7 side labels in Roman numerals."""
    assert guy, "Turtle not initialized?"
    r, g, b = color
    label = str(side)
    label = "I II III IV V VI VII".split()[side % 7]
    align = "left" if side < 3 or side == 5 else "right"
    if side == 4:
        align = "center"
    guy.color((r, g, b))
    guy.write(label, align=align, font=("Mono", font_size - 1, "bold"))
    guy.color((255 - r, 255 - g, 255 - b))
    guy.write(label, align=align, font=("Mono", font_size, "normal"))
    guy.color(color)


BrewerPuRd9 = [
    (247, 244, 249),
    (231, 225, 239),
    (212, 185, 218),
    (201, 148, 199),
    (223, 101, 176),
    (231, 41, 138),
    (206, 18, 86),
    (152, 0, 67),
    (103, 0, 31),
]
BrewerPuRd9.reverse()
OriginalColors = [(255, 0, 0), (255, 196, 0), (196, 48, 0), (255, 96, 0)]


# wow:
# levels=3,2 size=[(10,20,30), 100, 100, 100, ...]
def heptagons(
    size: float,
    colors: list[ColorType],
    direction: float = 1,
    levels: int = 0,
    max_levels: int = 0,
    progress_bar=None,
    root: bool = True,
    parent_side: int = 0,
    writing: bool = False,
    childsizing: Callable[[float, int], float] = lambda x, _: x,
    args=None,
) -> tuple[int, int]:
    """Draw a recursive, overlapping heptagon tile pattern."""
    assert guy, "Turtle not initialized?"

    # Draw as fast as possible
    guy.speed("fastest")
    turtle.delay(0)
    turtle.colormode(255)

    if root:
        # Center
        guy.penup()
        guy.setpos(-size / 2, size)
        guy.pendown()

    mmax_x, mmax_y = 0, 0
    STATS["SIZES"][levels] = size
    STATS["TOTAL"] += 1
    STATS["TOTAL_PER"][levels] += 1
    # for side in range(5): NOOOOOO stop at 6, not limit
    for side in range(7):
        STATS["SIDES"] += 1
        # This helps a lot with limiting recursion, closer to the hyperbolic tiling too
        is_outer = side not in [0, 1, 6]

        child_size = childsizing(size, levels)

        (r, g, b) = colors[levels % len(colors)]
        b = (b + parent_side * 80) % 128
        if args and args.skip2:
            if side in [3, 6]:
                guy.penup()
            else:
                guy.pendown()
        guy.color((r, g, b))

        pensize = levels * 3 + 1
        guy.pensize(pensize)
        offset = 0
        if child_size < size:
            # Draw first part 1 side
            # Child line is in the middle of this side
            offset = max(0, (size - child_size) / 2)
            if offset > 0:
                guy.forward(offset)
        elif child_size > size:
            # Child side length is larger than parent side length
            offset = child_size / 2 - size / 2
            pendown = guy.pen()["pendown"]
            guy.pen(pendown=False)
            guy.backward(offset)
            guy.pen(pendown=pendown)

        # TODO NEW_SHAPE.eps
        # turn right(dir*360/7)
        # after going forward(size-childsize)/2 guy.right(direction * 360 / 7)

        if levels > 0 and (is_outer or root):
            # Draw child heptagon
            max_x, max_y = heptagons(
                child_size,
                colors=colors,
                direction=-direction,
                levels=levels - 1,
                max_levels=max_levels,
                progress_bar=progress_bar,
                root=False,
                parent_side=side,
                childsizing=childsizing,
                args=args,
            )

            # Find max x, y the turtle reached
            mmax_x = max(max_x, mmax_x)
            mmax_y = max(max_y, mmax_y)

        # Draw first part 1 side
        guy.color((r, g, b))

        # Draw number
        if root and writing:
            print_side_number(side, (r, g, b))

        guy.pensize(pensize)

        if child_size <= size:
            guy.forward(size - offset)
        elif child_size > size:
            pendown = guy.pen()["pendown"]
            guy.pen(pendown=False)
            guy.forward(offset)
            guy.pen(pendown=pendown)
            guy.forward(size)

        angle = direction * 360 / 7
        if args and args.random_angle:
            angle += 0.5 * (random.random() - 0.5)
        guy.right(angle)

        # Find max x, y the turtle reached
        x, y = guy.pos()
        mmax_x = max(int(x), mmax_x)
        mmax_y = max(int(y), mmax_y)

    if progress_bar:
        progress_bar.update(1)

    if root:
        # Show turtle on top right corner of drawing
        guy.penup()
        guy.color("green")
        guy.setpos(mmax_x + 20, mmax_y + 20)
    return mmax_x, mmax_y


def main(test_args=None):
    """Parse command line args and draw art, then save as a vector graphics EPS file."""
    start_time = time.time()

    args = parser.parse_args(test_args)
    levels = args.levels
    expected_count = sum(7 * 4**n for n in range(levels))
    arg_summary = f"{levels}_{args.size}_{args.childsizing}_{args.colors}"

    color_levels: BrewerSubThemeType = str(max(3, min(10, levels)))
    themes = load_themes()
    for theme in themes:
        COLOR_CHOICES.append(theme)
    if (
        args.list_colors
        or args.colors not in themes
        or color_levels not in themes[args.colors]
    ):
        print(
            f"Known colors are: {'\n'.join(themes.keys())}\nLevels generally 3 to 10 or 3 to 12"
        )
        sys.exit(0xFF)

    turtle.colormode(255)
    if args.light_mode:
        turtle.bgcolor((235, 235, 255))
    else:
        turtle.bgcolor((16, 16, 48))

    global guy
    guy = turtle.Turtle()
    guy.getscreen().title(arg_summary)
    guy.shape("turtle")
    guy.shapesize(2, 2)

    algo = CHILD_SIZING_ALGORITHMS[args.childsizing]
    print(
        "arguments:",
        arg_summary,
        "size sequence:",
        args.size,
        algo(args.size, levels),
        algo(algo(args.size, levels), levels - 1),
        "expected total shapes:",
        expected_count,
    )

    # TODO: --start-color --end-color --theme (Brewer custom, reverse, etc)
    # TODO: more child sizing
    # TODO: Minkowski metric child sizing for a seamless tiling (HOW????????????????????????????????????????)
    filename = args.filename
    filename = filename.replace("TIME", str(int(time.time())))
    filename = filename.replace("ARGS", arg_summary)

    colors = themes[args.colors][color_levels]
    if args.reverse_colors:
        colors.reverse()
    if args and args.colors:
        colors.insert(levels, (0, 0, 0))

    ok = False
    progress_bar = None
    if tqdm:
        # The root heptagon builds 7 heptagons around it (factor of 7)
        # Each heptagon has 4 children on its outer edges (powers of 4)
        progress_bar = tqdm.tqdm(total=expected_count)

    try:
        heptagons(
            args.size,
            colors=colors,
            levels=levels,
            max_levels=levels,
            progress_bar=progress_bar,
            writing=args.write,
            childsizing=algo,
            args=args,
        )
        ok = True
    except (KeyboardInterrupt, EOFError):
        print("bye")
    finally:
        print("saving output to vector graphics file:", filename)
        guy.getscreen().getcanvas().postscript(file=filename)
        print("seconds elapsed:", time.time() - start_time)
        pprint.pprint(STATS)
        if progress_bar:
            progress_bar.close()
    if ok:
        print("FIN")
        if args.quit:
            print("shutting down")
        else:
            turtle.done()


if __name__ == "__main__":
    main()
