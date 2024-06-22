import re
import urllib.parse
import mimetypes
from urllib.parse import unquote_plus
from typing import Optional, Dict


def parse_content_disposition(content_disposition: str) -> Optional[str]:
    """
    Parse the Content-Disposition header to extract the filename.

    Args:
        content_disposition (str): The Content-Disposition header value.

    Returns:
        Optional[str]: The extracted filename, or None if not found.
    """
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

    return filename.strip()
