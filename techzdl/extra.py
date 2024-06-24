import string
import random
import re
from pathlib import Path,PurePath
import asyncio
import re
import urllib.parse
import mimetypes
from urllib.parse import unquote_plus
from typing import Optional, Dict


def get_random_string(length: int) -> str:
    """
    Generate a random string of specified length using uppercase letters.

    Args:
        length (int): The length of the random string.

    Returns:
        str: A random string of specified length.
    """
    random_string = "".join(random.choices(string.ascii_uppercase, k=length))
    return random_string


def change_file_path_if_exist(original_path: Path) -> Path:
    """
    Change the file path if a file with the same name already exists.

    Args:
        original_path (Path): The original file path.

    Returns:
        Path: A new file path if the original exists, otherwise the original path.
    """
    num = 0
    path = original_path
    while path.exists():
        num += 1
        name = original_path.stem + f" ({num})"
        ext = original_path.suffix
        path = original_path.parent / f"{name}{ext}"
    return path


class AdjustableSemaphore:
    def __init__(self, initial_value: int):
        """
        Initialize an adjustable semaphore.

        Args:
            initial_value (int): The initial value of the semaphore.
        """
        self._value = initial_value
        self._condition = asyncio.Condition()

    async def acquire(self):
        """
        Acquire a semaphore, waiting if necessary until it becomes available.
        """
        async with self._condition:
            while self._value <= 0:
                await self._condition.wait()
            self._value -= 1

    async def release(self):
        """
        Release a semaphore, incrementing the internal counter and notifying waiters.
        """
        async with self._condition:
            self._value += 1
            self._condition.notify()

    async def set_limit(self, new_limit: int):
        """
        Set a new limit for the semaphore.

        Args:
            new_limit (int): The new limit for the semaphore.
        """
        async with self._condition:
            self._value += new_limit - self._value
            self._condition.notify_all()

def sanitize_filename(filename):
    """
    Replace invalid characters in filenames with an underscore.
    """
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def parse_content_disposition(content_disposition: str) -> Optional[str]:
    """
    Parse the Content-Disposition header to extract the filename.

    Args:
        content_disposition (str): The Content-Disposition header value.

    Returns:
        Optional[str]: The extracted filename, or None if not found.
    """
    print(content_disposition)
    parts = content_disposition.split(";")
    filename = None
    for part in parts:
        part = part.strip()
        if part.startswith("filename="):
            filename = part.split("=", 1)[1].strip(' "')
        elif part.startswith("filename*="):
            match = re.match(r"filename\*=(\S*)''(.*)", part)
            if match:
                encoding, value = match.groups()
                try:
                    filename = urllib.parse.unquote(value, encoding=encoding)
                except ValueError:
                    filename = None
    return filename


def get_filename(headers: Dict[str, str], url: str, id: str) -> str:
    """
    Determine the filename from HTTP headers, URL, or generate a default.

    Args:
        headers (Dict[str, str]): The HTTP response headers.
        url (str): The URL from which the file is being downloaded.
        id (str): A unique identifier to use as a fallback filename.

    Returns:
        str: The determined filename.
    """

    url = str(url)
    filename = None

    if headers.get("Content-Disposition"):
        filename = parse_content_disposition(headers["Content-Disposition"])

    if not filename:
        filename = unquote_plus(url.rstrip("/").split("/")[-1].strip(' "'))

    if not filename or "." not in filename:
        if headers.get("Content-Type"):
            extension = mimetypes.guess_extension(headers["Content-Type"])
            filename = f"{id}{extension or ''}".strip()
        else:
            filename = id

    filename= filename.strip().replace("/", "_")
    return PurePath(sanitize_filename(filename))
