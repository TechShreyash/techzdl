# You can set a fixed number of workers for the downloader by passing the 'workers' parameter to the get_downloader method.
# In this context, 'workers' refers to the number of parallel connections that will be used to download the file.
# This is useful when you want to limit the number of connections to the server.
# Note: Setting this parameter will disable dynamic worker adjustments based on download speed.
# For optimal performance, you can omit this parameter and allow the library to automatically determine the number of workers.

import asyncio
from techzdl import TechZDL


async def main():
    downloader = TechZDL(
        url="https://link.testfile.org/bNYZFw",
        workers=4,  # Fixed number of workers for the downloader
    )
    await downloader.start()


asyncio.run(main())
