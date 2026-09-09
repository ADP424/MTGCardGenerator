"""
Resize specific frame images (or whole directories of them) under images/frames/ to a given target
size, using Hamming resampling.

Usage:
    python tools/resize_frames.py --size 2010x2814 leveler/red.png
    python tools/resize_frames.py --size 2010x2814 leveler the_one_set/poker --apply
"""

import argparse
import os

from PIL import Image

FRAMES_PATH = "images/frames"


def parse_size(value: str) -> tuple[int, int]:
    """
    Parse a "WIDTHxHEIGHT" string into an (int, int) tuple, for use as an argparse type.
    """

    parts = value.lower().split("x")
    if len(parts) != 2 or not all(part.isdigit() for part in parts):
        raise argparse.ArgumentTypeError(f"Invalid size '{value}', expected WIDTHxHEIGHT (e.g. 2010x2814).")
    return (int(parts[0]), int(parts[1]))


def find_files_to_resize(paths: list[str], target_size: tuple[int, int]) -> list[tuple[str, tuple[int, int]]]:
    """
    Resolve a list of paths (relative to images/frames/, each a .png file or a directory) into every
    .png file under them that isn't already at target_size, as (filepath, current_size) tuples.
    """

    to_resize: list[tuple[str, tuple[int, int]]] = []
    seen: set[str] = set()

    for raw_path in paths:
        full_path = os.path.join(FRAMES_PATH, raw_path)

        if os.path.isfile(full_path):
            filepaths = [full_path]
        elif os.path.isdir(full_path):
            filepaths = []
            for root, _, files in os.walk(full_path):
                for filename in files:
                    if filename.lower().endswith(".png"):
                        filepaths.append(os.path.join(root, filename))
        else:
            raise SystemExit(f"No such file or directory: {full_path}")

        for filepath in filepaths:
            if filepath in seen:
                continue
            seen.add(filepath)
            with Image.open(filepath) as image:
                size = image.size
            if size != target_size:
                to_resize.append((filepath, size))

    return to_resize


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "paths",
        nargs="+",
        help="One or more .png files or directories to resize, relative to images/frames/.",
    )
    parser.add_argument(
        "--size",
        required=True,
        type=parse_size,
        help="Target size as WIDTHxHEIGHT (e.g. 2010x2814).",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually resize the files in place. Without this flag, only lists what would change.",
    )
    args = parser.parse_args()

    to_resize = find_files_to_resize(args.paths, args.size)
    if not to_resize:
        print(f"No files need resizing to {args.size[0]}x{args.size[1]}.")
        return

    for filepath, current_size in to_resize:
        print(f"{filepath}: {current_size} -> {args.size}")

    print(f"\n{len(to_resize)} file(s) would be resized.")

    if not args.apply:
        print("Dry run only - pass --apply to actually resize these files.")
        return

    print()
    for index, (filepath, current_size) in enumerate(to_resize, start=1):
        with Image.open(filepath) as image:
            resized = image.convert("RGBA").resize(args.size, resample=Image.Resampling.HAMMING)
            resized.save(filepath)
        print(f"[{index}/{len(to_resize)}] Resized {filepath}: {current_size} -> {args.size}")

    print(f"\nResized {len(to_resize)} file(s).")


if __name__ == "__main__":
    main()
