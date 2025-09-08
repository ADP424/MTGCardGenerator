def reset_log():
    with open("log.txt", "w", encoding="utf8") as log_file:
        log_file.write("")


def log(message: str, do_print=True):
    with open("log.txt", "a", encoding="utf8") as log_file:
        log_file.write(f"{message}\n")
    if do_print:
        print(message)
