from __future__ import annotations

import os
from functools import lru_cache
from typing import Iterable

from constants import FRAMES_PATH


@lru_cache(maxsize=None)
def exists(path: str) -> bool:
    return os.path.isfile(f"{FRAMES_PATH}/{path}.png")


def first(paths: Iterable[str]) -> str | None:
    return next((path for path in paths if exists(path)), None)


def find_slug(roots: Iterable[str], slugs: Iterable[str]) -> str | None:
    """The first `{root}/{slug}` that exists. Slugs are tried in order, each across every root."""
    roots = list(roots)
    for slug in slugs:
        found = first(f"{root}/{slug}" for root in roots)
        if found:
            return found
    return None


def find_root_first(roots: Iterable[str], slugs: Iterable[str]) -> str | None:
    """The first `{root}/{slug}` that exists. Roots are tried in order, each across every slug."""
    return first(f"{root}/{slug}" for root in roots for slug in slugs)


def find_mask(mask_dir: str, name: str) -> str | None:
    return first([f"{mask_dir}/{name}"])
