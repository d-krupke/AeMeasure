import pathlib
import typing

from aemeasure import Measurement
from aemeasure.database import Database


class MeasurementSeries:
    """
    A series of measurements.
    """
    def __init__(self, path: typing.Union[str, pathlib.Path], cache=True):
        self.db = Database(path)
        self.cache = cache

    def measurement(self,
                    capture_stdout: typing.Optional[str] = None,
                    capture_stderr: typing.Optional[str] = None,
                    cache: typing.Optional[bool]=None) -> Measurement:
        """
        Create a new measurement. A measurement should be for example
        an algorithm solving a single instance. Note that this is not
        meant for micro-benchmarks: If you try to measure running times
        significantly below 1s, you should use another tool.
        capture_stdout: Saves the output of stdout into this field. Note that
        saving the output can use up a significant amount of disk storage.
        capture_stderr: Saves the output of stderr into this field.
        cache: If set to true, the entry will only be saved to disk when
        the datbase is flushed or closed. If set to false, every measurement
        will directly be written to disk. If not set, the top level decision
        is used.
        """
        cache = self.cache if cache is None else cache
        return Measurement(self.db, capture_stdout=capture_stdout,
                           capture_stderr=capture_stderr,
                           cache=cache)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.flush()
