import pathlib
import typing

from aemeasure import Measurement
from aemeasure.database import Database


class MeasurementSeries:
    def __init__(self, path: typing.Union[str, pathlib.Path], cache=True):
        self.db = Database(path)
        self.cache = cache

    def measurement(self, **kwargs) -> Measurement:
        return Measurement(self.db, cache=self.cache, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.flush()
