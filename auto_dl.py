
async def watcher(total, semaphore):
    global DONE
    prev = 0
    p_speed = 0
    limit = 2

    while True:
        if DONE >= total:
            break
        await asyncio.sleep(5)
        speed = (DONE - prev) / 5 / 1024 / 1024  # MB/s
        print(f"Speed: {speed} mb/sec")

        if speed > p_speed:
            limit += 2
            await semaphore.set_limit(limit)
            print(f"Limit: {limit}")
        elif speed < p_speed:
            limit = max(2, limit - 2)
            await semaphore.set_limit(limit)
            print(f"Limit: {limit}")

        prev = DONE
        p_speed = speed


async def load_chunk(num, session, url, start, end, semaphore):
    global DONE

    await semaphore.acquire()
    try:
        # print(f"downloading chunk {num}")

        headers = {"Range": f"bytes={start}-{end}"}
        async with session.get(url, headers=headers) as response:
            chunk = await response.read()

        async with aiofiles.open("video.mp4", "r+b") as file:
            await file.seek(start)
            await file.write(chunk)

        DONE += end - start + 1
        # print(f"downloaded chunk {num}")

    finally:
        await semaphore.release()


async def main():
    url = "https://ash-speed.hetzner.com/1GB.bin"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            total_size = int(response.headers["Content-Length"])

        chunk_size = 5 * 1024 * 1024  # 5MB
        total_chunks = (total_size + chunk_size - 1) // chunk_size

        semaphore = AdjustableSemaphore(2)
        tasks = []

        print(f"Creating file with size {total_size/1024/1024/1024} gb")
        async with aiofiles.open("video.mp4", "wb") as file:
            for i in range(total_chunks):
                print(f"Creating chunk {i}/{total_chunks}", end="\r")
                start = i * chunk_size
                end = min(start + chunk_size - 1, total_size - 1)
                await file.write(b"\0" * (end - start + 1))
                task = load_chunk(i, session, url, start, end, semaphore)
                tasks.append(task)

        tasks.append(watcher(total_size, semaphore))
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    a = time()
    asyncio.run(main())
    b = time()
    print(f"Time taken: {b-a} seconds")
