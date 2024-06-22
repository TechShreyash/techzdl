import aiohttp
import aiofiles
import asyncio
import inspect
from tqdm import tqdm
from pathlib import Path
from extra import change_file_path_if_exist, get_random_string
from filename_parser import get_filename
from logger import Logger
from typing import Callable, Any, Union, Awaitable


class AdjustableSemaphore:
    def __init__(self, initial_value):
        self._value = initial_value
        self._condition = asyncio.Condition()

    async def acquire(self):
        async with self._condition:
            while self._value <= 0:
                await self._condition.wait()
            self._value -= 1

    async def release(self):
        async with self._condition:
            self._value += 1
            self._condition.notify()

    async def set_limit(self, new_limit):
        async with self._condition:
            self._value += new_limit - self._value
            self._condition.notify_all()


class FileDownloader:
    def __init__(
        self,
        url: str,
        output_dir: Union[str, Path] = Path("downloads"),
        filename: str = None,
        workers: int = None,
        initial_dynamic_workers: int = 2,
        dynamic_workers_update_interval: int = 5,
        debug: bool = True,
        progress: bool = True,
        progress_callback: Union[
            Callable[..., Any], Callable[..., Awaitable[Any]]
        ] = None,
        progress_args: tuple = (),
        progress_interval: int = 1,
        chunk_size: int = 5 * 1024 * 1024,
        single_threaded: bool = False,
    ) -> None:
        """
        Initialize the FileDownloader object.

        Args:
            url (str): URL of the file to download.
            output_dir (Union[str, Path], optional): Directory where the file will be saved. Defaults to "downloads".
            filename (str, optional): Name to save the file as. By default this will determined automatically, from headers or url, if failed then a default id will be used as filename.
            workers (int, optional): Number of fixed concurrent download workers. By default this will be dynamically changed based on the download speed.
            initial_dynamic_workers (int, optional): Number of initial dynamic workers count to start with when dynamically determining workers. Defaults to 2.
            dynamic_workers_update_interval (int,optional): Interval in seconds after which the dynamic worker count will get updated, Defaukt 5 seconds
            debug (bool, optional): Enable/Disable debug mode. Defaults to True.
            progress (bool, optional): True if you want tqdm download progress. Defaults to True.
            progress_callback (Union[Callable[..., Any], Callable[..., Awaitable[Any]]], optional):
                Callback function to update download progress. Can be sync or async. Defaults to None.
            progress_args (tuple, optional): Additional arguments for progress_callback. Defaults to ().
            progress_interval (int, optional): Time interval for progress updates in seconds. Defaults to 1.
            chunk_size (int, optional): Size of each download chunk in bytes. Defaults to 5 MB.
            single_threaded (bool, optional): True if you want to use single-threaded download. Defaults to False, will be determined automatically based on the download server.
        """
        self.id = get_random_string(6)
        self.url = url
        self.output_dir = (
            Path(output_dir) if isinstance(output_dir, str) else output_dir
        )
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.filename = filename
        self.workers = workers
        self.debug = debug
        self.logger = Logger(f"TechZDL - {self.id}")
        self.progress = progress
        self.progress_callback = progress_callback
        self.progress_args = progress_args
        self.chunk_size = chunk_size
        self.progress_interval = progress_interval
        self.single_threaded = single_threaded or workers == 1
        self.is_callback_async = inspect.iscoroutinefunction(progress_callback)
        self.dynamic_workers = initial_dynamic_workers
        self.dynamic_workers_update_interval = dynamic_workers_update_interval

    def log(self, message: str) -> None:
        """
        Log a message if debug mode is enabled.

        Args:
            message (str): Message to log.
        """
        if self.debug:
            self.logger.debug(message)

    async def show_progress(self, description: str) -> None:
        """
        Show download progress either via a callback or tqdm progress bar.

        Args:
            description (str): Description for the progress display.
        """
        if self.progress_callback:
            while self.size_done < self.total_size:
                if self.is_callback_async:
                    await self.progress_callback(
                        description,
                        self.size_done,
                        self.total_size,
                        *self.progress_args,
                    )
                else:
                    self.progress_callback(
                        description,
                        self.size_done,
                        self.total_size,
                        *self.progress_args,
                    )
                await asyncio.sleep(self.progress_interval)
        else:
            if self.progress:
                with tqdm(
                    total=self.total_size,
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                    desc=description,
                    bar_format="{desc}: {percentage:3.0f}% |{bar}| {n_fmt}B/{total_fmt}B [{elapsed}<{remaining}, {rate_fmt}{postfix}]",
                ) as pbar:
                    previous_size = 0
                    while self.size_done < self.total_size:
                        pbar.update(self.size_done - previous_size)
                        previous_size = self.size_done
                        await asyncio.sleep(self.progress_interval)
                    pbar.update(self.total_size - previous_size)

    async def load_chunk(self, temp_file_path, start, end, semaphore) -> None:
        await semaphore.acquire()
        try:
            headers = {"Range": f"bytes={start}-{end}"}
            async with self.session.get(self.url, headers=headers) as response:
                chunk = await response.read()

            async with aiofiles.open(temp_file_path, "r+b") as file:
                await file.seek(start)
                await file.write(chunk)

            self.size_done += len(chunk)
        finally:
            await semaphore.release()

    async def single_threaded_download(self) -> None:
        """
        Perform a single-threaded download of the file.
        """
        async with self.session.get(self.url) as response:
            async with aiofiles.open(self.output_path, "wb") as output_file:
                while chunk := await response.content.read(self.chunk_size):
                    await output_file.write(chunk)
                    self.size_done += len(chunk)

    async def temp_file_creator(self, temp_file_path, total_chunks) -> tuple:
        async with aiofiles.open(temp_file_path, "wb") as file:
            for i in range(total_chunks):
                start = i * self.chunk_size
                end = min(start + self.chunk_size - 1, self.total_size - 1)
                await file.write(b"\0" * (end - start + 1))
                self.size_done += end - start + 1

    async def dynamic_worker_updater(self, semaphore) -> None:
        prev_downloaded = 0
        prev_speed = 0

        while True:
            if self.size_done >= self.total_size:
                break
            await asyncio.sleep(self.dynamic_workers_update_interval)
            speed = (
                self.size_done - prev_downloaded
            ) / self.dynamic_workers_update_interval

            if speed > prev_speed:
                self.dynamic_workers += 2
                await semaphore.set_limit(self.dynamic_workers)
            elif speed < prev_speed:
                self.dynamic_workers = max(2, self.dynamic_workers - 2)
                await semaphore.set_limit(self.dynamic_workers)

            prev_downloaded = self.size_done
            prev_speed = speed

    async def multi_threaded_download(self):
        total_chunks = (self.total_size + self.chunk_size - 1) // self.chunk_size

        temp_file_path = self.output_dir / (self.output_path.stem + ".temp")
        self.log(
            f"Creating Temp File {temp_file_path.name} of size {self.total_size} bytes"
        )
        await asyncio.gather(
            self.temp_file_creator(temp_file_path, total_chunks),
            self.show_progress("Creating Temp File"),
        )
        self.size_done = 0

        semaphore = AdjustableSemaphore(self.dynamic_workers)
        tasks = []

        for i in range(total_chunks):
            start = i * self.chunk_size
            end = min(start + self.chunk_size - 1, self.total_size - 1)
            task = self.load_chunk(temp_file_path, start, end, semaphore)
            tasks.append(task)

        self.log(f"Downloading {self.filename}")

        if self.workers:
            self.dynamic_workers = self.workers
            await semaphore.set_limit(self.dynamic_workers)
        else:
            tasks.append(self.dynamic_worker_updater(semaphore))

        tasks.append(self.show_progress("Downloading"))

        await asyncio.gather(*tasks)

        temp_file_path.rename(self.output_path)

    async def start(self) -> Path:
        """
        Start the download process.

        Returns:
            Path: Path to the downloaded file.
        """
        async with aiohttp.ClientSession() as session:
            self.session = session
            async with self.session.get(self.url) as response:
                self.total_size = int(response.headers.get("Content-Length", 0))
                self.size_done = 0
                if self.total_size == 0:
                    raise Exception("Content-Length header is missing or invalid")

                if not self.filename:
                    self.filename = get_filename(response.headers, self.url, self.id)

                self.output_path = change_file_path_if_exist(
                    self.output_dir / self.filename
                )
                self.filename = self.output_path.name

                accept_ranges = response.headers.get("Accept-Ranges")

            if accept_ranges != "bytes" or self.single_threaded:
                if accept_ranges != "bytes":
                    self.log(
                        "Server does not support range requests. Multi-Threaded Download not supported."
                    )
                self.log("Starting Single-Threaded Download")
                self.log(f"Downloading {self.filename}")

                if self.progress:
                    await asyncio.gather(
                        self.single_threaded_download(),
                        self.show_progress("Downloading"),
                    )
                else:
                    await self.single_threaded_download()
            else:
                self.log(
                    "Server supports range requests. Starting Multi-Threaded Download"
                )

                await self.multi_threaded_download()

            self.log(f"Downloaded {self.filename}")
            return self.output_path
