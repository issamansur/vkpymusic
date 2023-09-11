from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

setup(
    name="vkpymusic",
    version="2.1.1",
    description="Python library for VK Audio (API)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    keywords="vk api music downloader python",
    author="Issa Mansur (EDEXADE)",
    author_email="issa_mansur@mail.ru",
    url="https://github.com/issamansur/vkpymusic",
    download_url="",
    packages=find_packages(),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    install_requires=["requests==2.31.0"],
)
