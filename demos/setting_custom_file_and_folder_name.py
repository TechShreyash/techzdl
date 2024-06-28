# By specifying the output directory and filename, you can organize your downloads and ensure files are saved with your preferred names.
# This is useful when you need to manage multiple downloads and want to store them in specific locations with specific names.

import asyncio
from techzdl import TechZDL


async def main():
    downloader = TechZDL(
        url="https://link.testfile.org/bNYZFw",
        output_dir="my_files",  # Custom directory where the file will be saved
        filename="my_video.mp4",  # Custom filename for the downloaded file
    )
    await downloader.start()


asyncio.run(main())
