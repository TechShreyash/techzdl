from curl_cffi.requests import AsyncSession


async def main():
    try:
        raise Exception("This is a test.")
    finally:
        print("This is a real.")


import asyncio

asyncio.run(main())
