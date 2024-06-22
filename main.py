import speedtest
from downloader import FileDownloader
from pathlib import Path
from logger import Logger
from typing import Callable, Any, Union, Awaitable


class TechZDL:
    def __init__(self) -> None:
        """
        Initialize the TechZDL class.
        """
        pass

    def get_dowloader(
        self,
        url: str,
        headers: dict = None,
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
    ) -> FileDownloader:
        """
        Create a FileDownloader object with the specified parameters.

        Args:
            url (str): URL of the file to download.

            output_dir (Union[str, Path], optional): Directory where the file will be saved.
                Defaults to Path("downloads"). This can be a string or a Path object.

            filename (Optional[str], optional): Name to save the file as.
                If not provided, the filename will be extracted from response headers or URL.
                Defaults to None.

            workers (int, optional): Number of concurrent download workers.
                Higher values can speed up downloads by using multiple threads.
                Defaults to 4.

            debug (bool, optional): Enable debug mode. If True, detailed debug logs will be shown.
                Useful for troubleshooting. Defaults to False.

            progress (bool, optional): Show download progress. If True, download progress will be
                displayed. Defaults to True.

            progress_callback (Union[Callable[..., Any], Callable[..., Awaitable[Any]]], optional):
                A callback function to be called to update download progress. Can be synchronous or
                asynchronous. The callback will receive the progress percentage and any additional
                arguments specified in `progress_args`. Defaults to None.

            progress_args (tuple, optional): Additional arguments to pass to the `progress_callback`
                function. Defaults to an empty tuple.

            progress_interval (int, optional): Time interval in seconds to sleep between updating the
                progress. This controls how frequently the progress callback is called. Defaults to 1 second.

            chunk_size (int, optional): Size of each download chunk in bytes. Adjust this value based on
                memory and performance considerations. Defaults to 1 MiB (1024 * 1024 bytes).

            single_threaded (bool, optional): Use single-threaded download mode. If True, disables
                multithreading for the download. Defaults to False.

        Returns:
            FileDownloader: Instance of FileDownloader configured with the specified parameters.

        Example:
            ```python
            import asyncio

            async def main():
                TechZDL = TechZDL()
                downloader = TechZDL.get_downloader("https://speed.hetzner.de/100MB.bin")
                await downloader.start()

            asyncio.run(main())
            ```
        """

        return FileDownloader(
            url,
            headers,
            output_dir,
            filename,
            workers,
            initial_dynamic_workers,
            dynamic_workers_update_interval,
            debug,
            progress,
            progress_callback,
            progress_args,
            progress_interval,
            chunk_size,
            single_threaded,
        )


import asyncio


async def main():
    techzdl = TechZDL()
    downloader = techzdl.get_dowloader(
        "https://vadapav.mov/f/42e13842-a9aa-4d6c-ba06-8f8829726c75/",
        chunk_size=1024 * 1024,
    )
    await downloader.start()


asyncio.run(main())
