# TechZDL Documentation

## Table of Contents
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Class: TechZDL](#class-techzdl)
    - [Arguments](#arguments)
    - [Attributes](#attributes)
- [Methods](#methods)
    - [start()](#start)
    - [stop()](#stop)
    - [get_file_info()](#get_file_info)
- [Support](#support)

---

## Installation

You can install TechZDL using pip:

```bash
pip install techzdl
```

To update to the latest version:

```bash
pip install --upgrade techzdl
```

If you encounter issues updating, you can force a reinstall:

```bash
pip install --upgrade --force-reinstall techzdl
```

---

## Quick Start
Here is a basic example of how to use TechZDL:

```python
import asyncio
from techzdl import TechZDL

async def main():
    # Initialize downloader
    downloader = TechZDL(url="https://link.testfile.org/bNYZFw")
    
    # Start download
    await downloader.start()

if __name__ == "__main__":
    asyncio.run(main())
```

> **Demo Video**: [Watch on GitHub](https://github.com/TechShreyash/techzdl/assets/82265247/33267e71-2b41-4dd1-b306-c87a197a3b57)

For more examples, check the [demos](demos) folder in the repository.

---

## Class: TechZDL

You can import the class as follows:

```python
from techzdl import TechZDL
```

### Arguments

| Argument | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `url` | `str` | **Required** | The direct URL of the file to download. |
| `custom_headers` | `dict` | `None` | Custom HTTP headers to include in the request. |
| `output_dir` | `str` \| `Path` | `"downloads"` | Directory where the file will be saved. |
| `filename` | `str` | `None` | Name of the file. If not set, it's determined automatically. |
| `workers` | `int` | `None` | Fixed number of download workers. Setting this disables dynamic adjustment. |
| `initial_dynamic_workers` | `int` | `2` | Initial number of workers if dynamic adjustment is active. |
| `dynamic_workers_update_interval` | `int` | `5` | Seconds between checking/updating worker count. |
| `debug` | `bool` | `True` | Enable or disable debug logging. |
| `progress` | `bool` | `True` | Enable basic progress display (tqdm). |
| `progress_callback` | `Callable` | `None` | Custom callback for progress updates. Overrides `progress`. |
| `progress_args` | `tuple` | `()` | Additional arguments to pass to the `progress_callback`. |
| `progress_interval` | `int` | `1` | Interval (in seconds) for progress updates. |
| `chunk_size` | `int` | `5MB` | Size of each download chunk in bytes. |
| `single_threaded` | `bool` | `False` | Force standard single-threaded download. |
| `max_retries` | `int` | `3` | Maximum retries for file/chunk downloads. |

### Attributes

| Attribute | Type | Description |
| :--- | :--- | :--- |
| `id` | `str` | Unique identifier for the downloader instance. |
| `is_running` | `bool` | `True` if the download process is currently active. |
| `filename` | `str` | Final name of the downloaded file. |
| `output_path` | `Path` | Full path to the downloaded file. |
| `download_success` | `bool` | `True` if the download completed successfully. |
| `download_error` | `Exception` | Contains the exception if an error occurred. |

---

## Methods

### `start()`

Starts the download process.

```python
await downloader.start(in_background=False)
```

**Arguments:**
- `in_background` (`bool`): If `True`, runs the download in the background and returns `None` immediately. If `False`, waits for completion.

**Returns:**
- `Path`: The path to the downloaded file (only if `in_background=False`).

### `stop()`

Forcefully stops the current download process.

```python
await downloader.stop()
```

### `get_file_info()`

Fetches metadata about the file without downloading it.

```python
info = await downloader.get_file_info()
```

**Returns:** (`dict`)
- `filename`: The name of the file.
- `total_size`: The size of the file in bytes.

---

## Support

- **Telegram Support Group**: [Join Here](https://telegram.me/TechZBots_Support)
- **Email**: [techshreyash123@gmail.com](mailto:techshreyash123@gmail.com)
- **Telegram Channel**: [TechZBots](https://telegram.me/TechZBots)
