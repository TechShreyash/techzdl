# TechZDL

A simple yet powerful file downloader package for Python.

## Description

TechZDL is a highly efficient and easy-to-use file downloader package for Python. It provides features for downloading files with multiple threads, dynamic worker adjustments based on network speed, and more.

## Installation

You can install TechZDL using pip:

```sh
pip install techzdl
```

To update TechZDL to the latest version, use:

```sh
pip install --upgrade techzdl
```

## Usage

Here's a basic example of how to use TechZDL:

### Basic Usage

Code from [demos/basic.py](demos/basic.py) file

```python
import asyncio
from techzdl.api import TechZDL


async def main():
    techzdl = TechZDL()
    downloader = techzdl.get_downloader(url="https://link.testfile.org/bNYZFw")
    await downloader.start()


asyncio.run(main())
```

https://github.com/TechShreyash/techzdl/assets/82265247/33267e71-2b41-4dd1-b306-c87a197a3b57

## Configuration Parameters

The `get_downloader` method accepts several parameters to customize the download process:

- **url (str)**: URL of the file to download.

- **custom_headers (Optional[dict], optional)**: Custom headers to send with the request. Defaults to `None`.

- **output_dir (Union[str, Path], optional)**: Directory where the file will be saved. Defaults to `"downloads"`.

- **filename (Optional[str], optional)**: Name to save the file as (including extension). By default, this will be determined automatically based on the URL or Content-Disposition header.

- **workers (Optional[int], optional)**: Number of fixed concurrent download workers. By default, this will be dynamically adjusted based on the download speed. Setting this will disable dynamic worker adjustment.

> Workers here means the number of parallel connections that will be used to download the file.

- **initial_dynamic_workers (int, optional)**: Initial number of dynamic workers. Defaults to `2`.

- **dynamic_workers_update_interval (int, optional)**: Interval in seconds to update the dynamic worker count. Defaults to `5`.

- **debug (bool, optional)**: Enable debug logs. Defaults to `True`.

- **progress (bool, optional)**: Enable download progress display. Defaults to `True`.

- **progress_callback (Optional[Union[Callable[..., Any], Callable[..., Awaitable[Any]]]], optional)**:
  Callback function for download progress updates. Can be sync or async. Defaults to `None`. Setting this disables `tqdm` progress.

- **progress_args (tuple, optional)**: Additional arguments for `progress_callback`. Defaults to `()`.

- **progress_interval (int, optional)**: Time interval for progress updates in seconds. Defaults to `1`.

- **chunk_size (int, optional)**: Size of each download chunk in bytes. Defaults to `5 MB`.

- **single_threaded (bool, optional)**: Force single-threaded download. Defaults to `False`.

- **max_retries (int, optional)**: Maximum retries for each chunk/file download. Defaults to `3`.

- **timeout (int, optional)**: Timeout for each request in seconds. Defaults to `60`.

## Examples / Demos

### Getting File Info

Code from [demos/getting_file_info.py](demos/getting_file_info.py) file

```python
# This script demonstrates how to use the TechZDL package to fetch file information asynchronously.

import asyncio
from techzdl.api import TechZDL


async def main():
    techzdl = TechZDL()

    downloader = techzdl.get_downloader(url="https://link.testfile.org/bNYZFw")

    # Retrieve file information asynchronously
    file_info = await downloader.get_file_info()

    # Print the retrieved file information
    print(f"Filename: {file_info['filename']}")
    print(f"Total Size: {file_info['total_size']} bytes")


asyncio.run(main())
```

### Setting Custom File And Folder Name

Code from [demos/setting_custom_file_and_folder_name.py](demos/setting_custom_file_and_folder_name.py) file

```python
# By specifying the output directory and filename, you can organize your downloads and ensure files are saved with your preferred names.
# This is useful when you need to manage multiple downloads and want to store them in specific locations with specific names.

import asyncio
from techzdl.api import TechZDL


async def main():
    techzdl = TechZDL()

    downloader = techzdl.get_downloader(
        url="https://link.testfile.org/bNYZFw",
        output_dir="my_files",  # Custom directory where the file will be saved
        filename="my_video.mp4",  # Custom filename for the downloaded file
    )
    await downloader.start()


asyncio.run(main())
```

### Custom Headers

Code from [demos/custom_header.py](demos/custom_header.py) file

```python
# You can pass custom headers to the downloader by providing a dictionary to the 'custom_headers' parameter of the get_downloader method.
# This is useful when you need to include specific headers such as 'referer' or 'user-agent' to access the resource.

import asyncio
from techzdl.api import TechZDL


async def main():
    techzdl = TechZDL()
    headers = {
        "referer": "https://testfile.org/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    }
    downloader = techzdl.get_downloader(
        url="https://link.testfile.org/bNYZFw",
        custom_headers=headers,  # Custom headers for the downloader
    )
    await downloader.start()


asyncio.run(main())
```

### Fixed No. Of Workers

Code from [demos/fixed_no_of_workers.py](demos/fixed_no_of_workers.py) file

```python
# You can set a fixed number of workers for the downloader by passing the 'workers' parameter to the get_downloader method.
# In this context, 'workers' refers to the number of parallel connections that will be used to download the file.
# This is useful when you want to limit the number of connections to the server.
# Note: Setting this parameter will disable dynamic worker adjustments based on download speed.
# For optimal performance, you can omit this parameter and allow the library to automatically determine the number of workers.

import asyncio
from techzdl.api import TechZDL


async def main():
    techzdl = TechZDL()
    downloader = techzdl.get_downloader(
        url="https://link.testfile.org/bNYZFw",
        workers=4,  # Fixed number of workers for the downloader
    )
    await downloader.start()


asyncio.run(main())
```

### Custom Progress Callback

Code from [demos/custom_progress_callback.py](demos/custom_progress_callback.py) file

```python
# This script demonstrates how to monitor the download progress by providing a custom callback function.
# By setting the 'progress_callback' parameter, the provided function will be called periodically with the current progress.
# This will disable the default progress bar and you can use your own progress bar or any other progress indicator.
# This is useful for updating a UI, logging progress, or executing other actions based on the download status.


import asyncio
from techzdl.api import TechZDL

def progress_callback(description, done, total, arg1, arg2):
    print(f"{description}: {done}/{total} bytes downloaded", arg1, arg2)

async def main():
    techzdl = TechZDL()

    downloader = techzdl.get_downloader(
        url="https://link.testfile.org/bNYZFw",  # URL of the file to download
        progress_callback=progress_callback,  # Custom progress callback function
        progress_args=("arg1", "arg2"),  # Additional arguments to pass to the callback function
        progress_interval=2,  # Interval in seconds for calling the progress callback
    )
    await downloader.start()

asyncio.run(main())
```

### Timeouts And Max Retries

Code from [demos/timeout_and_max_retries.py](demos/timeout_and_max_retries.py) file

```python
# This script demonstrates how to configure the downloader to handle timeouts and retries.
# The 'timeout' parameter sets the maximum time (in seconds) to wait for a server response.
# The 'max_retries' parameter sets the maximum number of retry attempts for each chunk or file download.
# These settings are useful for handling unreliable network conditions or server issues.

import asyncio
from techzdl.api import TechZDL


async def main():
    techzdl = TechZDL()

    downloader = techzdl.get_downloader(
        url="https://link.testfile.org/bNYZFw",  # URL of the file to download
        timeout=30,  # Timeout in seconds for each request (default: 60 seconds)
        max_retries=5,  # Maximum number of retries for each chunk/file download (default: 3)
    )
    await downloader.start()


asyncio.run(main())
```

### Single Threaded Mode

Code from [demos/single_threaded_mode.py](demos/single_threaded_mode.py) file

```python
# The 'single_threaded' parameter can be set to True to force the downloader to operate with a single connection.
# This is useful when you want to limit resource usage or when the server does not support multiple connections.
# Note that using a single-threaded approach may affect download speed, especially for large files.
# The single-threaded mode is automatically enabled when the 'workers' parameter is set to 1 or when the server does not support range requests.

import asyncio
from techzdl.api import TechZDL


async def main():
    techzdl = TechZDL()

    downloader = techzdl.get_downloader(
        url="https://link.testfile.org/bNYZFw",
        single_threaded=True,  # Enable single-threaded mode
    )
    await downloader.start()


asyncio.run(main())
```

### Disable Debug Logs And Default Progress Bar

Code from [demos/disable_debug_logs_and_default_progress.py](demos/disable_debug_logs_and_default_progress.py) file

```python
# Setting 'debug' to False will disable detailed logging, which can be useful to reduce log clutter in production.
# Setting 'progress' to False will disable the tqdm progress bar by techzdl, which can be useful in environments where a progress bar is not needed, such as in automated scripts or background processes.
# Adding custom progress_callback will still work

import asyncio
from techzdl.api import TechZDL


async def main():
    techzdl = TechZDL()

    downloader = techzdl.get_downloader(
        url="https://link.testfile.org/bNYZFw",
        debug=False,  # Disable debug logs
        progress=False,  # Disable progress display
    )
    await downloader.start()


asyncio.run(main())
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
