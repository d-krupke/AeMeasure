import pathlib
import typing

import pandas as pd

from aemeasure import Database


def data_to_pandas(
    data: typing.List[typing.Dict], defaults: typing.Optional[typing.Dict] = None
):
    if not defaults:
        defaults = {}
    # find columns
    for entry in data:
        for key in entry:
            if key not in defaults:
                defaults[key] = None
    pd_data = {key: [] for key in defaults}

    for entry in data:
        entry_ = dict(defaults)
        entry_.update(entry)
        for key, value in entry_.items():
            pd_data[key].append(value)

    return pd.DataFrame(pd_data)


def read_as_pandas_table(
    path: typing.Union[str, pathlib.Path], defaults: typing.Optional[typing.Dict] = None
):
    db = Database(path)
    data = db.load()
    return data_to_pandas(data, defaults)
