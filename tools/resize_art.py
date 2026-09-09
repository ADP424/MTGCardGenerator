"""
Upscale 1500x2100 (and 2100x1500 landscape) art images under images/art/ to the current
2010x2814 / 2814x2010 canvas size, using Hamming resampling (my favorite).

Usage:
    python tools/resize_art.py                      # dry run, lists files
    python tools/resize_art.py --apply              # actually resize
    python tools/resize_art.py --dir "The One Set"  # only that subdirectory
"""

import argparse
import os

from PIL import Image

ART_PATH = "images/art"

# (source size) -> (target size)
RESIZE_TARGETS = {
    (1500, 2100): (2010, 2814),
    (2100, 1500): (2814, 2010),
}


def find_files_to_resize(subdir: str = None) -> list[tuple[str, tuple[int, int], tuple[int, int]]]:
    """
    Return every art file whose size matches one of RESIZE_TARGETS, as
    (filepath, current_size, target_size) tuples.

    Parameters
    ----------
    subdir: str, optional
        Only look under this subdirectory of images/art/, instead of all of it.
    """

    search_root = os.path.join(ART_PATH, subdir) if subdir else ART_PATH

    to_resize = []
    for root, _dirs, files in os.walk(search_root):
        for filename in files:
            if not filename.lower().endswith(".png"):
                continue
            filepath = os.path.join(root, filename)
            with Image.open(filepath) as image:
                size = image.size
            target = RESIZE_TARGETS.get(size)
            if target is not None:
                to_resize.append((filepath, size, target))
    return to_resize


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually resize the files in place. Without this flag, only lists what would change.",
    )
    parser.add_argument(
        "--dir",
        default=None,
        help="Only resize art under this subdirectory of images/art/ (e.g. 'The One Set'). "
        "Defaults to all of images/art/.",
    )
    args = parser.parse_args()

    if args.dir and not os.path.isdir(os.path.join(ART_PATH, args.dir)):
        parser.error(f"No such directory: {os.path.join(ART_PATH, args.dir)}")

    to_resize = find_files_to_resize(args.dir)
    if not to_resize:
        print("No art files need resizing.")
        return

    for filepath, current_size, target_size in to_resize:
        print(f"{filepath}: {current_size} -> {target_size}")

    print(f"\n{len(to_resize)} file(s) would be resized.")

    if not args.apply:
        print("Dry run only - pass --apply to actually resize these files.")
        return

    print()
    for index, (filepath, current_size, target_size) in enumerate(to_resize, start=1):
        with Image.open(filepath) as image:
            resized = image.convert("RGBA").resize(target_size, resample=Image.Resampling.HAMMING)
            resized.save(filepath)
        print(f"[{index}/{len(to_resize)}] Resized {filepath}: {current_size} -> {target_size}")

    print(f"\nResized {len(to_resize)} file(s).")


if __name__ == "__main__":
    main()
