from downloader import FileDownloader
from pathlib import Path
from logger import Logger
from typing import Callable, Any, Union, Awaitable, Optional


class TechZDL:
    def __init__(self) -> None:
        """
        Initialize the TechZDL class.
        """
        self.logger = Logger("TechZDL")

    def get_downloader(
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
        timeout: int = 60,
    ) -> FileDownloader:
        """
        Create a FileDownloader object with the specified parameters.

        Args:
            url (str): URL of the file to download.
            custom_headers (Optional[dict], optional): Custom headers to send with the request. Defaults to None.
            output_dir (Union[str, Path], optional): Directory where the file will be saved. Defaults to "downloads".
            filename (Optional[str], optional): Name to save the file as (including extension). By default, this will be determined automatically.
            workers (Optional[int], optional): Number of fixed concurrent download workers. By default, this will be dynamically changed based on the download speed.
            initial_dynamic_workers (int, optional): Initial number of dynamic workers. Defaults to 2.
            dynamic_workers_update_interval (int, optional): Interval in seconds to update dynamic worker count. Defaults to 5.
            debug (bool, optional): Enable debug logs. Defaults to True.
            progress (bool, optional): Enable download progress display. Defaults to True.
            progress_callback (Optional[Union[Callable[..., Any], Callable[..., Awaitable[Any]]]], optional):
                Callback function for download progress updates. Can be sync or async. Defaults to None. Setting this disables tqdm progress.
            progress_args (tuple, optional): Additional arguments for progress_callback. Defaults to ().
            progress_interval (int, optional): Time interval for progress updates in seconds. Defaults to 1.
            chunk_size (int, optional): Size of each download chunk in bytes. Defaults to 5 MB.
            single_threaded (bool, optional): Force single-threaded download. Defaults to False.
            max_retries (int, optional): Maximum retries for each chunk/file download. Defaults to 3.
            timeout (int, optional): Timeout for each request in seconds. Defaults to 60.

        Returns:
            FileDownloader: Instance of FileDownloader configured with the specified parameters.

        Example:
            ```python
            import asyncio

            async def main():
                techzdl = TechZDL()
                downloader = techzdl.get_downloader("https://speed.hetzner.de/100MB.bin")
                await downloader.start()

            asyncio.run(main())
            ```
        """
        if debug:
            self.logger.info(f"Creating TechZ FileDownloader with URL: {url}")

        downloader = FileDownloader(
            url,
            custom_headers,
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
            max_retries,
            timeout,
        )
        return downloader
