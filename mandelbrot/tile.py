#!/usr/bin/env python3
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--map-fname", "-m", required=True)
parser.add_argument("--src-fname", "-s", required=True)
parser.add_argument("--replace", "-r", default="▒")
parser.add_argument("--new-char", "-w", type=str, default=None)
parser.add_argument("--step", type=int, default=1)

def main():
    args = parser.parse_args()
    with open(args.map_fname) as mfile, open(args.src_fname) as sfile:
        mapcontents = mfile.read()
        source = sfile.read().replace('\n', '\\n')
        out = []
        i = 0
        replace_chars = 0
        for char in mapcontents:
            if char in args.replace:
                if replace_chars % args.step == 0 and i < len(source):
                    out.append(source[i])
                    i += 1
                else:
                    out.append(args.new_char or char)
                replace_chars += 1
            else:
                out.append(char)
        print(''.join(out))

if __name__ == "__main__":
    main()
