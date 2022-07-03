import os
import shutil
import unittest

from aemeasure import Database


class TestDb(unittest.TestCase):
    def _prepare_db(self, path):
        self._clear_db(path)
        return Database(path)

    def _clear_db(self, path):
        if os.path.exists(path):
            shutil.rmtree(path)

    def test_write(self):
        path = "./test1"
        db = self._prepare_db(path)
        db.add({"entry": "test"})
        db.flush()
        self._clear_db(path)

    def test_compress(self):
        path = "./test2"
        db = self._prepare_db(path)
        db.add({"entry": "test"})
        db.flush()
        db.compress()
        self._clear_db(path)

    def test_load(self):
        entry = {"entry": "test"}
        path = "./test3"
        db = self._prepare_db(path)
        db.add(dict(entry))
        self.assertListEqual(db.load(), [entry])
        db.flush()
        self.assertListEqual(db.load(), [entry])
        self._clear_db(path)

    def test_load2(self):
        entry = {"entry": "test"}
        path = "./test4"
        db = self._prepare_db(path)
        db.add(dict(entry))
        db.flush()
        db.compress()
        self.assertListEqual(db.load(), [entry])
        db2 = Database(path)
        self.assertListEqual(db2.load(), [entry])
        self._clear_db(path)
