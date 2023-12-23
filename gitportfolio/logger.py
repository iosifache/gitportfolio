import logging

from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET",
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler()],
)


def get_logger() -> logging.Logger:
    return logging.getLogger("gitportfolio")


def disable_logger() -> None:
    get_logger().propagate = False
