from typing import Dict


class FeatureFlags:
    def __init__(self, config: Dict) -> None:
        self.config = config

    def is_enabled(self, name: str) -> bool:
        return bool(self.config.get("features", {}).get(name, False))

    def set_flag(self, name: str, value: bool) -> None:
        self.config.setdefault("features", {})[name] = bool(value)

    def is_maintenance(self) -> bool:
        return bool(self.config.get("maintenance_mode", False))

    def set_maintenance(self, value: bool) -> None:
        self.config["maintenance_mode"] = bool(value)
