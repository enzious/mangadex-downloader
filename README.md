[![pypi-total-downloads](https://img.shields.io/pypi/dm/mangadex-downloader?label=DOWNLOADS&style=for-the-badge)](https://pypi.org/project/mangadex-downloader)
[![python-ver](https://img.shields.io/pypi/pyversions/mangadex-downloader?style=for-the-badge)](https://pypi.org/project/mangadex-downloader)
[![pypi-release-ver](https://img.shields.io/pypi/v/mangadex-downloader?style=for-the-badge)](https://pypi.org/project/mangadex-downloader)

# mangadex-downloader

[![Indonesian](https://img.shields.io/badge/Language-Indonesian-blue.svg)](https://github.com/mansuf/mangadex-downloader/blob/main/README.id.md)
[![Turkish](https://img.shields.io/badge/Language-Turkish-blue.svg)](https://github.com/mansuf/mangadex-downloader/blob/main/README.tr.md)

A command-line tool to download manga from [MangaDex](https://mangadex.org/), written in [Python](https://www.python.org/).

## Table of Contents

- [Key Features](#key-features)
- [Supported formats](#supported-formats)
- [Installation](#installation)
    - [Python Package Index (PyPI)](#installation-pypi)
    - [Bundled executable](#installation-bundled-executable)
    - [Development version](#installation-development-version)
- [Usage](#usage)
    - [PyPI version](#usage-pypi-version)
    - [Bundled executable version](#usage-bundled-executable-version)
- [Contributing](#contributing)
- [Donation](#donation)
- [Links](#links)
- [Disclaimer](#disclaimer)

## Key Features <a id="key-features"></a>

- Download manga, chapter, or list directly from MangaDex
- Download manga or list from user library
- Find and download MangaDex URLs from MangaDex forums ([https://forums.mangadex.org/](https://forums.mangadex.org/))
- Batch download support
- Old MangaDex url support
- Scanlation groups filter support
- Authentication support
- Control how many chapters and pages you want to download
- Compressed images support
- HTTP / SOCKS proxy support
- DNS-over-HTTPS support
- Multi languages support
- Save as raw images, EPUB, PDF, Comic Book Archive (.cbz or .cb7)

***And ability to not download oneshot chapter***

## Supported formats <a id="supported-formats"></a>

[Read here](https://mangadex-dl.mansuf.link/en/latest/formats.html) for more info.

## Installation <a id="installation"></a>

What will you need:

- Python 3.8.x or up with Pip (if you are in Windows, you can download bundled executable. [See this instructions how to install it](#installation-bundled-executable))

That's it.

### Python Package Index (PyPI) <a id="installation-pypi"></a>

Installing mangadex-downloader is easy, as long as you have requirements above.

```shell
# For Windows
py -3 -m pip install mangadex-downloader

# For Linux / Mac OS
python3 -m pip install mangadex-downloader
```

You can also install optional dependencies

- [py7zr](https://pypi.org/project/py7zr/) for cb7 support
- [orjson](https://pypi.org/project/orjson/) for maximum performance (fast JSON library)
- [lxml](https://pypi.org/project/lxml/) for EPUB support

Or you can install all optional dependencies

```shell
# For Windows
py -3 -m pip install mangadex-downloader[optional]

# For Mac OS / Linux
python3 -m pip install mangadex-downloader[optional]
```

There you go, easy ain't it ?.

### Bundled executable <a id="installation-bundled-executable"></a>

**NOTE:** This installation only apply to Windows.

Because this is bundled executable, Python are not required to install.

Steps:

- Download latest version here -> https://github.com/mansuf/mangadex-downloader/releases
- Extract it.
- That's it ! You have successfully install mangadex-downloader. 
[See this instructions to run mangadex-downloader](#usage-bundled-executable-version)

### Development version <a id="installation-development-version"></a>

**NOTE:** You must have git installed. If you don't have it, install it from here https://git-scm.com/.

```shell
git clone https://github.com/mansuf/mangadex-downloader.git
cd mangadex-downloader
python setup.py install # or "pip install ."
```

## Usage <a id="usage"></a>

### PyPI version <a id="usage-pypi-version"></a>

```shell

mangadex-dl "insert MangaDex URL here" 
# or
mangadex-downloader "insert MangaDex URL here" 

# Use this if "mangadex-dl" or "mangadex-downloader" didn't work

# For Windows
py -3 -m mangadex_downloader "insert MangaDex URL here" 

# For Linux / Mac OS
python3 -m mangadex_downloader "insert MangaDex URL here" 
```

### Bundled executable version <a id="usage-bundled-executable-version"></a>

- Navigate to folder where you downloaded mangadex-downloader
- Open "start cmd.bat" (don't worry it's not a virus, it will open a command prompt)

![example_start_cmd](https://raw.githubusercontent.com/mansuf/mangadex-downloader/main/assets/example_start_cmd.png)

- And then start using mangadex-downloader, see example below:

```shell
mangadex-dl.exe "insert MangaDex URL here" 
```

![example_usage_executable](https://raw.githubusercontent.com/mansuf/mangadex-downloader/main/assets/example_usage_executable.png)

For more example usage, you can [read here](https://mangadex-dl.mansuf.link/en/stable/cli_usage/index.html)

For more info about CLI options, you can [read here](https://mangadex-dl.mansuf.link/en/stable/cli_ref/index.html)

## Contributing <a id="contributing"></a>

See [CONTRIBUTING.md](https://github.com/mansuf/mangadex-downloader/blob/main/CONTRIBUTING.md) for more info

## Donation <a id="donation"></a>

If you like this project, please consider donate to one of these websites:

- [Sociabuzz](https://sociabuzz.com/mansuf/donate)
- [Github Sponsor](https://github.com/sponsors/mansuf)

Any donation amount will be appreciated 💖

## Links <a id="links"></a>

- [PyPI](https://pypi.org/project/mangadex-downloader/)
- [Docs](https://mangadex-dl.mansuf.link)

## Disclaimer <a id="disclaimer"></a>

mangadex-downloader are not affiliated with MangaDex. Also, the current maintainer ([@mansuf](https://github.com/mansuf)) is not a MangaDex dev
