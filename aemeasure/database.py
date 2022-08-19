import datetime
import json
import os.path
import pathlib
import random
import socket
import typing
import zipfile
from zipfile import ZipFile


class Database:
    """
    A simple database to dump data (dictionaries) into. Should be reasonably threadsafe
    even for slurm pools with NFS.
    """

    def __init__(self, path: typing.Union[str, pathlib.Path]):
        self.path = path
        if not os.path.exists(path):
            # Could fail in very few unlucky cases on an NFS (parallel creations)
            os.makedirs(path, exist_ok=True)
        if os.path.isfile(path):
            raise RuntimeError(
                f"Cannot create database {path} because there exists an equally named file."
            )
        self._subfile_path = self._get_unique_name()
        self._cache = []

    def _get_unique_name(self, __tries=3):
        """
        Generate a unique file name to prevent collisions of parallel processes.
        """
        if __tries <= 0:
            raise RuntimeError("Could not generate a unique file name. This is odd.")
        hostname = socket.gethostname()
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
        rand = random.randint(0, 10000)
        name = f"{timestamp}-{hostname}-{rand}.data"
        if os.path.exists(name):
            return self._get_unique_name(__tries=__tries - 1)
        return name

    def compress(self, compression=zipfile.ZIP_LZMA, compresslevel=None):
        """
        Warning: This may not be threadsafe! If you want to extract all data to
        a single file, just use 'read' and dump the output into a single json.
        """
        compr_path = os.path.join(self.path, "_compressed.zip")
        with ZipFile(compr_path, "a", compression=compression,
                     compresslevel=compresslevel) as z:
            for file_name in os.listdir(self.path):
                path = os.path.join(self.path, file_name)
                if not os.path.isfile(path) or not path.endswith(".data"):
                    continue
                z.write(path, file_name)
                os.remove(path)

    def dump(self, entries: typing.List[typing.Dict], flush=True):
        if isinstance(entries, dict):
            raise ValueError("Use 'add' to dump a single dictionary.")
        self._cache += entries
        if flush:
            self.flush()

    def add(self, entry: typing.Dict, flush=True):
        self.dump([entry], flush)

    def flush(self):
        if not self._cache:
            return
        with open(os.path.join(self.path, self._subfile_path), "a") as f:
            for data in self._cache:
                f.write(json.dumps(data) + "\n")
            self._cache.clear()

    def load(self) -> typing.List[typing.Dict]:
        data = list(self._cache)
        # load compressed data
        compr_path = os.path.join(self.path, "_compressed.zip")
        if os.path.exists(compr_path):
            with ZipFile(compr_path, "r") as z:
                for filename in z.filelist:
                    with z.open(filename, "r") as f:
                        for line in f.readlines():
                            data.append(json.loads(line))
        # load uncompressed data
        for fp in os.listdir(self.path):
            path = os.path.join(self.path, fp)
            if not os.path.isfile(path) or not path.endswith(".data"):
                continue
            with open(path, "r") as f:
                for entry in f.readlines():
                    data.append(json.loads(entry))
        return data

    def clear(self):
        """
        Clear database (cache and disk). Note that remaining data in the
        cache of other nodes may still be written.
        """
        # cache
        self._cache.clear()
        # compressed
        compr_path = os.path.join(self.path, "_compressed.zip")
        if os.path.exists(compr_path):
            os.remove(compr_path)
        # remaining .data files
        for fp in os.listdir(self.path):
            path = os.path.join(self.path, fp)
            if not os.path.isfile(path) or not str(path).endswith(".data"):
                continue
            os.remove(path)

    def __del__(self):
        self.flush()
