import datetime
import logging
import os
import socket
import sys
import typing

from .database import Database
from .utils.capture import OutputCopy
from .utils.git import get_git_revision


class Measurement(dict):
    _measurement_stack = []
    _git_revision = get_git_revision()

    @staticmethod
    def last() -> dict:
        return Measurement._measurement_stack[-1]

    def time(self, timer=None) -> datetime.timedelta:
        if timer is None:
            return datetime.datetime.now() - self._time
        else:
            return datetime.datetime.now() - self._timer[timer]

    def save_timestamp(self, key="timestamp"):
        self[key] = datetime.datetime.now().isoformat()

    def save_seconds(self, key="runtime", timer=None):
        v = self.time(timer).total_seconds()
        self[key] = v
        return v

    def save_hostname(self, key="hostname"):
        v = socket.gethostname()
        self[key] = v
        return v

    def save_argv(self, key="argv"):
        if sys.argv:
            v = " ".join(sys.argv)
            self[key] = v
            return v
        else:
            self[key] = None
            return None

    def save_git_revision(self, key="git_revision") -> str:
        self[key] = self._git_revision
        return self._git_revision

    def save_metadata(self):
        self.save_seconds()
        self.save_timestamp()
        self.save_hostname()
        self.save_argv()
        self.save_git_revision()
        self.save_cwd()

    def start_timer(self, name: str):
        self._timer[name] = datetime.datetime.now()

    def __init__(
            self,
            db: typing.Union[Database, str],
            capture_stdout: typing.Optional[str] = None,
            capture_stderr: typing.Optional[str] = None,
            save_metadata = False,
            cache=False,
    ):
        super().__init__()
        self._time = datetime.datetime.now()
        if isinstance(db, Database):
            self._db = db
        else:
            self._db = Database(db)
        self._timer = dict()
        self._capture_stdout = capture_stdout
        self._capture_stderr = capture_stderr
        self._cache = cache
        self._save_metadata = save_metadata

    def __enter__(self):
        self._measurement_stack.append(self)
        self.start_capture()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_capture()
        if self._save_metadata:
            self.save_metadata()
        if not exc_type:
            self.write()
        else:
            logging.getLogger("AeMeasure").warning("Do not save measurement due to exception.")
        e = self._measurement_stack.pop()
        assert e is self

    def save_cwd(self, label="cwd"):
        self[label] = os.getcwd()

    def start_capture(self):
        if self._capture_stdout:
            sys.stdout = OutputCopy(sys.stdout)
        if self._capture_stderr:
            sys.stderr = OutputCopy(sys.stderr)

    def stop_capture(self):
        if self._capture_stdout:
            self[self._capture_stdout] = sys.stdout.getvalue()
            sys.stdout = sys.stdout.wrapped_stream
        if self._capture_stderr:
            self[self._capture_stderr] = sys.stderr.getvalue()
            sys.stderr = sys.stderr.wrapped_stream

    def write(self):
        self._db.dump([self], self._cache)
