"""
An example of creating an MPI Logger to be used directly with
structlog.

Example
-------

>>> import structlog
>>> from mpi_logger import MPIStreamIO, MPILoggerFactory, DEFAULT_PROCESSORS
>>> out_stream = MPIStreamIO('example.log')
>>> structlog.configure(
processors=DEFAULT_PROCESSORS,
logger_factor=MPILoggerFactory(out_stream)
)
>>> log = structlog.get_logger()
>>> log.msg('Hello')
>>> log.info('FYI')
>>> log.warning('Careful')
>>> log.error('Woops')
"""

import atexit
from pathlib import Path
from mpi4py import MPI
import structlog


def add_mpi_rank(logger, log_method, event_dict):
    """
    Include the MPI rank in the output log entry.
    """
    event_dict["rank"] = MPI.COMM_WORLD.Get_rank()
    return event_dict


IO_MODE = MPI.MODE_WRONLY | MPI.MODE_CREATE | MPI.MODE_EXCL
DEFAULT_PROCESSORS = [
    add_mpi_rank,
    structlog.stdlib.add_log_level,
    structlog.processors.TimeStamper(fmt="ISO"),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
    structlog.processors.JSONRenderer(sort_keys=True)
]


class MPIStreamIO(object):
    """
    A very basic MPI stream handler for synchronised I/O.
    Non-Unicode strings will be checked and converted to Unicode.
    If the pathname to the file already exists, then it will be
    removed and a new file created in its place.
    """

    def __init__(self, pathname, comm=MPI.COMM_WORLD, mode=IO_MODE):
        """
        :param pathname:
            Output pathname to contain the log entries.

        :param comm:
            An MPI communicator. Default is ``MPI.COMM_WORLD``.

        :param mode:
            The mode used to open the file. Default is:
            ``MPI.MODE_WRONLY | MPI.MODE_CREATE | MPI.MODE_EXCL``.
        """

        self._pathname = Path(pathname)
        self._rank = MPI.COMM_WORLD.Get_rank()

        # check for existance of output file and parent directory
        if self._rank == 0:
            if not self._pathname.parent.exists():
                self._pathname.parent.mkdir()

            if self._pathname.exists():
                self._pathname.unlink()

        MPI.COMM_WORLD.Barrier()

        self._file = MPI.File.Open(comm, pathname, mode)
        self._file.Set_atomicity(True)

        # register with atexit for cleanup upon normal Python exit
        atexit.register(lambda: MPIStreamIO.close(self))

    def write(self, msg):
        """Write the message to disk."""
        # if for some reason we don't have a unicode string...
        try:
            msg = msg.encode()
        except AttributeError:
            pass
        self._file.Write_shared(msg)

    def sync(self):
        """Synchronise the processes."""
        self._file.Sync()

    def close(self):
        """Close the MPI Streamed file."""
        self.sync()
        self._file.Close()


class MPILogger:
    """
    The MPI logger returned by the MPILoggerFactory that will be called
    by structlog.
    """

    def __init__(self, stream):
        self._terminator = '\n'
        self._stream = stream
        self._rank = MPI.COMM_WORLD.Get_rank()
        self._write = self._stream.write

    def __repr__(self):
        return f"<MPILogger(rank:{self._rank!r})>"

    def msg(self, message):
        self._write(f'{message}{self._terminator}')

    def close(self):
        print('closing')
        if self._stream:
            self._stream.close()
            self._stream = None

    log = debug = info = warn = warning = msg
    fatal = failure = err = error = critical = exception = msg


class MPILoggerFactory:
    """
    The callable logger factory that returns an MPILogger instance.
    """

    def __init__(self, stream):
        self._stream = stream

    def __call__(self, *args):
        return MPILogger(self._stream)
