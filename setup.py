# setup.py
from setuptools import setup, find_packages

setup(
    name="techzdl",
    version="1.2.1",
    author="TechShreyash",
    author_email="techshreyash123@gmail.com",
    description="A simple yet powerfull file downloader package for python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/TechShreyash/techzdl",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=["aiohttp", "aiofiles", "tqdm", "curl_cffi"],
    license="MIT",
)
