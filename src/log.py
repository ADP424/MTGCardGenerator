indent = 0


def increase_log_indent(increment: int = 1):
    global indent
    indent += increment


def decrease_log_indent(increment: int = 1):
    global indent
    indent -= increment


def reset_log():
    with open("log.txt", "w", encoding="utf8") as log_file:
        log_file.write("")


def log(message: str = "", do_print=True):
    output = f"{"\t" * indent}{message}"
    with open("log.txt", "a", encoding="utf8") as log_file:
        log_file.write(f"{output}\n")
    if do_print:
        print(output)
