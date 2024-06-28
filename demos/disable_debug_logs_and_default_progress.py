# Setting 'debug' to False will disable detailed logging, which can be useful to reduce log clutter in production.
# Setting 'progress' to False will disable the tqdm progress bar by techzdl, which can be useful in environments where a progress bar is not needed, such as in automated scripts or background processes.
# Adding custom progress_callback will still work

import asyncio
from techzdl import TechZDL


async def main():
    downloader = TechZDL(
        url="https://link.testfile.org/bNYZFw",
        debug=False,  # Disable debug logs
        progress=False,  # Disable progress display
    )
    await downloader.start()


asyncio.run(main())
