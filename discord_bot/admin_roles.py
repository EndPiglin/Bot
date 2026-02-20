from config.config_manager import ConfigManager
from utils.logger import log


def add_admin_role(config_manager: ConfigManager, role_id: int) -> None:
    cfg = config_manager.config
    roles = cfg.setdefault("admin_roles", [])
    if role_id not in roles:
        roles.append(role_id)
        config_manager.save_config()
        log.info(f"Added admin role: {role_id}")


def remove_admin_role(config_manager: ConfigManager, role_id: int) -> None:
    cfg = config_manager.config
    roles = cfg.setdefault("admin_roles", [])
    if role_id in roles:
        roles.remove(role_id)
        config_manager.save_config()
        log.info(f"Removed admin role: {role_id}")
