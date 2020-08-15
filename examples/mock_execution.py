#!/usr/bin/env python

"""
A toy example that demonstrates a pool of workers and 1 scheduler that
collectively do a list of tasks, all while logging to the same file
using structlog.

To query the output log, use jq https://stedolan.github.io/jq/

To Run
------

mpiexec -n {n processors} python mock_execution.py --n-tasks 10 --log-pathname execution.log


Querying the output log file using jq
-------------------------------------

jq '. | select(.level | contains("error"))' execution.log
jq '. | select(.level | contains("warning"))' execution.log
jq '. | select(.level | contains("info"))' execution.log
jq '. | select(.level | contains("msg"))' execution.log
"""

import click
from mpi4py import MPI
import schwimmbad
import structlog

from mpi_structlog import DEFAULT_PROCESSORS, MPIStreamIO, MPILoggerFactory
from task import SomeTask


@click.command()
@click.option("--n-tasks", type=click.IntRange(min=1), default=20,
              help="The number of independent tasks to process.")
@click.option("--log-pathname", type=click.Path(dir_okay=False),
              help="The pathname for the output log file.")
def main(n_tasks, log_pathname):
    """
    Simulate the execution of a bunch of tasks using MPI,
    as well as setup MPI logging.
    We should see all processor ranks logging similar events right up
    till `pool = schwimmbad.choose_pool(mpi=True)` is called.
    After which only rank 0 will be logging events, and executing lines
    of code.
    All tasks should contain the same value for rank as an argument,
    and the value will be zero.
    The tasks themeselves will be carried out by the workers,
    ranks 1 and higher, and rank 0 will act as a scheduler.
    """
    # comm and processor info
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    stream = MPIStreamIO(log_pathname)
    logger_factory = MPILoggerFactory(stream)
    structlog.configure(
        processors=DEFAULT_PROCESSORS,
        logger_factory=logger_factory,
    )

    # bind the logs to include the rank and size
    log = structlog.get_logger('status').bind(size=size)
    log.info('checking rank and size')

    # define a pool which tells workers to wait for the scheduler's instructions
    log.info('about to initialise an MPI pool')
    pool = schwimmbad.choose_pool(mpi=True)

    # after pool is created, only rank 0 will be executing the following lines
    log.info('MPI pool chosen')

    task_ids = range(1, n_tasks+1)

    # the task class that calls some function
    task_calculator = SomeTask()
    log.info('task chosen')

    # define the list of tasks and the input parameters
    args = [(task_id, rank) for task_id in task_ids]

    # the rank argument should always be zero as we defined an MPI pool above
    log.info(args=args)

    # map tasks across the pool of workers
    # rank 0 acts only as a scheduler, ranks 1 and higher are workers
    pool.map(task_calculator, args)
    pool.close()

    log.info('finished processing')


if __name__ == "__main__":
    main()
