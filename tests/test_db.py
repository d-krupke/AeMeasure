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
        dataf = [f for f in os.listdir(path) if str(f).endswith(".data")]
        self.assertEqual(len(dataf), 1)
        db.compress()
        dataf = [f for f in os.listdir(path) if str(f).endswith(".data")]
        self.assertListEqual(dataf, [])
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

    def test_clear(self):
        entry = {"entry": "test"}
        path = "./test5"
        db = self._prepare_db(path)
        db.add(dict(entry))
        db.flush()
        self.assertListEqual(db.load(), [entry])
        db.clear()
        self.assertListEqual(db.load(), [])
        db2 = self._prepare_db(path)
        self.assertListEqual(db2.load(), [])
        self._clear_db(path)


    def test_complex(self):
        class Complex:
            def __init__(self, i):
                self.i = i

            def __str__(self):
                return "COMPLEX"

            def __hash__(self):
                return self.i
        entry = {"complex": Complex(1)}
        path = "test_complex"
        db = self._prepare_db(path)
        db.add(entry)
        db.add(Complex(3))
        db.add({Complex(1): Complex(2), Complex(4): Complex(4)})
        db.flush()
        self.assertEqual(len(db.load()), 3)

