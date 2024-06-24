import asyncio
from techzdl.api import TechZDL


async def main():
    techzdl = TechZDL()
    downloader = techzdl.get_downloader(url="https://link.testfile.org/bNYZFw")
    await downloader.start()


asyncio.run(main())
