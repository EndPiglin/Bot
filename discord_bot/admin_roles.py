from config.config_manager import ConfigManager


def add_admin_role(cfg_mgr: ConfigManager, role_id: int):
    cfg = cfg_mgr.config
    roles = cfg.setdefault("admin_roles", [])
    if role_id not in roles:
        roles.append(role_id)
        cfg_mgr.save_config()


def remove_admin_role(cfg_mgr: ConfigManager, role_id: int):
    cfg = cfg_mgr.config
    roles = cfg.setdefault("admin_roles", [])
    if role_id in roles:
        roles.remove(role_id)
        cfg_mgr.save_config()
