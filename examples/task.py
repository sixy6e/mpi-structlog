"""
A toy task that simulates a computation by waiting for a random amount of time.
"""

import time
import random
from mpi4py import MPI
import structlog

# log file I/O is initialised elsewhere
LOG = structlog.get_logger('status')

# which rank worker will do the work (should always be 1 or higher)
COMM = MPI.COMM_WORLD
RANK = COMM.Get_rank()


class SomeTask:

    """
    A simple class definition (similar to luigi by Spotify) that defines
    a work method for custom functions.
    """

    def do_work(self, task_id, rank):
        # ranks 1 and higher will be the processes executing the work
        # but the 'rank' argument will always be zero, as rank 0 defined the work
        log = LOG.bind(rank_argument=rank, worker_rank=RANK)
        log.info(f"start processing task id: {task_id}")

        # simulate a computation for a small amount of time
        n = random.randint(1, 4)
        time.sleep(n / 4)

        # logging level (randomly chosen index)
        idx = n - 1
        levels = [
            'error',
            'warning',
            'info',
            'msg',
        ]

        # log a random level
        status = levels[idx]
        if status == 'error':
            log.error(f"error processing task id: {task_id}")
        elif status == 'warning':
            log.warning(f"finished processing task id: {task_id} with a warning")
        elif status == 'info':
            log.info(f"finished processing task id: {task_id}")
        else:
            log.msg(f"finished processing task id: {task_id}")

    def __call__(self, args):
        self.do_work(*args)
