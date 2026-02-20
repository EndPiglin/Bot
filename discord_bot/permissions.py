from typing import Iterable


def is_admin(user, admin_users: Iterable[int], admin_roles: Iterable[int]) -> bool:
    if user.id in admin_users:
        return True

    if hasattr(user, "roles"):
        for role in user.roles:
            if role.id in admin_roles:
                return True

    return False
