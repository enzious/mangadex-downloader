# MIT License

# Copyright (c) 2022 Rahman Yusuf

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
import re
import logging
import sys
from pathlib import Path

from .utils import delete_file, QueueWorker
from .errors import MangaDexException
from .config import config
from . import __repository__, __url_repository__

try:
    import orjson
except ImportError:
    HAVE_ORJSON = False
else:
    HAVE_ORJSON = True

log = logging.getLogger(__name__)

class _BasicInfo:
    @property
    def data(self):
        raise NotImplementedError

class _ImageInfo(_BasicInfo):
    def __init__(self, data) -> None:
        self.name = data["name"]
        self.hash = data["hash"]
        self.chapter_id = data["chapter_id"]

    @property
    def data(self):
        return {
            "name": self.name,
            "hash": self.hash,
            "chapter_id": self.chapter_id
        }
    
    def __eq__(self, o) -> bool:
        return self.data == o.data

class _ChapterInfo(_BasicInfo):
    def __init__(self, data):
        self.name = data["name"]
        self.id = data["id"]
    
    @property
    def data(self):
        return {
            "name": self.name,
            "id": self.id
        }
    
    def __eq__(self, o) -> bool:
        if isinstance(o, str):
            return self.id == o
        elif isinstance(o, _ChapterInfo):
            return self.data == o.data

class _FileInfo(_BasicInfo):
    def __init__(self, data):
        self.name = data["name"]
        self.id = data["id"]
        self.hash = data["hash"]
        self.completed = data["completed"]

        images = data["images"]
        if images is not None:
            self.images = [_ImageInfo(i) for i in data["images"]]
        else:
            self.images = images

        chapters = data["chapters"]
        if chapters is not None:
            self.chapters = [_ChapterInfo(i) for i in data["chapters"]]
        else:
            self.chapters = chapters

    @property
    def data(self):
        return {
            "name": self.name,
            "id": self.id,
            "hash": self.hash,
            "completed": self.completed,
            "images": self.images,
            "chapters": self.chapters
        }

    def __eq__(self, o) -> bool:
        return self.data == o.data

# Use orjson custom encoder
if HAVE_ORJSON:
    def DownloadTrackerJSONEncoder(o):
        if isinstance(o, _BasicInfo):
            return o.data

        raise TypeError(f'Object of type {o.__class__.__name__} '
                        f'is not JSON serializable')
else:
    class DownloadTrackerJSONEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, _BasicInfo):
                return o.data
            
            return super().default(o)

json_lib = orjson if HAVE_ORJSON else json

class DownloadTracker:
    """An tracker for downloaded manga
    
    This will track downloaded volume and chapters from a manga. 
    The tracker will be put in downloaded manga directory, named `downloaded-{format}.json`. 
    (ex: downloaded-raw.json, downloaded-raw-volume.json, etc)
    The schema will look like this

    {
        "comment": [
            "DO NOT EDIT THIS FILE",
            "UNLESS YOU KNOW WHAT YOU'RE DOING"
        ],
        "files": [
            // For raw formats
            // (raw, raw-volume, raw-single)
            {
                "name": "Vol. 1 Ch. 20",
                "id": "a2f32e55-ca66-462b-92ad-de17dbe16b61",
                "hash": null,
                completed: true,
                images: [
                    {
                        "name": "1.png",
                        "hash": "362dd913aaf46c1236980df92f832bc8985f788a00dc73c0a058d29b5c4cdafb"
                    },
                    {
                        "name": "2.png",
                        "hash": "ee70cc1ec3082418e14900fc44467e527ccba2d3e75c79f70ab20e4402343635",
                    },
                    {
                        "name": "3.png",
                        "hash": "6bedfd6f6292598b500d603e6670626187dd6395195fcdf774ffb9162968bd3a",
                    },
                    {
                        "name": "4.png",
                        "hash": "536e0c5dde0cb57bae66b56e713f5443e61471efd83798a40a7f2ca256e8054e",
                    },
                    {
                        "name": "5.png",
                        "hash": "80005e5c69f48a022e41527079bb687de3bcbd1cb0fd8e85dcedd36d119dc5af",
                    },
                ],
                chapters: null
            },

            // For any formats that is NOT raw formats
            // (cbz, cb7, epub, pdf)
            {
                "name": "Vol. 1 Ch. 20.cbz",
                "id": "a2f32e55-ca66-462b-92ad-de17dbe16b61",
                "hash": "df59b431b1a049c4c2aa0619115a74ae67b0465f977cff19f2ed0dc1ef723bb7",
                completed: true,
                "images": null,
                "chapters": null
            },

            // For volume and single formats (again, this is not for raw formats)
            {
                "name": "Volume. 1.cbz",
                "id": null,
                "hash": "269568b4055aeb5076c978c8d56e8b3342d5580eb7d180f541a08796f2979f47",
                "images": null,
                completed: true,
                "chapters": [
                    "a2f32e55-ca66-462b-92ad-de17dbe16b61",
                    "51507eab-585f-46ce-bf87-17b3e0d8aed9",
                    "de889522-918b-47d6-acbf-6f8bd0b93c42",
                    "b07d5b64-5192-42be-b035-e942f47d478e",
                ]
            }
        ]
    }
    """
    _comment = [
        "DO NOT EDIT THIS FILE",
        "UNLESS YOU KNOW WHAT YOU'RE DOING"
    ]

    def __init__(self, fmt, path):
        self.path = Path(path)
        self.format = fmt
        self.file = self.path / f"downloaded-{fmt}.json"

        self.data = {}
        self.queue = QueueWorker()

        if config.no_track:
            # Do not start queue worker if no track is enabled
            # We wasting a thread if we start the queue worker

            # This won't write a file
            self.data = self._write_new()
            return

        self.queue.start()

        if HAVE_ORJSON:
            type_data = "bytes"
        else:
            type_data = "text"
        
        self.func_write = getattr(self.file, f"write_{type_data}")
        self.func_read = getattr(self.file, f"read_{type_data}")

        self._load()

    @property
    def disabled(self):
        """Is download tracker disabled ?
        
        This is just to prevent 'circular imports' problem
        """
        return config.no_track

    def shutdown(self):
        """Since :class:`DownloadTracker` is working in a asynchronous mode. 
        The thread need to be shutdown manually
        """
        if self.disabled:
            return

        self.queue.shutdown()

    def recreate(self):
        """Remove the old file and re-create new one"""
        if self.disabled:
            return

        delete_file(self.file)
        data = self._write_new()

        self.data = data

    def _write_new(self):
        """Write new tracker to JSON file"""
        default_data = {
            "comment": self._comment,
            "files": []
        }

        if not self.disabled:
            self.file.write_text(
                json.dumps(default_data)
            )

        return default_data

    def _write(self, data):
        if self.disabled:
            return

        kwargs = {}
        kwargs["default" if HAVE_ORJSON else "cls"] = DownloadTrackerJSONEncoder

        job = lambda: self.func_write(
            json_lib.dumps(data, **kwargs)
        )

        # Write data asynchronously to improve performance
        self.queue.submit(job, blocking=False)

    @property
    def empty(self):
        return len(self.data["files"]) == 0

    def get(self, name) -> _FileInfo:
        """Retrieve file_info from given name"""
        files = self.data["files"]
        file_info = None

        for fi in filter(lambda x: x.name == name, files):
            file_info = fi
        
        return file_info

    def remove_file_info_from_name(self, name):
        files = self.data["files"]

        iterator = filter(lambda x: x.name == name, files)
        for fi in iterator:
            files.remove(fi)

    def add_file_info(
        self,
        name,
        id=None,
        hash=None,
        null_images=True,
        null_chapters=True
    ):
        files = self.data["files"]

        file_info = _FileInfo(
            {
                "name": name,
                "id": id,
                "hash": hash,
                "completed": False,
                "images": None if null_images else [],
                "chapters": None if null_chapters else [],
            }
        )

        files.append(file_info)
        self._write(self.data)

        return file_info

    def add_image_info(self, name, img_name, hash, chap_id):
        file_info = self.get(name)

        im_info = _ImageInfo(
            {"name": img_name, "hash": hash, "chapter_id": chap_id}
        )
        try:
            file_info.images.remove(im_info) # to prevent duplicate
        except ValueError:
            pass

        file_info.images.append(im_info)

        # Reorder images
        def get_page_image(im_info):
            re_page = r"(?P<page>[0-9]{1,})\..{1,}"

            found = re.search(re_page, im_info.name)
            if found is None:
                raise Exception(
                    f"An error occurred when getting page from filename '{im_info.name}'. " \
                    f"Please report it to {__url_repository__}/{__repository__}/issues"
                )
            
            page = int(found.group("page"))
            return page
        
        file_info.images = sorted(file_info.images, key=get_page_image)
        self._write(self.data)

    def add_chapter_info(self, name, chapter_name, chapter_id):
        file_info = self.get(name)

        if chapter_id in file_info.chapters:
            # To prevent duplicate
            return
        
        ch_info = _ChapterInfo(
            {"name": chapter_name, "id": chapter_id}
        )

        file_info.chapters.append(ch_info)
        self._write(self.data)
    
    def toggle_complete(self, name, is_complete):
        file_info = self.get(name)

        file_info.completed = is_complete
        self._write(self.data)

    def _check_data(self, data):
        """Check DownloadTracker data
        
        Return ``True`` if it's valid data, otherwise ``False``
        """
        # Check for `files` key
        try:
            files = data["files"]
        except KeyError:
            # Malformed data
            return False
        
        # TODO: Add extra checking for each files
        new_files = []
        for index, file in enumerate(files):
            try:
                fi = _FileInfo(file)
            except KeyError as e:
                log.error(
                    f"Malformed tracker file structure in '{self.path}' at index {index}. " \
                    f"Exception raised: {e}" \
                     "Re-creating new DownloadTracker file...." 
                )
                delete_file(self.path)
                return self._write_new()
            
            # Check duplicate
            if fi in new_files:
                log.warning(
                    f"Duplicate '{fi.name}' found in tracker file ('{self.path}') at index {index}, " \
                    "Removing duplicates..."
                )

                # Ignored, the _FileInfo won't be written
                continue
            
            new_files.append(fi)

        data["files"] = new_files
        return data

    def _load(self):
        """Load DownloadTracker data
        
        If file tracker doesn't exists it will create a new tracker and fill it with empty value.
        Otherwise it will read and check the file.

        If the tracker contains invalid data (either malformed data or fail to parse JSON), 
        it will re-create the tracker with empty value.
        """
        if not self.file.exists():
            self.data = self._write_new()
            return
        
        try:
            data = json_lib.loads(self.func_read())
        except json.JSONDecodeError:
            self._write_new()
            return
        
        data = self._check_data(data)

        self._write(data)
        self.data = data