# This is a demo script to illustrate how to use the TechZDL library for downloading files asynchronously.

import asyncio
from techzdl import TechZDL


async def main():
    # Initialize the downloader with a URL to download the file from
    downloader = TechZDL(url="https://link.testfile.org/bNYZFw")

    # Start the download process
    await downloader.start()


# Run the main function using asyncio
asyncio.run(main())
