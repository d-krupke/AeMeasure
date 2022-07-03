# AeMeasure

This module has been developed to save (macro-)benchmarks of algorithms in a simple and
dynamic way. The primary features are:
* Saving metadata such as Git-Revision, hostname, etc.
* No requirement of a data scheme.
* Compatibility with distributed execution, e.g., via slurm.
* Easy data rescue in case of data corruption (or non-availability of this library) as well as compression.
  * Data is saved in multiple json files (coherent json is not efficient) and compressed as zip.
* Optional capturing of stdin and stdout.

You can also consider this tool as a simple serverless but NFS-compatible object database with helpers for benchmarks.

A simple application that runs an algorithm for a set of instances and saves the results to `./results` could look like this:

```python
from aemeasure import MeasurementSeries

# cache=True will only write the results at the end.
with MeasurementSeries("./results", cache=True) as ms:
    for instance in instances:
        with ms.measurement() as m:
            m["instance"] = str(instance)
            m["size"] = len(instance)
            m["algorithm"] = "fancy_algorithm"
            m["parameters"] = "asdgfdfgsdgf"
            solution = run_algorithm(instance)
            m["solution"] = solution.to_json_dict()
            m["objective"] = 42
            m["lower_bound"] = 13
            m.save_metadata()
```

You can then parse the database as pandas table via
```python
from aemeasure import read_as_pandas_table

table = read_as_pandas_table("./results", defaults={"uses_later_added_special_feature": False})
```

Following data can easily be saved:
* Runtime (enter and exit of Measurement)
* stdout/stderr
* Git Revision
* Timestamp of start
* Hostname
* Arguments
* Python-File
* Current working directory

Except of stdout and stderr, these values are automatically saved when using `m.save_metadata()`.
