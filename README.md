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
This is a **macro-benchmarking tool** with a **file-based database**.

## When to use AeMeasure?

> *"They say the workman is only as good as his tools; in experimental algorithmics the workman must often build his tools."* - Catherine McGeoch, A Guide to Experimental Algorithmics

AeMeasure is designed for flexibility and simplicity. If you don't have changing
requirements every few weeks, you may be better off with
using a proper database. If you are somewhere in between, you could take a look at, e.g.,
[MongoDB](https://www.mongodb.com/), which is more flexible regarding the schema but
still provides a proper database. If you want a very simple&flexible solution and the data
in the repository (compressed of course, but still human-readable),
AeMeasure may be the right tool for you.

## Installation

The easiest installation is via pip
```shell
pip install -U aemeasure
```

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

## Metadata and stdout/stderr

If you are using MeasurementSeries, all possible information is automatically
added to the measurements by default. You can deactivate this easily in
the constructor. However, often it is useful to have this data (especially stderr
and git revision) at hand, when you notice some oddities in your results. This
can take up a lot of space, but the compression option of the database should
help.

The following data is saved:
* Runtime (enter and exit of Measurement)
* stdout/stderr
* Git Revision
* Timestamp of start
* Hostname
* Arguments
* Python-File
* Current working directory

You can also activate individual metadata by just calling the corresponding member
function of the measurement.

## Usage with Slurminade

This tool is excellent in combination with [Slurminade](https://github.com/d-krupke/slurminade) to automatically distribute
your experiments to Slurm nodes. This also allows you to schedule the missing instances.

An example could look like this:

```python
import slurminade
from aemeasure import MeasurementSeries, read_as_pandas_table, Database

# your supervisor/admin will tell you the necessary configuration.
slurminade.update_default_configuration(partition="alg", constraint="alggen03")
slurminade.set_dispatch_limit(200)  # just a safety measure in case you messed up

# Experiment parameters
result_folder = "./results"
timelimit = 300

# The part to be distributed
@slurminade.slurmify()
def run_for_instance(instance_name, timelimit):
    """
    Solve instance with different solvers.
    """
    instances = load_instances()
    instance = instances[instance_name]
    with MeasurementSeries(result_folder) as ms:
        models = (Model1(instance), Model2(instance))
        for model in models:
            with ms.measurement() as m:
                ub, lb = model.optimize(timelimit)
                m["instance"] = instance_name
                m["timelimit"] = timelimit
                m["ub"] = ub
                m["lb"] = lb
                m["n"] = len(instance)
                m["Method"] = str(model)
                m.save_seconds()

if __name__ == "__main__":
    # Read data
    instances = load_instances()
    Database(result_folder).compress()  # compress prior results to make space
    t = read_as_pandas_table(result_folder)  # read prior results to check which instances are still missing

    # find missing instances (skip already solved instances)
    finished_instances = t["instance"].to_list() if not t.empty else []
    print("Already finished instances:", finished_instances)
    missing_instances = [i for i in instances if i not in finished_instances]
    if finished_instances and missing_instances:
        assert isinstance(missing_instances[0], type(finished_instances[0]))
    print("Still missing instances:", missing_instances)

    # distribute
    for instance in missing_instances:
        run_for_instance.distribute(instance, timelimit)
```

If you have a lot of instances, you may want to use `slurminade.AutoBatch` to automatically
batch multiple instances into a single task.

Important points of this example:
* Extract the parameters as variables and put them at the top so you can easily copy and adapt such a template.
* The `run_for_instance` function will read the instance itself as this is more efficient than to distribute it via slurm as an argument.
* We compress the results at the beginning. As this is executed before distribution, it is threadsafe.
* We quickly check, which instances are already solved and only distribute the missing ones.
* To compress the final results, simply run this script again (it will also check if you may have missed some instances due to an error).

I have often seen scripts that are simply started on each node that either use a complicated
manual instance distribution, require an additional server, or need a lot of additional
data collection in the end. The above's approach seems to be much more elegant to me, if
you already have Slurm and an NFS.

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

## Changelog

* 0.2.9: Added pyproject.toml for PEP compliance.
* 0.2.8: Saving Python-environment, too.
* 0.2.7: Robust JSON serialization. It will save the data but print an error if the data is not JSON-serializable.
* 0.2.6: Extended logging and exception if data could not be written.
* 0.2.5: Skipping on zero size (probably not yet written, can be a problem with NFS)
* 0.2.4: Added some logging.
* 0.2.3: Setting LZMA as compression standard.
* For some reason, the default keys for 'stdin' and 'stdout' were wrong. Fixed.