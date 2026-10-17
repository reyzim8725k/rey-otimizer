"""Logging centralizado da aplicação."""
from datetime import datetime
from pathlib import Path
import threading

class AppLogger:
    def __init__(self, root: str = "logs"):
        self.path = Path(root) / f"reyoptimizer_{datetime.now():%Y-%m-%d}.log"
        self.path.parent.mkdir(exist_ok=True)
        self._lock = threading.Lock()
        self.listeners = []

    def log(self, level: str, module: str, action: str, result: str):
        line = f"{datetime.now():%Y-%m-%d %H:%M:%S} | {level:<7} | {module} | {action} | {result}"
        with self._lock:
            self.path.open("a", encoding="utf-8").write(line + "\n")
        for listener in list(self.listeners):
            try: listener(line, level)
            except Exception: pass

    def info(self, module, action, result): self.log("INFO", module, action, result)
    def success(self, module, action, result): self.log("SUCCESS", module, action, result)
    def warn(self, module, action, result): self.log("WARN", module, action, result)
    def error(self, module, action, result): self.log("ERROR", module, action, result)
