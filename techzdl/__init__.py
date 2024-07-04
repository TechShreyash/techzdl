# Name: techzdl
# Version: 1.2.5
# Summary: A simple yet powerfull file downloader package for python
# Home-page: https://github.com/TechShreyash/techzdl
# Author: TechShreyash
# Author-email: techshreyash123@gmail.com
# License: MIT

import aiohttp
import aiofiles
import asyncio
import inspect
from tqdm import tqdm
from pathlib import Path
from techzdl.extra import (
    change_file_path_if_exist,
    get_random_string,
    AdjustableSemaphore,
    get_filename,
)
from techzdl.logger import Logger
from typing import Callable, Any, Union, Awaitable, Optional
from curl_cffi.requests import AsyncSession


class TechZDL:
    def __init__(
        self,
        url: str,
        custom_headers: Optional[dict] = None,
        output_dir: Union[str, Path] = Path("downloads"),
        filename: Optional[str] = None,
        workers: Optional[int] = None,
        initial_dynamic_workers: int = 2,
        dynamic_workers_update_interval: int = 5,
        debug: bool = True,
        progress: bool = True,
        progress_callback: Optional[
            Union[Callable[..., Any], Callable[..., Awaitable[Any]]]
        ] = None,
        progress_args: tuple = (),
        progress_interval: int = 1,
        chunk_size: int = 5 * 1024 * 1024,
        single_threaded: bool = False,
        max_retries: int = 3,
    ) -> None:
        """
        Initialize the TechZDL object.

        #### Args:
            - `url` `(str)`: URL of the file to download.
            - `custom_headers` `(Optional[dict], optional)`: Custom headers to send with the request. Defaults to None.
            - `output_dir` `(Union[str, Path], optional)`: Directory where the file will be saved. Defaults to "downloads".
            - `filename` `(Optional[str], optional)`: Name to save the file as (including extension). By default, this will be determined automatically.
            - `workers` `(Optional[int], optional)`: Number of fixed concurrent download workers. By default, this will be dynamically adjusted based on the download speed. Setting this will disable dynamic worker adjustment.
            - `initial_dynamic_workers` `(int, optional)`: Initial number of dynamic workers. Defaults to 2.
            - `dynamic_workers_update_interval` `(int, optional)`: Interval in seconds to update dynamic worker count. Defaults to 5.
            - `debug` `(bool, optional)`: Enable debug logs. Defaults to True.
            - `progress` `(bool, optional)`: Enable download progress display. Defaults to True.
            - `progress_callback` `(Optional[Union[Callable[..., Any], Callable[..., Awaitable[Any]]]], optional)`: Callback function for download progress updates. Can be sync or async. Defaults to None. Setting this disables tqdm progress.
            - `progress_args` `(tuple, optional)`: Additional arguments for progress_callback. Defaults to ().
            - `progress_interval` `(int, optional)`: Time interval for progress updates in seconds. Defaults to 1.
            - `chunk_size` `(int, optional)`: Size of each download chunk in bytes. Defaults to 5 MB.
            - `single_threaded` `(bool, optional)`: Force single-threaded download. Defaults to False.
            - `max_retries` `(int, optional)`: Maximum retries for each chunk/file download. Defaults to 3.

        #### Examples:
        ```python
        import asyncio
        from techzdl import TechZDL

        async def main():
            downloader = TechZDL(url="https://link.testfile.org/bNYZFw")
            await downloader.start()

        asyncio.run(main())
        ```

        For more examples and usage, check: [TechZDL Demos](https://github.com/TechShreyash/techzdl/tree/main/demos)
        """

        self.id = get_random_string(6)
        self.url = url
        self.custom_headers = custom_headers
        self.output_dir = (
            Path(output_dir) if isinstance(output_dir, str) else output_dir
        )
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.output_path = None
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
        self.is_running = False
        self.downloader_tasks = []
        self.temp_file_path = None
        self.download_success = False
        self.download_error = None
        self.background_download = False
        self.is_downloader_used = False

        self.logger.info(f"Created TechZ FileDownloader with ID: {self.id} URL: {url}")

    async def start(self, in_background: bool = False) -> Path:
        """
        Starts the download process.

        #### Args

        - `in_background` `(bool, optional)`: Run the download process in the background. Defaults to False.

        #### Returns

        - `filepath` `(Path)`: Path to the downloaded file.

        > Note: `Path` here refers to the `Path` object from the `pathlib` library.

        ```python
        from pathlib import Path
        ```
        """
        if self.is_running:
            raise Exception("Download process is already started")

        if self.is_downloader_used:
            raise Exception(
                "Download process is already created using this object. Please create a new object to start a new download process."
            )

        main_task = asyncio.create_task(self._download_manager())
        self.downloader_tasks.append(main_task)
        self.is_running = True
        self.is_downloader_used = True

        if not in_background:
            return await main_task
        else:
            self.background_download = True

    async def stop(self) -> None:
        """
        Forcefully stops the download process.
        """
        if self.is_running:
            for task in self.downloader_tasks:
                task.cancel()

            await asyncio.gather(*self.downloader_tasks, return_exceptions=True)

            self._log("Download process stopped", level="warning")
            await self._cleanup()
            self.is_running = False
        else:
            self._log(
                "Download process is not running! Why are you trying to stop it.",
                level="warning",
            )

    async def get_file_info(self) -> dict:
        """
        Fetches file information from the server.

        #### Returns

        - `dict`: File information in the format `{"filename": str, "total_size": int}`.

        - `filename` `(str)`: Name as returned by the server or determined by the TechZDL package using response headers and download URL.
        - `total_size` `(int)`: Total size of the file in bytes.
        """
        for i in range(self.max_retries):
            try:

                session = aiohttp.ClientSession()

                self._log(f"Fetching file info from {self.url}")
                response = None
                try:
                    response = await session.get(
                        url=self.url, headers=self.custom_headers
                    )
                except Exception as e:
                    raise e
                finally:
                    if response:
                        response.close()
                total_size = int(response.headers.get("Content-Length", 0))
                if total_size == 0:
                    raise Exception("Content-Length header is missing or invalid")

                filename = get_filename(response.headers, response.url, self.id)
                break
            except Exception as e:
                try:
                    self._log(
                        f"Failed to get file info using aiohttp: {e}", level="error"
                    )
                    await session.close()

                    session = AsyncSession()

                    response = None
                    try:
                        response = await session.get(
                            url=self.url, headers=self.custom_headers, stream=True
                        )
                    except Exception as e:
                        raise e
                    finally:
                        if response:
                            response.close()

                    total_size = int(response.headers.get("Content-Length", 0))
                    if total_size == 0:
                        raise Exception("Content-Length header is missing or invalid")

                    filename = get_filename(response.headers, response.url, self.id)
                    break
                except Exception as e:
                    self._log(f"Error getting file info: {e}", level="error")
                    if i == self.max_retries - 1:
                        await session.close()
                        raise e
                    self._log(
                        f"Retrying getting file info ({i + 1}/{self.max_retries})",
                        level="warning",
                    )
                    await asyncio.sleep(2**i)  # Exponential backoff

        await session.close()
        return {"filename": str(filename), "total_size": total_size}

    def _log(self, message: str, level: str = "info") -> None:
        """
        Log a message with the specified level.

        Args:
            message (str): Message to log.
            level (str): Log level ('info', 'warning', 'error'). Defaults to 'info'.
        """

        if level == "warning":
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)
        elif self.debug:
            self.logger.info(message)

    async def _task_runner(self, tasks: list[Awaitable]) -> None:
        """
        Run a list of async tasks concurrently, handling exceptions and cancellations.

        Args:
            tasks (list[Awaitable]): List of async tasks to run.
        """

        try:
            new_tasks = [asyncio.create_task(task) for task in tasks]
            tasks = new_tasks
            for task in tasks:
                self.downloader_tasks.append(task)

            done, pending = await asyncio.wait(
                tasks, return_when=asyncio.FIRST_EXCEPTION
            )
            for task in tasks:
                self.downloader_tasks.remove(task)

            for task in done:
                if task.exception():
                    for pending_task in pending:
                        pending_task.cancel()
                    await asyncio.gather(*pending, return_exceptions=True)
                    raise task.exception()
        except Exception as e:
            self._log(
                f"Exception raised in task runner: {e}",
                level="error",
            )
            raise e

    async def _show_progress(self, description: str) -> None:
        """
        Show download progress either via a callback or tqdm progress bar.

        Args:
            description (str): Description for the progress display.
        """
        previous_size = 0

        if self.progress_callback:
            while self.size_done < self.total_size:
                if self.size_done != previous_size:
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

                    previous_size = self.size_done

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
                    while self.size_done < self.total_size:
                        if self.size_done != previous_size:
                            pbar.update(self.size_done - previous_size)
                            previous_size = self.size_done

                        await asyncio.sleep(self.progress_interval)
                    pbar.update(self.total_size - previous_size)

    async def _load_chunk(
        self, start: int, end: int, semaphore: AdjustableSemaphore
    ) -> None:
        """
        Load a chunk of the file.

        Args:
            temp_file_path (Path): Path to the temporary file.
            start (int): Start byte of the chunk.
            end (int): End byte of the chunk.
            semaphore (AdjustableSemaphore): Semaphore to control concurrency.
        """
        await semaphore.acquire()
        try:
            for i in range(self.max_retries):
                try:
                    headers = {"Range": f"bytes={start}-{end}"}
                    if self.custom_headers:
                        headers.update(self.custom_headers)

                    response = None
                    try:
                        response = await self.session.get(url=self.url, headers=headers)
                        chunk = await response.content.read()
                    except Exception as e:
                        raise e
                    finally:
                        if response:
                            response.close()

                    async with aiofiles.open(self.temp_file_path, "r+b") as file:
                        await file.seek(start)
                        await file.write(chunk)

                    self.size_done += len(chunk)
                    break
                except Exception as e:
                    self._log(
                        f"Error downloading chunk {start}-{end}: {e}", level="error"
                    )
                    if i == self.max_retries - 1:
                        raise e
                    self._log(
                        f"Retrying chunk {start}-{end} ({i + 1}/{self.max_retries})",
                        level="warning",
                    )
                    await asyncio.sleep(2**i)  # Exponential backoff
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self._log(f"Failed to download chunk {start}-{end}: {e}", level="error")
            raise e
        finally:
            await semaphore.release()

    async def _temp_file_creator(self, total_chunks: int) -> None:
        """
        Create a temporary file with the specified size.

        Args:
            temp_file_path (Path): Path to the temporary file.
            total_chunks (int): Total number of chunks.
        """
        async with aiofiles.open(self.temp_file_path, "wb") as file:
            for i in range(total_chunks):
                start = i * self.chunk_size
                end = min(start + self.chunk_size - 1, self.total_size - 1)
                await file.write(b"\0" * (end - start + 1))
                self.size_done += end - start + 1

    async def _dynamic_worker_updater(self, semaphore: AdjustableSemaphore) -> None:
        """
        Dynamically update the number of workers based on download speed.

        Args:
            semaphore (AdjustableSemaphore): Semaphore to control concurrency.
        """
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

    async def _single_threaded_download_child(self) -> None:
        response = None
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
                if response:
                    response.close()
        else:
            try:
                response = await self.session.get(self.url, headers=self.custom_headers)
                async with aiofiles.open(self.output_path, "wb") as output_file:
                    while chunk := await response.content.read(self.chunk_size):
                        await output_file.write(chunk)
                        self.size_done += len(chunk)
            except Exception as e:
                raise e
            finally:
                if response:
                    response.close()

    async def _single_threaded_download(self) -> None:
        """
        Perform a single-threaded download of the file.
        """
        for i in range(self.max_retries):
            self.size_done = 0  # Reset size_done if retrying

            try:
                await self._task_runner(
                    [
                        self._single_threaded_download_child(),
                        self._show_progress("Downloading"),
                    ]
                )
                break
            except Exception as e:
                self._log(f"Error downloading file: {e}", level="error")
                if i == self.max_retries - 1:
                    raise e
                self._log(
                    f"Retrying download ({i + 1}/{self.max_retries})", level="warning"
                )
                await asyncio.sleep(2**i)  # Exponential backoff

    async def _multi_threaded_download(self) -> None:
        """
        Perform a multi-threaded download of the file.
        """
        total_chunks = (self.total_size + self.chunk_size - 1) // self.chunk_size
        self.temp_file_path = self.output_dir / (self.output_path.stem + ".temp")
        self._log(
            f"Creating temp file {self.temp_file_path.name} of size {self.total_size} bytes"
        )

        await self._task_runner(
            [
                self._temp_file_creator(total_chunks),
                self._show_progress("Creating Temp File"),
            ]
        )
        self.size_done = 0

        semaphore = AdjustableSemaphore(self.dynamic_workers)
        tasks = []

        for i in range(total_chunks):
            start = i * self.chunk_size
            end = min(start + self.chunk_size - 1, self.total_size - 1)
            task = self._load_chunk(start, end, semaphore)
            tasks.append(task)

        self._log(f"Starting download of {self.filename}")

        if self.workers:
            self.dynamic_workers = self.workers
            await semaphore.set_limit(self.dynamic_workers)
        else:
            tasks.append(self._dynamic_worker_updater(semaphore))

        tasks.append(self._show_progress("Downloading"))

        await self._task_runner(tasks)
        self.temp_file_path.rename(self.output_path)
        self.temp_file_path = None

    async def _cleanup(self) -> None:
        if self.is_running and self.output_path:
            self.output_path.unlink(missing_ok=True)

        if self.temp_file_path:
            self.temp_file_path.unlink(missing_ok=True)

        if self.session:
            await self.session.close()

    async def _download_manager(self) -> Path:
        try:
            self.size_done = 0
            self._log("Initializing download process")

            for i in range(self.max_retries):

                try:
                    if self.session:
                        await self.session.close()
                    self.session = aiohttp.ClientSession()

                    self._log(f"Fetching file info from {self.url}")
                    response = None
                    try:
                        response = await self.session.get(
                            url=self.url, headers=self.custom_headers
                        )
                    except Exception as e:
                        raise e
                    finally:
                        if response:
                            response.close()

                    self.total_size = int(response.headers.get("Content-Length", 0))
                    if self.total_size == 0:
                        raise Exception("Content-Length header is missing or invalid")

                    if not self.filename:
                        self.filename = get_filename(
                            response.headers, response.url, self.id
                        )
                    accept_ranges = response.headers.get("Accept-Ranges")
                    break
                except Exception as e:
                    try:
                        self._log(
                            f"Failed to get file info using aiohttp: {e}", level="error"
                        )
                        await self.session.close()

                        self.session = AsyncSession()
                        self.curl_cffi_required = True

                        response = None
                        try:
                            response = await self.session.get(
                                url=self.url, headers=self.custom_headers, stream=True
                            )
                        except Exception as e:
                            raise e
                        finally:
                            if response:
                                response.close()

                        self.total_size = int(response.headers.get("Content-Length", 0))
                        if self.total_size == 0:
                            raise Exception(
                                "Content-Length header is missing or invalid"
                            )

                        if not self.filename:
                            self.filename = get_filename(
                                response.headers, response.url, self.id
                            )
                        accept_ranges = response.headers.get("Accept-Ranges")
                        break
                    except Exception as e:
                        self._log(f"Error getting file info: {e}", level="error")
                        if i == self.max_retries - 1:
                            if self.session:
                                await self.session.close()
                            raise e
                        self._log(
                            f"Retrying getting file info ({i + 1}/{self.max_retries})",
                            level="warning",
                        )
                        await asyncio.sleep(2**i)  # Exponential backoff

            self.output_path = change_file_path_if_exist(
                self.output_dir / self.filename
            )
            self.filename = self.output_path.name

            if accept_ranges != "bytes" or self.single_threaded:
                if accept_ranges != "bytes":
                    self._log(
                        "Server does not support range requests. Multi-threaded download not supported.",
                        level="warning",
                    )
                self._log("Starting single-threaded download")
                self._log(f"Downloading {self.filename}")

                await self._single_threaded_download()
            else:
                self._log(
                    "Server supports range requests. Starting multi-threaded download"
                )
                await self._multi_threaded_download()

            self._log(f"Download completed: {self.filename}")
            self.is_running = False
            await self.session.close()

            self.download_success = True
            return self.output_path

        except asyncio.CancelledError:
            self.download_error = asyncio.CancelledError
            raise asyncio.CancelledError

        except Exception as e:
            self._log(f"Error in download process: {e}", level="error")
            await self._cleanup()
            self.is_running = False
            self.download_error = e
            raise e
