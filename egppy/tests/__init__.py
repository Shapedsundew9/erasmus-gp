"""Ensures module path is in the python path."""
from sys import path
from os.path import abspath, dirname, join
from logging import basicConfig, DEBUG, INFO

path.insert(0, abspath(join(dirname(__file__), "..")))
basicConfig(
    level=DEBUG,
    format="%(asctime)s %(levelname)s %(filename)s %(lineno)d %(message)s",
    filename="log/test.log"
)
