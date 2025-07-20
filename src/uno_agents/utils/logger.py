"""Module for log-related utils."""

import logging
import sys


def init_logger(source: str, level: int = logging.DEBUG) -> logging.Logger:
    """Function to initialize a logger."""
    logger = logging.getLogger(source)
    logger.setLevel(level)

    logger_handler = logging.StreamHandler(sys.stdout)
    logger_handler.setLevel(level)

    logger_formatter = logging.Formatter("[%(asctime)s][%(name)s][%(levelname)s] %(message)s")
    logger_handler.setFormatter(logger_formatter)

    logger.addHandler(logger_handler)
    return logger
