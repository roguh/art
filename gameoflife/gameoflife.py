#!/usr/bin/env python3
"""The Game of Life."""
import abc
import argparse
import os
import random
import string
import subprocess
import sys
import time
from typing import Callable, Literal, Optional, TypedDict

# pylint: disable=missing-class-docstring, missing-function-docstring, invalid-name

Cell = bool
Row = list[bool]
Board = list[list[bool]]
Surface = Literal["sphere", "rectangle", "infinite", "torus", "?"]

LIVE = True
DEAD = False
L = LIVE
D = DEAD

LIVE_STR = "# "
DEAD_STR = "  "
LIVE_STR_PRETTY = "█▒"
DEAD_STR_PRETTY = "  "


class OutputArgs(TypedDict, total=False):
    source: str
    name: str
    delay: float
    start_delay: float
    pretty: bool
    narrow: bool
    color: str
    output: Literal["cli", "neopixel"]


def empty_row() -> Row:
    return []


surfaces: list[Surface] = ["sphere", "rectangle", "infinite", "torus", "?"]


def ix(row: Row, x: int, default=DEAD) -> Cell:
    return row[x] if 0 <= x < len(row) else default


def empty(width: int, height: int) -> Board:
    return [[DEAD for _ in range(width)] for _ in range(height)]


def glider(up: bool, left: bool) -> Board:
    out = [
        [D, L, D],
        [L, L, D],
        [L, D, L],
    ]
    if not up:
        out.reverse()
    if not left:
        for row in out:
            row.reverse()
    return out


def add(board: Board, other: Board, operator=bool.__or__) -> Board:
    new = []
    for y, row in enumerate(board):
        new_row = empty_row()
        other_row = other[y] if y < len(other) else empty_row()
        for x, cell in enumerate(row):
            new_row.append(operator(cell, ix(other_row, x)))
        new.append(new_row)
    return new


def shift(board: Board, y: int = 0, x: int = 0) -> Board:
    for _ in range(abs(y)):
        if y > 0:
            board.insert(0, [DEAD for _ in range(len(board[0]))])
        if y < 0:
            board.append([DEAD for _ in range(len(board[-1]))])
    for row in board:
        for _ in range(x):
            if x > 0:
                row.insert(0, DEAD)
            if x < 0:
                row.append(DEAD)
    return board


def neighbors(x: int, row: Row, prev_row: Row, next_row: Row, surface: Surface) -> int:
    """Count living neighbors diagonally, horizontally, and vertically."""
    if surface == "sphere":
        return [
            # Wrap around to end of row
            ix(row, x - 1, row[-1]),
            # Wrap around to beginning of row
            ix(row, x + 1, row[0]),
            # Next: wrap around diagonal if at beginning or end
            ix(next_row, x - 1, next_row[-1]),
            # This next_row is always a valid row, handled by the parent function
            ix(next_row, x),
            ix(next_row, x + 1, next_row[0]),
            # Previous: wrap around diagonal if at beginning or end
            ix(prev_row, x - 1, prev_row[-1]),
            # This prev_row is always a valid row, handled by the parent function
            ix(prev_row, x),
            ix(prev_row, x + 1, prev_row[0]),
        ].count(LIVE)
    return [
        ix(row, x - 1),
        ix(row, x + 1),
        ix(next_row, x - 1),
        ix(next_row, x),
        ix(next_row, x + 1),
        ix(prev_row, x - 1),
        ix(prev_row, x),
        ix(prev_row, x + 1),
    ].count(LIVE)


def update(board: Board, surface: Surface) -> Board:
    new_board = []
    prev_row = empty_row()
    if surface == "sphere":
        prev_row = board[-1]
    for y, row in enumerate(board):
        next_row = board[y + 1] if 0 <= y + 1 < len(board) else empty_row()
        if surface == "sphere" and y + 1 == len(board):
            next_row = board[0]
        new_row = empty_row()
        for x, cell in enumerate(row):
            neighbor_count = neighbors(x, row, prev_row, next_row, surface)
            # "normal" RULE B3/S23
            new_cell = LIVE if neighbor_count == 3 else cell if neighbor_count == 2 else DEAD
            # RULE B3/S12345
            # new_cell = LIVE if neighbor_count == 3 else cell if neighbor_count in [1, 2, 3, 4, 5] else DEAD
            new_row.append(new_cell)
        new_board.append(new_row)
        prev_row = row
    return new_board


def show(board: Board, alphabet: tuple[str, str] = (LIVE_STR, DEAD_STR), sep="") -> str:
    live, dead = alphabet
    return "\n".join(sep.join(live if cell else dead for cell in row) for row in board)


def parse(lines: list[str], live: str = "#@&" + string.ascii_uppercase) -> Board:
    output: Board = []
    for row in lines:
        row = row.strip()
        if len(row) == 0:
            continue
        output.append([LIVE if cell in live else DEAD for cell in row])
    assert len(output) > 0, f"empty board parsed:\n{lines}"
    assert all(len(row) > 0 for row in output), f"empty rows found:\n{lines}"
    return output


def pick_updater(source: str, surface: Surface) -> Callable[[Board], Board]:
    def command(board_str: str) -> list[str]:
        if source.endswith(".py"):
            return ["python3", source, board_str]
        if source.endswith(".bin"):
            return [source, board_str]
        return ["echo", "Unknown source"]

    def external(board: Board) -> Board:
        # ignore surface
        encoded_board = show(board, alphabet=("#", "."))
        output = subprocess.check_output(command(encoded_board)).decode("utf-8")
        return parse(output.split("\n"))

    def default(board: Board) -> Board:
        return update(board, surface=surface)

    if source.startswith("./variants"):
        print("Using external script", source)
        return external
    return default


class Display(abc.ABC):
    @abc.abstractmethod
    def display(self, board: Board, iteration: int, args: OutputArgs) -> None:
        pass


class NeoPixel(Display):
    width = 16
    height = 16
    color = (255, 0, 0)

    def __init__(self) -> None:
        # This 'board' refers to the circuitboard
        import board
        import neopixel

        # Raspberry Pi
        # Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18
        # NeoPixels must be connected to D10, D12, D18 or D21 to work.
        # D19 - must enable SPI interface, but this allows using neopixels without root permissions
        # D12 = GPIO18
        # D19 - GPIO10, MOSI, part of userspace SPI driver
        assert board.D10 == board.MOSI
        pin = board.D10
        # pixel order?
        self.pixels = neopixel.NeoPixel(pin, self.width * self.height, auto_write=False)
        self.pixels.brightness = 0.5
        print(f"Initialized {self.pixels.n} pixels, {self.width}x{self.height}")

    def __del__(self) -> None:
        self.pixels.deinit()
        print("Turned off neopixel display")

    def display(self, game_board: Board, iteration: int, args: OutputArgs) -> None:
        delay = args.get("delay")

        # Resize to fit the display
        reduced_board = add(empty(self.width, self.height), game_board)
        assert len(reduced_board) == self.height
        assert len(reduced_board[0]) == self.width

        i = 0
        for row in reduced_board:
            for cell in row:
                if cell:
                    self.pixels[i] = self.color
                else:
                    self.pixels[i] = (0, 0, 0)
                i += 1
        start_time = time.time()
        self.pixels.show()
        elapsed = time.time() - start_time
        if iteration % 10 == 1:
            print(f"Drew to screen in {elapsed} seconds")


class CLI(Display):
    current_color = 0
    clear = "\033[2J"
    to_top = "\033[H"
    black_on_white = "\x1b[1;30;47m"
    reset_color = "\x1b[0m"
    colors: list[tuple[str, str]] = [
        ("red", "\x1b[0;31m"),
        ("magenta", "\x1b[0;34m"),
        ("yellow", "\x1b[0;33m"),
        ("green", "\x1b[0;32m"),
        ("blue", "\x1b[0;35m"),
        ("cyan", "\x1b[0;36m"),
        ("white", "\x1b[0;37m"),
    ]
    colors_dict = dict(colors)

    def display(self, board: Board, iteration: int, args: OutputArgs) -> None:
        alphabet = (LIVE_STR, DEAD_STR)
        if args.get("pretty"):
            alphabet = (LIVE_STR_PRETTY, DEAD_STR_PRETTY)
        if args.get("narrow"):
            alphabet = (alphabet[0][0], alphabet[1][0])
        
        setcolor = args.get("color")

        if iteration > 1:
            if setcolor:
                print(CLI.reset_color, CLI.clear, end=CLI.to_top)
            time.sleep(args.get("delay", 1.0))

        # Display
        if setcolor and setcolor in CLI.colors_dict:
            print(CLI.colors_dict.get(setcolor), end="")
        if setcolor == "dynamic":
            live, dead = alphabet
            out = "\n".join(
                "".join(
                    CLI.colors[
                        (self.current_color // 5 + x // 3 + y // 6) % len(CLI.colors)
                    ][1]
                    + live
                    if cell
                    else dead
                    for x, cell in enumerate(row)
                )
                for y, row in enumerate(board)
            )
            print(out)
        else:
            print(show(board, alphabet))
        if all(not cell for row in board for cell in row):
            print("empty board")

        self.current_color += 1
        
        if setcolor:
            print(CLI.reset_color + CLI.black_on_white, end="")
        print(f"The Game of Life. {iteration} steps.", args.get("name", ""), args.get("source", ""))


def loop(
    board: Board,
    max_iterations: float = float("inf"),
    surface: Surface = surfaces[0],
    args: Optional[OutputArgs] = None,
) -> None:
    if not args:
        args = {}

    if args.get("output") == "neopixel":
        display = NeoPixel().display
    else:
        display = CLI().display

    iteration = 0
    if max_iterations == 0 or args.get("start_delay", 0) > 0:
        display(board, iteration, args)
        time.sleep(args.get("start_delay", 0))

    update_function = pick_updater(args.get("source", "unknown"), surface)

    while iteration < max_iterations:
        # Update
        board = update_function(board)

        iteration += 1
        display(board, iteration, args)


def make_init_board(args) -> Board:
    # Use terminal width to find size
    try:
        width = args.width or int(subprocess.check_output(["tput", "cols"]))
        height = args.height or int(subprocess.check_output(["tput", "lines"]))
        height -= 1
        if not args.narrow:
            width //= 2
    except:  # pylint: disable=bare-except
        width, height = 32, 32
        print("Unable to find terminal size with Linux tput")
    if args.empty_board:
        return empty(width, height)
    if args.file:
        with open(args.file, encoding="utf-8") as boardfile:
            init_board = parse(boardfile.readlines())
            if args.expand_to_size:
                return add(empty(width, height), init_board)
            return init_board
    if args.random_board:
        board = empty(width, height)
        for y in range(height):
            for x in range(width):
                board[y][x] = random.choice([LIVE, DEAD, DEAD])
        return board
    if args.glider_board:
        if width > height:
            width = height * (width // height)
        else:
            height = width * (height // width)
    top = 2
    offset = 8
    board = empty(width, height)
    direction = True
    for y in range(top, height, offset):
        board = add(
            board,
            shift(glider(up=direction, left=direction), x=width // 2, y=y),
        )
        direction = not direction
    return board


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--iterations", "-i", type=float, default=float("inf"))
    parser.add_argument("--delay", "-d", type=float, default=0.03)
    parser.add_argument("--start-delay", type=float, default=1)
    parser.add_argument(
        "--surface",
        "-s",
        default=surfaces[0],
        choices=surfaces,
        help="The shape of the universe.",
    )
    parser.add_argument(
        "--source",
        choices=["python", "./variants/golf.py"],
        default="python",
    )
    parser.add_argument("--name", default="")
    parser.add_argument("--pretty", "-p", action="store_true")
    parser.add_argument("--narrow", "-n", action="store_true")
    parser.add_argument("--color", "-c", default="off")
    parser.add_argument("--output", "-o", choices=["neopixel", "cli"])
    parser.add_argument(
        "--width",
        "-w",
        type=int,
        default=None,
        help="Minimum size of the board. "
        "The size of the terminal window may be used if this option not given.",
    )
    parser.add_argument(
        "--height",
        "-l",
        type=int,
        default=None,
        help="Minimum size of the board. "
        "The size of the terminal window may be used if this option not given.",
    )
    parser.add_argument("--expand-to-size", "-e", action="store_true")
    board_input = parser.add_mutually_exclusive_group(required=True)
    board_input.add_argument(
        "--file",
        "-f",
        help="Dead cells and live cells are represented by "
        f"the characters {DEAD_STR} and {LIVE_STR}",
    )
    board_input.add_argument("BOARD", nargs="?")
    board_input.add_argument("--empty-board", action="store_true")
    board_input.add_argument("--random-board", action="store_true")
    board_input.add_argument("--glider-board", action="store_true")

    args = parser.parse_args()

    init_board = make_init_board(args)

    output_args: OutputArgs = {
        "name": "gliders" if args.glider_board else "random" if args.random_board else os.path.basename(args.file),
        "source": args.source,
        "delay": float(args.delay),
        "start_delay": float(args.start_delay),
        "pretty": bool(args.pretty),
        "narrow": bool(args.narrow),
        "color": "dynamic" if args.color == "on" else args.color,
        "output": args.output,
    }
    try:
        loop(
            board=init_board,
            max_iterations=args.iterations,
            surface=args.surface,
            args=output_args,
        )
    except (EOFError, KeyboardInterrupt):
        return 1
    finally:
        if args.color:
            print(end=CLI.reset_color)
    return 0

if __name__ == "__main__":
    sys.exit(main())
