from __future__ import annotations

import logging
import os
import sys


# Technical logging helper only; the code in this file is not part of the symbolic RSP
# model or the wider research contribution.
LOGGER_NAME = "core"
DEFAULT_LEVEL = "INFO"
DEFAULT_FORMAT = "[%(asctime)s] %(message)s"
DEFAULT_DATE_FORMAT = "%H:%M:%S"
_configured = False



# Define a helper to map user-provided log levels onto Python logging levels.
def _resolve_level(level: int | str | None) -> int:
    if level is None:
        level = os.getenv("RSP_SMT_LOG_LEVEL", DEFAULT_LEVEL)
    if isinstance(level, int):
        return level
    value = getattr(logging, level.upper(), None)
    if isinstance(value, int):
        return value
    raise ValueError(f"Unknown log level: {level}")



# Define a lightweight default configuration for notebook/terminal output.
def configure_logging(level: int | str | None = None) -> None:
    global _configured

    logger = logging.getLogger(LOGGER_NAME)
    if level is None and _configured:
        return

    logger.setLevel(_resolve_level(level))
    logger.propagate = False

    if any(getattr(handler, "_rsp_smt_handler", False) for handler in logger.handlers):
        _configured = True
        return

    # Send logs to stdout so Jupyter displays them as ordinary cell output.
    handler = logging.StreamHandler(sys.stdout)
    handler._rsp_smt_handler = True
    handler.setFormatter(logging.Formatter(DEFAULT_FORMAT, datefmt=DEFAULT_DATE_FORMAT))
    logger.addHandler(handler)
    _configured = True



# Define a helper to retrieve a named logger after applying the default setup.
def get_logger(name: str | None = None) -> logging.Logger:
    configure_logging()
    if name is None:
        return logging.getLogger(LOGGER_NAME)
    return logging.getLogger(name)
