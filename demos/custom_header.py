# You can pass custom headers to the downloader by providing a dictionary to the 'custom_headers' parameter of the get_downloader method.
# This is useful when you need to include specific headers such as 'referer' or 'user-agent' to access the resource.

import asyncio
from techzdl.api import TechZDL


async def main():
    techzdl = TechZDL()
    headers = {
        "referer": "https://testfile.org/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    }
    downloader = techzdl.get_downloader(
        url="https://link.testfile.org/bNYZFw",
        custom_headers=headers,  # Custom headers for the downloader
    )
    await downloader.start()


asyncio.run(main())
