# The 'single_threaded' parameter can be set to True to force the downloader to operate with a single connection.
# This is useful when you want to limit resource usage or when the server does not support multiple connections.
# Note that using a single-threaded approach may affect download speed, especially for large files.
# The single-threaded mode is automatically enabled when the 'workers' parameter is set to 1 or when the server does not support range requests.

import asyncio
from techzdl import TechZDL


async def main():
    downloader = TechZDL(
        url="https://link.testfile.org/bNYZFw",  # URL of the file to download
        single_threaded=True,  # Enable single-threaded mode
    )
    await downloader.start()


asyncio.run(main())
