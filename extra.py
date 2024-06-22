import string
import random
from pathlib import Path


def get_random_string(length: int) -> str:
    """
    Generate a random string of specified length using uppercase letters.

    Args:
        length (int): The length of the random string.

    Returns:
        str: A random string of specified length.
    """

    return "".join(random.choices(string.ascii_uppercase, k=length))


def change_file_path_if_exist(original_path: Path) -> Path:
    num = 0
    path = original_path
    while path.exists():
        num += 1
        name = original_path.stem + f" ({num})"
        ext = original_path.suffix
        path = original_path.parent / f"{name}{ext}"
    return path
