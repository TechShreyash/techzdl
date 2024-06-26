# This script demonstrates how to use the TechZDL package to fetch file information asynchronously.

import asyncio
from techzdl import TechZDL


async def main():
    downloader = TechZDL(url="https://link.testfile.org/bNYZFw")

    # Retrieve file information asynchronously
    file_info = await downloader.get_file_info()

    # Print the retrieved file information
    print(f"Filename: {file_info['filename']}")
    print(f"Total Size: {file_info['total_size']} bytes")


asyncio.run(main())
