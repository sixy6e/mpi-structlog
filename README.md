# mpi-structlog
mpi-structlog provides structured logging for Python based MPI code using [mpi4py](https://github.com/mpi4py/mpi4py) and [structlog](https://github.com/hynek/structlog).

# Why
Over the years, in working alongside a lot of scientific researchers, there was a tendency among them to avoid logging at all costs.
Python and mpi4py was typically the toolkit of choice on HPC environments.
I personally found structlog made logging simple and fun to use, so why not couple it with the researchers toolkit of choice.


Examples of use
--------------

```python
import structlog
from mpi_structlog import MPIStreamIO, MPILoggerFactory, DEFAULT_PROCESSORS
out_stream = MPIStreamIO('example.log')
structlog.configure(
processors=DEFAULT_PROCESSORS,
logger_factor=MPILoggerFactory(out_stream)
)
log = structlog.get_logger()
log.msg('Hello')
log.info('FYI')
log.warning('Careful')
log.error('Woops')
```

Also, see [mock\_execution.py](https://github.com/sixy6e/mpi-structlog/examples/mock_execution.py) in [examples](https://github.com/sixy6e/mpi-structlog/examples) that demonstrates using a scheduler and a pool of workers all logging structured entries to the same file (does require [schwimmbad](https://github.com/adrn/schwimmbad/tree/master) for creating an MPI pool of workers).
The following example demonstrates 4 processors working on 16 tasks, and all processors writing structured log entries to a file named "execution.log".

```shell
mpiexec -n 4 python mock_execution.py --n-tasks 16 --log-pathname execution.log
```


Installation
------------

mpi-structlog depends on the following packages:

* [mpi4py](https://github.com/mpi4py/mpi4py)
* [structlog](https://github.com/hynek/structlog)

Optional (for running [mock\_execution.py](https://github.com/sixy6e/mpi-structlog/examples/mock_execution))

* [schwimmbad](https://github.com/adrn/schwimmbad/tree/master)

python setup.py install
