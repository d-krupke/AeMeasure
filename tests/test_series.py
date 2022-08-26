import os
import shutil
import unittest

from aemeasure import Database, MeasurementSeries


class SeriesTest(unittest.TestCase):
    def _prepare_db(self, path):
        self._clear_db(path)
        return Database(path)

    def _clear_db(self, path):
        if os.path.exists(path):
            shutil.rmtree(path)

    def test_1(self):
        self._clear_db("./test_db")
        self._prepare_db("./test_db")
        with MeasurementSeries("./test_db") as ms:
            with ms.measurement() as m:
                m["test"] = 1
        db = Database("./test_db")
        self.assertEqual(len(db.load()), 1)
        self.assertEqual(db.load()[0]["test"], 1)
        self._clear_db("./test_db")

    def test_2(self):
        self._clear_db("./test_db")
        self._prepare_db("./test_db")
        def f():
            with MeasurementSeries("./test_db") as ms:
                with ms.measurement() as m1:
                    m1["test"] = 1
                with ms.measurement() as m2:
                    raise ValueError()
        self.assertRaises(ValueError, f)
        db = Database("./test_db")
        self.assertEqual(len(db.load()), 1)
        self.assertEqual(db.load()[0]["test"], 1)
        self._clear_db("./test_db")