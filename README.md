# AeMeasure - A macro-benchmarking tool with a serverless database

This module has been developed to save (macro-)benchmarks of algorithms in a simple and
dynamic way. The primary features are:
* Saving metadata such as Git-Revision, hostname, etc.
* No requirement of a data scheme. This is important as often you add additional feature in later iterations but still want to compare it to the original data.
* Compatibility with distributed execution, e.g., via slurm. If you want to use multi-processing, use separate `MeasurementSeries`.
* Easy data rescue in case of data corruption (or non-availability of this library) as well as compression.
  * Data is saved in multiple json files (coherent json is not efficient) and compressed as zip.
* Optional capturing of stdin and stdout.

You can also consider this tool as a simple serverless but NFS-compatible object database with helpers for benchmarks.

The motivation for this tool came from the need to **quickly compare different optimization models (MIP, CP, SAT, ...)**
and analyze their performance.  Here it is more important to save the context (parameters, revision,...) than to
be precise to a millisecond. If you need very precise measurements, you need to look for a micro-benchmarking tool.
This is a **macro-benchmarking tool** with a file-based.

## Usage

A simple application that runs an algorithm for a set of instances and saves the results to `./results` could look like this:

```python
from aemeasure import MeasurementSeries

with MeasurementSeries("./results") as ms:
    # By default, stdout, stdin, and metadata (git revision, hostname, etc) will
    # automatically be added to each measurement.
    for instance in instances:
        with ms.measurement() as m:
            m["instance"] = str(instance)
            m["size"] = len(instance)
            m["algorithm"] = "fancy_algorithm"
            m["parameters"] = "asdgfdfgsdgf"
            solution = run_algorithm(instance)
            m["solution"] = solution.as_json()
            m["objective"] = 42
            m["lower_bound"] = 13
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

## Serverless Database

The serverless database allows to dump unstructured JSONs in a relatively threadsafe way (focus on Surm-node with NFS).
```python
from aemeasure import Database
# Writing
db = Database("./db_folder")  # We use a folder, not a file, to make it NFS-safe.
db.add({"key": "value"}, flush=False)  # save simple dict, do not write directly.
db.flush()  # save to disk
db.compress()  # compress data on disk via zip

# Reading
db2 = Database("./db_folder")
data = db2.load()  # load all entries as a list of dicts.

# Clear
db2.clear()
db2.dump([e for e in data if e["feature_x"]])  # write back only entries with 'feature_x'
```

The primary points of the database are:
* No server is needed, synchronization possible via NFS.
* We are using a folder instead of a single file. Otherwise, the synchronization of different nodes via NFS would be difficult.
* Every node uses a separate, unique file to prevent conflicts.
* Every entry is a new line in JSON format appended to the current database file of the node. As this allows simply appending, this is much more efficient that keeping the whole structure in JSON. If something goes wrong, you can still easily repair it with a text editor and some basic JSON-skills.
* The database has a very simple format, such that it can also be read without this tool.
* As the nativ JSON format can need a signficant amount of disk, a compression option allows to significantly reduce the size via ZIP-compression.

**This database is made for frequent writing, infrequent reading. Currently, there are no query options aside of list comprehensions. Use `clear` and `dump` for selective deletion.**