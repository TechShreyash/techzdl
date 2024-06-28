# This includes starting the downloader in the background and stopping it after a specific duration.

import asyncio
from techzdl import TechZDL


async def main():
    downloader = TechZDL(url="https://mp4-download.com/8k-5-MP4")

    # Start the downloader in the background
    await downloader.start(in_background=True)

    # Wait for 20 seconds
    await asyncio.sleep(20)

    # Stop the downloader
    await downloader.stop()


asyncio.run(main())
