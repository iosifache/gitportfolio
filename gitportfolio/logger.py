import logging
import sys

from github import set_log_level as pygithub_set_log_level
from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler()],
)


def get_logger() -> logging.Logger:
    return logging.getLogger("gitportfolio")


def disable_logger() -> None:
    get_logger().propagate = False

    logging.disable(sys.maxsize)
    logging.getLogger("requests").setLevel(sys.maxsize)
    logging.getLogger("requests").propagate = False
    logging.getLogger("urllib3").setLevel(sys.maxsize)
    logging.getLogger("urllib3").propagate = False
    logging.getLogger("requests.packages.urllib3").setLevel(sys.maxsize)
    logging.getLogger("requests.packages.urllib3").propagate = False
    pygithub_set_log_level(sys.maxsize)
