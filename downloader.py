import aiohttp
import aiofiles
import asyncio
import inspect
from tqdm import tqdm
from pathlib import Path
from extra import change_file_path_if_exist, get_random_string, AdjustableSemaphore,get_filename
from logger import Logger
from typing import Callable, Any, Union, Awaitable
from curl_cffi.requests import AsyncSession


class FileDownloader:
    def __init__(
        self,
        url: str,
        custom_headers: dict = None,
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
        max_retries: int = 3,
        timeout: int = 60,
    ) -> None:
        """
        Initialize the FileDownloader object.

        Args:
            url (str): URL of the file to download.
            custom_headers (dict, optional): Custom headers to send with the request. Defaults to None.
            output_dir (Union[str, Path], optional): Directory where the file will be saved. Defaults to "downloads".
            filename (str, optional): Name to save the file as (including extension). By default this will determined automatically, from headers or url, if failed then a default id will be used as filename.
            workers (int, optional): Number of fixed concurrent download workers. By default this will be dynamically changed based on the download speed.
            initial_dynamic_workers (int, optional): Number of initial dynamic workers count to start with when dynamically determining workers. Defaults to 2.
            dynamic_workers_update_interval (int,optional): Interval in seconds after which the dynamic worker count will get updated, Default 5 seconds
            debug (bool, optional): True to get debug logs. Defaults to True.
            progress (bool, optional): True if you want tqdm download progress. Defaults to True.
            progress_callback (Union[Callable[..., Any], Callable[..., Awaitable[Any]]], optional):
                Callback function to update download progress. Can be sync or async. Defaults to None. Setting this will disable tqdm progress.
            progress_args (tuple, optional): Additional arguments for progress_callback. Defaults to ().
            progress_interval (int, optional): Time interval for progress updates in seconds. Defaults to 1.
            chunk_size (int, optional): Size of each download chunk in bytes. Defaults to 5 MB. Dont make it too small or too large (more than 10 mb not recommended).
            single_threaded (bool, optional): True if you want to use single-threaded download. Defaults to False, will be determined automatically based on the download url server.
            max_retries (int, optional): Number of retries for each chunk/file download. Defaults to 3.
            timeout (int, optional): Timeout for each request in seconds. Defaults to 60.
        """
        self.id = get_random_string(6)
        self.url = url
        self.custom_headers = custom_headers
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
        self.curl_cffi_required = False
        self.max_retries = max_retries
        self.session = None
        self.timeout = timeout

    def log(self, message: str) -> None:
        """
        Log a message if debug mode is enabled.

        Args:
            message (str): Message to log.
        """
        if self.debug:
            self.logger.debug(message)

    async def task_runner(self, tasks):
        new_tasks = [asyncio.create_task(task) for task in tasks]
        tasks = new_tasks
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)

        for task in done:
            if task.exception():
                for pending_task in pending:
                    pending_task.cancel()
                # Wait for the cancellation to complete
                await asyncio.gather(*pending, return_exceptions=True)
                raise task.exception()

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
            if self.is_callback_async:
                await self.progress_callback(
                    description, self.total_size, self.total_size, *self.progress_args
                )
            else:
                self.progress_callback(
                    description, self.total_size, self.total_size, *self.progress_args
                )
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
            for i in range(self.max_retries):
                try:
                    headers = {"Range": f"bytes={start}-{end}"}
                    if self.custom_headers:
                        headers.update(self.custom_headers)

                    if self.curl_cffi_required:
                        try:
                            response = await self.session.get(
                                url=self.url, headers=headers
                            )
                            chunk = response.content
                            if len(chunk) != end - start + 1:
                                print(len(chunk), end - start + 1)
                                raise Exception("Chunk size mismatch")
                        finally:
                            try:
                                response.close()
                            except:
                                pass
                    else:
                        try:
                            response = await self.session.get(
                                url=self.url, headers=headers
                            )
                            chunk = await response.content.read()
                        finally:
                            try:
                                response.close()
                            except:
                                pass

                    async with aiofiles.open(temp_file_path, "r+b") as file:
                        await file.seek(start)
                        await file.write(chunk)

                    self.size_done += len(chunk)
                    break
                except Exception as e:
                    self.log(f"Error downloading chunk {start}-{end}: {e}")
                    if i == self.max_retries - 1:
                        raise e
                    self.log(
                        f"Retrying chunk {start}-{end} ({i + 1}/{self.max_retries})"
                    )

        except asyncio.CancelledError:
            pass
        except Exception as e:
            raise e
        finally:
            await semaphore.release()

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

    async def single_threaded_download(self) -> None:
        """
        Perform a single-threaded download of the file.
        """

        for i in range(self.max_retries):
            try:
                if self.curl_cffi_required:
                    try:
                        response = await self.session.get(
                            url=self.url, headers=self.custom_headers, stream=True
                        )
                        async with aiofiles.open(self.output_path, "wb") as output_file:
                            async for chunk in response.aiter_content():
                                await output_file.write(chunk)
                                self.size_done += len(chunk)
                    except Exception as e:
                        raise e
                    finally:
                        try:
                            response.close()
                        except:
                            pass
                else:
                    try:
                        response = await self.session.get(
                            self.url, headers=self.custom_headers
                        )
                        async with aiofiles.open(self.output_path, "wb") as output_file:
                            while chunk := await response.content.read(self.chunk_size):
                                await output_file.write(chunk)
                                self.size_done += len(chunk)
                    finally:
                        try:
                            response.close()
                        except:
                            pass
                break
            except Exception as e:
                self.log(f"Error downloading file: {e}")
                if i == self.max_retries - 1:
                    raise e
                self.log(f"Retrying download ({i + 1}/{self.max_retries})")

    async def multi_threaded_download(self):
        total_chunks = (self.total_size + self.chunk_size - 1) // self.chunk_size

        temp_file_path = self.output_dir / (self.output_path.stem + ".temp")
        self.log(
            f"Creating Temp File {temp_file_path.name} of size {self.total_size} bytes"
        )
        await self.task_runner(
            [
                self.temp_file_creator(temp_file_path, total_chunks),
                self.show_progress("Creating Temp File"),
            ]
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

        await self.task_runner(tasks)

        temp_file_path.rename(self.output_path)

    async def start(self) -> Path:
        """
        Start the download process.

        Returns:
            Path: Path to the downloaded file.
        """
        self.size_done = 0
        self.log("Getting file info")

        for i in range(self.max_retries):
            try:
                if self.session:
                    try:
                        await self.session.close()
                    except:
                        pass
                self.session = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                )

                try:
                    response = await self.session.get(
                        url=self.url, headers=self.custom_headers
                    )
                finally:
                    try:
                        response.close()
                    except:
                        pass

                self.total_size = int(response.headers.get("Content-Length", 0))
                if self.total_size == 0:
                    raise Exception("Content-Length header is missing or invalid")

                if not self.filename:
                    self.filename = get_filename(response.headers, self.url, self.id)
                accept_ranges = response.headers.get("Accept-Ranges")
                break
            except Exception as e:
                try:
                    self.log(f"Failed to get file info using aiohttp: {e}")
                    try:
                        await self.session.close()
                    except:
                        pass

                    self.session = AsyncSession(timeout=self.timeout)
                    self.curl_cffi_required = True

                    try:
                        response = await self.session.get(
                            url=self.url, headers=self.custom_headers, stream=True
                        )
                    finally:
                        try:
                            response.close()
                        except:
                            pass

                    self.total_size = int(response.headers.get("Content-Length", 0))
                    if self.total_size == 0:
                        raise Exception("Content-Length header is missing or invalid")

                    if not self.filename:
                        self.filename = get_filename(
                            response.headers, self.url, self.id
                        )
                    accept_ranges = response.headers.get("Accept-Ranges")
                    break
                except Exception as e:
                    self.log(f"Error getting file info: {e}")
                    if i == self.max_retries - 1:
                        try:
                            await self.session.close()
                        except:
                            pass
                        raise e
                    self.log(f"Retrying getting file info ({i + 1}/{self.max_retries})")

        self.output_path = change_file_path_if_exist(self.output_dir / self.filename)
        self.filename = self.output_path.name

        if accept_ranges != "bytes" or self.single_threaded:
            if accept_ranges != "bytes":
                self.log(
                    "Server does not support range requests. Multi-Threaded Download not supported."
                )
            self.log("Starting Single-Threaded Download")
            self.log(f"Downloading {self.filename}")

            if self.progress:
                await self.task_runner(
                    [
                        self.single_threaded_download(),
                        self.show_progress("Downloading"),
                    ]
                )
            else:
                await self.single_threaded_download()
        else:
            self.log("Server supports range requests. Starting Multi-Threaded Download")

            await self.multi_threaded_download()

        self.log(f"Downloaded {self.filename}")
        try:
            await self.session.close()
        except:
            pass
        return self.output_path
