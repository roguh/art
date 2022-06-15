#!/usr/bin/env python3
# library: start breakpoint (to adjust a drawing when its done?)
# debug helpers, context managers
# 10k px render? render to png?
# async turtle or multithreaded turtle or your own library?
# vector graphics
import colorsys
import math
import random
import turtle
from pprint import pprint

length = 500
width = 1
mrt = turtle.Turtle()

fidelity = 20
debug_mode = False
labels = True

def prep():
    turtle.title(
        f"Making a parabola out of whitespace by drawing lines (the parabola is their envelope)"
    )
    
    mrt.shape("turtle")
    # mrt.shapesize(0.1, 0.1)
    mrt.color("white", "blue")
    mrt.width(width)
    turtle.bgcolor("black")
    
    # Draw as fast as possible
    mrt.speed("fastest")
    turtle.delay(0)


def shuffle(iterable):
    iterable = list(iterable)
    random.shuffle(iterable)
    return iterable


def color_at_index(i):
    # This goes from hue=1.0 to hue=0.0 to hue=1.0
    # return colorsys.hls_to_rgb(2 * abs(i - fidelity / 2) / fidelity, 0.5, 1)
    return colorsys.hls_to_rgb(0.4 + i / fidelity * 0.6, 0.5, 1)
    # return colorsys.hls_to_rgb(i / fidelity * 0.6, 0.5, 1)


"""
            # x1,0 to 0,y2=L/sin(D)

            # x = my + b
            # (x - b) / y = m

            # we know b=x-intercept
            # (x - x1) / y = m
            # (x2=0 - x1) / y2=ANGLE = m

            # 0,0 to 0,L

            # x = my + b
            # 0 = my - x + b

            # if we have a vertical line (at other==0)
            # then y = length
            # so the general form is A=-1 B=0 C=length

            x = i * length / fidelity
            subangle2 = other * (180 - angle) / fidelity
            x2 = other * length / fidelity
            A1 = m1 = math.sin(math.radians(subangle)) / x
            # 0
            if other == 0:
                A2 = -1
                B2 = 0
            else:
                A2 = m2 = math.sin(math.radians(subangle2)) / x2
                B2 = -1
            B1 = -1
            C1 = x
            # 0
            if other == 0:
                C2 = length
            else:
                C2 = x2
"""


def get_intersection(line1, line2):
    A1, B1, C1 = line1
    A2, B2, C2 = line2
    intersection_scale = A1 * B2 - A2 * B1
    intersection_x = (B1 * C2 - B2 * C1) / intersection_scale
    intersection_y = (C1 * A2 - C2 * A1) / intersection_scale
    return [intersection_x, intersection_y]


init_x, init_y = 0, 0


def position_of(angle, i):
    x, y = list(mrt.pos())
    return x - init_x, y - init_y


def get_max_intersection_dist(angle, i):
    return length, []
    # length/2 looks cool
    # This should be the length s.t. the line does not go past the last point where it intersects with another line
    # To find this, you must find all other lines it will intersect with
    # Find the lengths of these line segments
    # Pick the maximal length

    # BRUTE FORCE!!!!!!!!!!!!

    # we have the slope and the x-intercept for each line
    # x-intercept = lineindex * length / fidelity
    # x = ny + b2 where n=??? and b2=x-intercept
    # y = mx + b where m=tan(subangle)
    # y - b = mx
    # y/m - b/m = x
    # b/m = b2
    # n = 1/m

    # slope-intercept to general form
    # y=mx + b
    # 0 = mx - y + b
    # A=-1 B=m C=b
    max_dist = 0
    dists = []
    for other in range(fidelity + 1):
        if other == i:
            continue
        if i in [0, fidelity]:
            max_dist = length
            break
        # elif other == 0:
        #    dist = position / math.sin(math.radians(subangle))
        else:
            subangle = i * (180 - angle) / fidelity
            subangle2 = other * (180 - angle) / fidelity
            x, y = position_of(angle, i)
            dist = length
            # line1 = line_of(angle, subangle, i)
            # line2 = line_of(angle, subangle2, other)

            # intersection = get_intersection(line1, line2)

            # dist = ((x - intersection[0]) ** 2 + (y - intersection[1]) ** 2) ** 0.5
        dists.append((other, dist))
        if dist > length:
            continue
        max_dist = max(dist, max_dist)
    pprint(dists)
    return max_dist, dists


def petal_ish(angle=90.0, factor=1.0, outline=True, outline_color=None):
    """A parabola built using only lines."""
    global init_x, init_y
    init_x, init_y = list(mrt.pos())

    mrt.left(90)
    edges = []
    for i in range(fidelity + 1):
        mrt.color(color_at_index(i))

        subangle = i * (angle) / fidelity
        line_length = factor * length

        mrt.right(subangle)
        mrt.forward(line_length)
        edges.append(mrt.pos())
        if debug_mode:
            x, y = position_of(angle, i)
            mrt.write(f" {i}: {x:.1f} {y:.1f}  ", align="left")

        mrt.backward(line_length)
        if debug_mode:
            x, y = position_of(angle, i)
            mrt.write(f"  {x:.1f} {y:.1f}  ", align="right")

        mrt.left(subangle)
        if i < fidelity:
            mrt.forward(factor * length / fidelity)

    # Go back to initial position and heading
    mrt.up()
    mrt.backward(factor * length)
    mrt.right(90)
    mrt.down()

    if outline or outline_color:
        init_pos = mrt.pos()
        # Easiest way is to keep track of the points, sorry
        mrt.up()
        mrt.goto(edges[0])
        mrt.down()
        # TODO optimize, skip points if previous points are too close
        for i, p in enumerate(edges):
            if outline_color:
                mrt.color(outline_color)
            else:
                mrt.color(color_at_index(i))
            mrt.goto(p)
        mrt.up()
        mrt.goto(init_pos)
        mrt.down()
    mrt.color("white")


def scaleworld(x_scale, y_scale):
    x_scale *= length
    y_scale *= length
    turtle.setworldcoordinates(x_scale, x_scale, y_scale, y_scale)


def samples(angles):
    angles = list(angles)
    columns = math.ceil(len(angles) ** 0.5)
    scaleworld(-1 / 5, 1.5 * columns)
    print(columns, len(angles))
    for i, angle in enumerate(angles):
        # Jump to a clean part of the screen to draw the next shape
        mrt.up()
        mrt.setheading(0)
        mrt.setx(1.5 * length * (i % columns))
        mrt.sety(1.5 * length * (i // columns))

        if i % columns == 0:
            mrt.setx(0)
        mrt.down()

        if labels or debug_mode:
            mrt.color("grey")
            mrt.write(f"  {angle}  ", align="right")

        petal_ish(angle)


import sys

if any('help' in arg or '-h' in arg for arg in sys.argv):
    print(f"USAGE: {sys.argv[0]} [shayfleur|samples]")
    sys.exit(0)

shape = ''.join([a.replace('-', '').lower() for a in sys.argv[1:]])

if shape == 'shayfleur':
    # FLOWER:
    prep()
    scaleworld(-2, 2)
    for _ in range(8):
        petal_ish(145)
        mrt.left(45)

# samples([30, 45, 70, 90, 110, 135, 160, 170])
# samples([45, 90, 135])
# samples([5, 10, 15, 30, 45, 90, 120, 135, 145, 165])
# init_angle = 10
# samples(range(init_angle, 12 ** 2 + init_angle + 1, 3))

elif shape == 'samples':
    prep()
    init_angle = 10
    samples(shuffle(range(init_angle, 12 ** 2 + init_angle + 1, 3)))

else:
    print(f"Unknown shape {shape}")
    sys.exit(22)

# ./shay_flower__40_to_100_40deg.png
# scaleworld(-2, 2)
# N = 9
# M = 5
# for _ in range(M):
#     petal_ish(180 - 360 / N, outline=True)
#     fidelity = 20
#     petal_ish(360 / N, outline=True)
#     fidelity = 59
#     mrt.left(360 / M)

# ./shay_flower__40_to_100_40deg_single.png
# scaleworld(0, 2)
# N = 9
# M = 1
# turtle.bgcolor("white")
# mrt.width(3)
# for _ in range(M):
#     color_at_index = lambda _i: (0, 0, 0)
#     petal_ish(180 - 360 / N, outline=True)
#     fidelity = 20
#     color_at_index = lambda _i: (1, 0, 0)
#     petal_ish(360 / N, outline=True)
#     fidelity = 59
#     mrt.left(360 / M)

# scaleworld(-2, 2)
# N = 8
# M = 4
# for _ in range(M):
#     petal_ish(180 - 360 / N)
#     t = 0.15
#     mrt.left(360 / M * t)
#     petal_ish(360 / N)
#     mrt.left(360 / M * (1 - t))

# this needs something in the center...
# scaleworld(-2.5, 2.5)
# margin = length * 0.9
# N = 7
# for i in range(N):
#     mrt.up()
#     mrt.forward(margin)
#     mrt.down()
#     for j in range(4):
#         petal_ish(90)
#         mrt.up()
#         mrt.forward(length)
#         mrt.down()
#         mrt.left(90)
#     mrt.up()
#     mrt.backward(margin)
#     mrt.down()
#     mrt.left(360 / N)

# STUNNING7
# scaleworld(-2.5, 2.5)
# N = 7
# M = 3
# margin = length / 5
# for i in range(N):
#     mrt.up()
#     mrt.forward(margin)
#     mrt.down()
#     for j in range(M):
#         petal_ish(360 / M)
#         mrt.up()
#         mrt.forward(length)
#         mrt.down()
#         mrt.left(360 / M)
#     mrt.up()
#     mrt.backward(margin)
#     mrt.down()
#     mrt.left(360 / N)

# STUNNING8
# scaleworld(-2, 2)
# N = 8
# M = 3
# margin = length * 0.4
# for i in range(N):
#     mrt.up()
#     mrt.forward(margin)
#     mrt.down()
#     for j in range(M):
#         petal_ish(360 / M)
#         mrt.up()
#         mrt.forward(length)
#         mrt.down()
#         mrt.left(360 / M)
#     mrt.up()
#     mrt.backward(margin)
#     mrt.down()
#     mrt.left(360 / N)

# scaleworld(-2, 2)
# N = 3
# M = 4
# margin = length / 3
# for i in range(N):
#     mrt.up()
#     mrt.forward(margin)
#     mrt.down()
#     for j in range(M):
#         petal_ish(360 / M * 1.333333333333)
#         mrt.up()
#         mrt.forward(length)
#         mrt.down()
#         mrt.left(360 / M)
#     mrt.up()
#     mrt.backward(margin)
#     mrt.down()
#     mrt.left(360 / N)


mrt.up()
mrt.setpos(-length, -length)
mrt.color((0.2, 0.6, 0.4))
s = turtle.getscreen()
c = s.getcanvas()
c.postscript(file='output.eps')
turtle.done()
