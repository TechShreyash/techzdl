# You can pass custom headers to the downloader by providing a dictionary to the 'custom_headers' parameter of the get_downloader method.
# This is useful when you need to include specific headers such as 'referer' or 'user-agent' to access the resource.

import asyncio
from techzdl import TechZDL


async def main():
    headers = {
        "referer": "https://testfile.org/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    }  # Custom headers for the downloader
    
    downloader = TechZDL(
        url="https://link.testfile.org/bNYZFw",
        custom_headers=headers,  # Pass custom headers
    )
    await downloader.start()


asyncio.run(main())
