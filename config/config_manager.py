import json
from typing import Any, Dict

from .paths import Paths
from .defaults import DEFAULT_CONFIG
from .validators import validate_config
from utils.logger import log


class ConfigManager:
    def __init__(self, paths: Paths):
        self.paths = paths
        self._config: Dict[str, Any] = {}

    def load_config(self) -> Dict[str, Any]:
        path = self.paths.config_file
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            log.warning("config.json not found, creating default.")
            data = DEFAULT_CONFIG.copy()
            self.save_config(data)
        except json.JSONDecodeError:
            log.error("config.json is invalid JSON, using defaults.")
            data = DEFAULT_CONFIG.copy()

        data = validate_config(data)
        self._config = data
        return self._config

    def save_config(self, config: Dict[str, Any] = None) -> None:
        if config is None:
            config = self._config
        path = self.paths.config_file
        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        log.info("Config saved.")

    @property
    def config(self) -> Dict[str, Any]:
        return self._config

    def update(self, path: str, value: Any) -> None:
        parts = path.split(".")
        ref = self._config
        for p in parts[:-1]:
            ref = ref.setdefault(p, {})
        ref[parts[-1]] = value
        self.save_config()
