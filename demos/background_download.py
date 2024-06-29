# This includes starting the downloader in the background, performing other tasks, and waiting for the download to finish before showing a message.

import asyncio
from techzdl import TechZDL


async def main():
    downloader = TechZDL(url="https://link.testfile.org/bNYZFw")

    # Start the download process in the background
    await downloader.start(in_background=True)

    # Perform other tasks here, run your other code

    # For this demo, let's wait until the download starts, then show a message when it's finished

    await asyncio.sleep(5)  # A sleep timeout to let the download start first

    # Check if the download is running
    while downloader.is_running:
        await asyncio.sleep(1)

    # After the download is finished

    if downloader.download_success:
        print("Download Successful")
    else:
        print("Download Failed")
        raise downloader.download_error


asyncio.run(main())
