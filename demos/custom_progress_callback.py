# This script demonstrates how to monitor the download progress by providing a custom callback function.
# By setting the 'progress_callback' parameter, the provided function will be called periodically with the current progress.
# This will disable the default progress bar and you can use your own progress bar or any other progress indicator.
# This is useful for updating a UI, logging progress, or executing other actions based on the download status.


import asyncio
from techzdl import TechZDL


def progress_callback(description, done, total, arg1, arg2):
    print(f"{description}: {done}/{total} bytes downloaded", arg1, arg2)


async def main():
    downloader = TechZDL(
        url="https://link.testfile.org/bNYZFw",  # URL of the file to download
        progress_callback=progress_callback,  # Custom progress callback function
        progress_args=(
            "arg1",
            "arg2",
        ),  # Additional arguments to pass to the callback function
        progress_interval=2,  # Interval in seconds for calling the progress callback
    )
    await downloader.start()


asyncio.run(main())
