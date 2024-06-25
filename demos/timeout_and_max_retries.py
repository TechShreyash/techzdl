# This script demonstrates how to configure the downloader to handle timeouts and retries.
# The 'timeout' parameter sets the maximum time (in seconds) to wait for a server response.
# The 'max_retries' parameter sets the maximum number of retry attempts for each chunk or file download.
# These settings are useful for handling unreliable network conditions or server issues.

import asyncio
from techzdl.api import TechZDL


async def main():
    techzdl = TechZDL()

    downloader = techzdl.get_downloader(
        url="https://link.testfile.org/bNYZFw",  # URL of the file to download
        timeout=30,  # Timeout in seconds for each request (default: 60 seconds)
        max_retries=5,  # Maximum number of retries for each chunk/file download (default: 3)
    )
    await downloader.start()


asyncio.run(main())
