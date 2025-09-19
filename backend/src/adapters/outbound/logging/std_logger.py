import logging
from backend.src.domain.ports import Logger
from typing import Any

class StdLogger(Logger):
    def __init__(self, name: str = "app"):
        self._log = logging.getLogger(name)

    def debug(self, msg: str, **kv: Any) -> None: self._log.debug(msg)
    def info(self, msg: str, **kv: Any) -> None: self._log.info(msg)
    def warning(self, msg: str, **kv: Any) -> None: self._log.warning(msg)
    def error(self, msg: str, **kv: Any) -> None: self._log.error(msg, extra=kv,exc_info=True)
    def exception(self, msg: str, **kv: Any) -> None: self._log.exception(msg, extra=kv,exc_info=True)