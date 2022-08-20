import logging
import pathlib
import typing

from aemeasure import Measurement
from aemeasure.database import Database


class MeasurementSeries:
    """
    A series of measurements.
    """

    def __init__(self, db: typing.Union[Database, str, pathlib.Path],
                 stdout: typing.Optional[str] = "stdout",
                 stderr: typing.Optional[str] = "stderr",
                 metadata: bool = True,
                 cache: bool = True):
        """
        By default, the series will save
        :param path: Path to the database or database itself.
        :param stdout: Capture stdout under this label for every measurement. Set to
                        `None` if you don't want this feature.
        :param stderr: Capture stderr under this label for every measurement. Set to
                        `None` if your don't want this feature.
        :param metadata: Automatically save metadata.
        :param cache: Wait until the end of the series to flush the database to disk.
        """
        self.db = db if isinstance(db, Database) else Database(db)
        self.cache = cache
        self._stderr = stderr
        self._stdout = stdout
        self._save_metadata = metadata

    def measurement(self, cache: typing.Optional[bool] = None) -> Measurement:
        """
        Create a new measurement. A measurement should be for example
        an algorithm solving a single instance. Note that this is not
        meant for micro-benchmarks: If you try to measure running times
        significantly below 1s, you should use another tool.
        capture_stdout: Saves the output of stdout into this field. Note that
        saving the output can use up a significant amount of disk storage.
        capture_stderr: Saves the output of stderr into this field.
        :param cache: If set to true, the entry will only be saved to disk when
        the datbase is flushed or closed. If set to false, every measurement
        will directly be written to disk. If not set, the top level decision
        is used.
        """
        cache = self.cache if cache is None else cache
        return Measurement(self.db,
                           capture_stdout=self._stdout,
                           capture_stderr=self._stderr,
                           save_metadata=self._save_metadata,
                           cache=cache)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.getLogger("AeMeasure").info("Saving series.")
        self.db.flush()
