from setuptools import setup, find_packages

setup(
    name="mpi_structlog",
    version="0.0.1",
    url="https://github.com/sixy6e/mpi-structlog",
    author="Josh Sixsmith",
    description="Structured logging for MPI based Python code",
    keywords=[
        "logging", 
        "structured",
        "structure",
        "log",
        "MPI",
        "mpi4py",
    ],
    packages=find_packages(),
    install_requires=[
        "mpi4py",
        "structlog",
    ],
    license="MIT",
)
