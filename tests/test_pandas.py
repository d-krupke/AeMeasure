import unittest
import os
import shutil

from aemeasure import MeasurementSeries, read_as_pandas_table


class TestPandas(unittest.TestCase):
    def _clear_db(self, path):
        if os.path.exists(path):
            shutil.rmtree(path)

    def test_all(self):
        path = "./test_pandas_1"
        self._clear_db(path)
        with MeasurementSeries(path) as ms:
            with ms.measurement() as m:
                m["test"] = 1
                m.save_metadata()
            with ms.measurement() as m:
                m["test"] = 2
                m.save_metadata()
        t = read_as_pandas_table(path)
        self.assertEqual(len(t), 2)
        self.assertTrue("test" in t.columns)
