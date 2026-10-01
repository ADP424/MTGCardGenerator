from utils import log


def error(message: str) -> None:
    log(f"ERROR: {message}")


def warning(message: str) -> None:
    log(f"WARNING: {message}")
