# TechZDL

[![PyPI Downloads](https://static.pepy.tech/personalized-badge/techzdl?period=total&units=ABBREVIATION&left_color=BLACK&right_color=GREEN&left_text=Total+Downloads)](https://pepy.tech/projects/techzdl)
[![PyPI version](https://img.shields.io/pypi/v/techzdl?color=blue&label=PyPI%20Version)](https://pypi.org/project/techzdl/)
[![License](https://img.shields.io/github/license/TechShreyash/techzdl?color=red)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)

**TechZDL** is a robust, asynchronous, multi-threaded file downloader package for Python, designed to optimize bandwidth usage and significantly fast-track your downloads.

Developed with efficiency in mind, TechZDL features **dynamic worker adjustments**, **non-blocking operations**, and **automatic retries**, making it the perfect tool for handling large-scale downloads with ease. It is capable of increasing download speeds by up to **3x** compared to standard single-threaded downloaders.

---

## 🚀 Key Features

- **⚡ Multi-threaded Downloads**: Splits files into chunks and downloads them concurrently using multiple threads for maximum speed.
- **🔄 Dynamic Worker Adjustment**: Automatically scales the number of download workers based on real-time network speed and system resources.
- **🛡️ Robust Error Handling**: Built-in automatic retries and intelligent error handling ensure downloads complete successfully even with unstable connections.
- **🔧 Custom Headers**: Full support for custom HTTP headers to handle authenticated downloads or specific server requirements.
- **⏳ Asynchronous Core**: Fully non-blocking architecture powered by `asyncio` and `aiohttp`.
- **📊 Optimized Performance**: Smart bandwidth management reduces overhead and maximizes throughput.

## 📦 Installation

Install TechZDL easily via pip:

```bash
pip install techzdl
```

To upgrade to the latest version:

```bash
pip install --upgrade techzdl
```

## 🛠️ Quick Start

Here is a simple example to get you started:

```python
import asyncio
from techzdl import TechZDL

async def main():
    # Initialize the downloader
    downloader = TechZDL(url="https://link.testfile.org/bNYZFw")
    
    # Start the download
    await downloader.start()

if __name__ == "__main__":
    asyncio.run(main())
```

> **Demo Video**:
> https://github.com/TechShreyash/techzdl/assets/82265247/33267e71-2b41-4dd1-b306-c87a197a3b57

## 📖 Documentation

For more advanced usage, configuration options, and API details, please refer to the [DOCS.md](DOCS.md) file.

You can also find example scripts in the [demos](demos) directory.

## 🤝 Support & Community

- **Telegram Channel**: [Join TechZBots](https://telegram.me/TechZBots) for updates.
- **Support Group**: [Join Support Group](https://telegram.me/TechZBots_Support) for help and discussions.
- **Email**: [techshreyash123@gmail.com](mailto:techshreyash123@gmail.com)

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---
*Built with ❤️ by [TechShreyash](https://github.com/TechShreyash)*
