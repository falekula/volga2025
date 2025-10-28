from __future__ import annotations
import logging
import os
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler

class Logger:
    _loggers: dict[str, logging.Logger] = {}
    _configured: bool = False

    @classmethod
    def _configure_root(cls) -> None:
        if cls._configured:
            return

        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        logs_dir = Path(os.getenv("LOG_DIR", "logs"))
        logs_dir.mkdir(parents=True, exist_ok=True)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        pid = os.getpid()
        logfile = logs_dir / f"automation_{ts}_{pid}.log"

        fmt = logging.Formatter(
            fmt="%(asctime)s [%(process)d] %(levelname)s %(name)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        root = logging.getLogger()
        root.setLevel(getattr(logging, log_level, logging.INFO))
        root.handlers.clear()

        ch = logging.StreamHandler()
        ch.setLevel(getattr(logging, log_level, logging.INFO))
        ch.setFormatter(fmt)
        root.addHandler(ch)

        fh = RotatingFileHandler(
            filename=logfile,
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        )
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmt)
        root.addHandler(fh)

        cls._configured = True

    @classmethod
    def get_logger(cls, name: str = "Automation") -> logging.Logger:
        cls._configure_root()
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            logger.propagate = True
            cls._loggers[name] = logger
        return cls._loggers[name]
