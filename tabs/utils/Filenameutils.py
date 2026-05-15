


def txt2filename(txt: str) -> str:
    special_characters = [
        "@", "#", "$", "*", "&", "<", ">", "/", "\b", "|", "?", "CON", "PRN", "AUX", "NUL",
        "COM0", "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "LPT0",
        "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9", ":", "\"", "'"
    ]

    normal_string = txt
    for sc in special_characters:
        normal_string = normal_string.replace(sc, "")

    return normal_string


