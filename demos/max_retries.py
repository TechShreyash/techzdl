# This script demonstrates how to configure the downloader to handle retries.
# The 'max_retries' parameter sets the maximum number of retry attempts for each chunk or file download.
# These settings are useful for handling unreliable network conditions or server issues.

import asyncio
from techzdl import TechZDL


async def main():
    downloader = TechZDL(
        url="https://link.testfile.org/bNYZFw",  # URL of the file to download
        max_retries=5,  # Maximum number of retries for each chunk/file download (default: 3)
    )
    await downloader.start()


asyncio.run(main())
