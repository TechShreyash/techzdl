# This script demonstrates how to use the TechZDL package to fetch file information asynchronously.

import asyncio
from techzdl.api import TechZDL


async def main():
    techzdl = TechZDL()

    downloader = techzdl.get_downloader(url="https://link.testfile.org/bNYZFw")

    # Retrieve file information asynchronously
    file_info = await downloader.get_file_info()

    # Print the retrieved file information
    print(f"Filename: {file_info['filename']}")
    print(f"Total Size: {file_info['total_size']} bytes")


asyncio.run(main())
