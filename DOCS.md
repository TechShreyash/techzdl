# TechZDL v1.2.6 Documentation

## Installation

You can install TechZDL using pip:

```sh
pip install techzdl
```

To update TechZDL to the latest version, use:

```sh
pip install --upgrade techzdl
```

**Note**: If it doesn't update to the latest version, use:

```sh
pip install --upgrade --force-reinstall techzdl
```

## Usage

Here's a basic example of how to use the TechZDL package:

### Basic Usage

```python
import asyncio
from techzdl import TechZDL

async def main():
    downloader = TechZDL(url="https://link.testfile.org/bNYZFw")
    await downloader.start()

asyncio.run(main())
```

https://github.com/TechShreyash/techzdl/assets/82265247/33267e71-2b41-4dd1-b306-c87a197a3b57

## The TechZDL Class

You can import it using:

```python
from techzdl import TechZDL
```

### Arguments

Here is a list of arguments you can pass to the `TechZDL` class to modify your downloading process:

- `url` `(str)`: URL of the file to download.
- `custom_headers` `(Optional[dict])`: Custom headers to send with the request. Defaults to None.
- `output_dir` `(Union[str, Path])`: Directory where the file will be saved. Defaults to "downloads".
- `filename` `(Optional[str])`: Name to save the file as (including extension). By default, this will be determined automatically.
- `workers` `(Optional[int])`: Number of fixed concurrent download workers. By default, this will be dynamically adjusted based on the download speed. Setting this will disable dynamic worker adjustment.
- `initial_dynamic_workers` `(int)`: Initial number of dynamic workers. Defaults to 2.
- `dynamic_workers_update_interval` `(int)`: Interval in seconds to update dynamic worker count. Defaults to 5.
- `debug` `(bool)`: Enable debug logs. Defaults to True.
- `progress` `(bool)`: Enable download progress display. Defaults to True.
- `progress_callback` `(Optional[Callable[..., Any]])`: Callback function for download progress updates. Can be synchronous. Defaults to None. Setting this disables tqdm progress.
- `progress_args` `(tuple)`: Additional arguments for `progress_callback`. Defaults to ().
- `progress_interval` `(int)`: Time interval for progress updates in seconds. Defaults to 1.
- `chunk_size` `(int)`: Size of each download chunk in bytes. Defaults to 5 MB.
- `single_threaded` `(bool)`: Force single-threaded download. Defaults to False.
- `max_retries` `(int)`: Maximum retries for each chunk/file download. Defaults to 3.

### Attributes

- **`id`** `(str)`: A unique identifier for the TechZDL downloader object, generated at the time of object creation.
- **`is_running`** `(bool)`: Indicates if the download process is currently running. `True` if the process is active, otherwise `False`.
- **`filename`** `(str)`: The name of the downloaded file. Can be accessed after downloading starts.
- **`output_path`** `(Path)`: The file path where the downloaded file is stored. Can be accessed after downloading starts.

> **Note:** `Path` refers to the `Path` object from the `pathlib` library.
```python
from pathlib import Path
```

- **`download_success`** `(bool)`: `True` if the file was downloaded successfully, otherwise `False`. Can be accessed after downloading completes or fails.
- **`download_error`** `(Exception or None)`: Contains the exception if an error occurred during the download process, otherwise `None`. Can be accessed after downloading completes or fails.

> **Note:** The attributes `output_path`, `download_success`, and `download_error` are particularly useful when using the background download mode, as errors raised and the file path cannot be directly accessed.

### Example Usage

```python
import asyncio
from techzdl import TechZDL

async def main():
    downloader = TechZDL(url="https://link.testfile.org/bNYZFw")
    print(downloader.id)
    print(downloader.is_running)

asyncio.run(main())
```

> **Note:** While you can access the above attributes, modifying them directly is not recommended as it may cause issues with the downloader object.

### Example Usage

```python
import asyncio
from techzdl import TechZDL

async def main():
    downloader = TechZDL(url="https://link.testfile.org/bNYZFw")
    print(downloader.id)
    print(downloader.is_running)

asyncio.run(main())
```

> **Note:** While you can access the above attributes, modifying them directly is not recommended as it may cause issues with the downloader object.

## Methods

### TechZDL.start()

Starts the download process.

#### Args

- `in_background` `(bool, optional)`: Run the download process in the background. Defaults to False.

#### Returns

- `filepath` `(Path)`: Path to the downloaded file.


### TechZDL.stop()

Forcefully stops the download process.

### TechZDL.get_file_info()

Fetches file information from the server.

#### Returns

- `dict`: File information in the format `{"filename": str, "total_size": int}`.

  - `filename` `(str)`: Name as returned by the server or determined by the TechZDL package using response headers and download URL.
  - `total_size` `(int)`: Total size of the file in bytes.

## Support

For inquiries or support, join our [Telegram Support Group](https://telegram.me/TechZBots_Support) or email [techshreyash123@gmail.com](mailto:techshreyash123@gmail.com).

## Stay Connected

- Join our [Telegram Channel](https://telegram.me/TechZBots)
