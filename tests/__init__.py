"""Ensures module path is in the python path."""

from logging import basicConfig
from os.path import abspath, dirname, join
from sys import path

from egpcommon.egp_log import DEBUG

path.insert(0, abspath(path=join(dirname(p=__file__), "..")))
basicConfig(
    level=DEBUG,
    format="%(asctime)s %(levelname)s %(filename)s %(lineno)d %(message)s",
    filename="egp.log",
    filemode="w",
)
