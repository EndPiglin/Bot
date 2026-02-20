import json
from typing import Any, Dict

from .defaults import DEFAULT_CONFIG
from .validators import validate_config
from .paths import Paths
from utils.logger import log


class ConfigManager:
    def __init__(self, paths: Paths) -> None:
        self.paths = paths
        self.config: Dict[str, Any] = {}

    def load_config(self) -> Dict[str, Any]:
        if not self.paths.config_file.exists():
            log.info("Config file not found, creating default config.json")
            self.config = DEFAULT_CONFIG.copy()
            self.save_config()
            return self.config

        try:
            with self.paths.config_file.open("r", encoding="utf-8") as f:
                raw = json.load(f)
        except Exception as e:
            log.error(f"Failed to load config.json, using defaults: {e}")
            raw = DEFAULT_CONFIG.copy()

        self.config = validate_config(raw)
        self.save_config()  # persist any migrations / defaults
        return self.config

    def save_config(self) -> None:
        try:
            with self.paths.config_file.open("w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            log.info("Config saved.")
        except Exception as e:
            log.error(f"Failed to save config.json: {e}")
