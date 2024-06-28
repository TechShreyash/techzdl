# TechZDL v1.2.2

TechZDL is a powerful file downloader package for Python that supports multi-threaded downloads, dynamic worker adjustments based on network speed, custom headers, and more.

<img src="https://stats.techzbots.co/api/views_badge?page=https%3A%2F%2Fgithub.com%2FTechShreyash%2Ftechzdl&color1=20c488&color2=eb0205&label=Total%20Repo%20Views&counter_type=1" alt="Total Repo Views">

## Features

- **Multi-threaded downloads**: Efficiently download files using multiple threads.
- **Dynamic worker adjustments**: Automatically adjusts the number of workers based on network speed.
- **Custom headers**: Add custom headers to your download requests.
- **Error handling**: Robust error handling and retry mechanisms.
- **Asynchronous support**: Fully asynchronous for non-blocking operations.

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

## More Examples / Demos

Check the [demos](demos) folder for more examples and detailed demonstrations of file downloading using the TechZDL package. The demos include more information about the various features of TechZDL and how to use them effectively.

## Documentation

Check [DOCS.md](DOCS.md) for detailed documentation of the TechZDL package.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For inquiries or support, join our [Telegram Support Group](https://telegram.me/TechZBots_Support) or email [techshreyash123@gmail.com](mailto:techshreyash123@gmail.com).

## Acknowledgements

Thanks to all contributors and users for their support and feedback.

## Stay Connected

- Join our [Telegram Channel](https://telegram.me/TechZBots)
