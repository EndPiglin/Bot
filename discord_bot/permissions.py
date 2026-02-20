from typing import List

import discord


def is_admin(user: discord.Member, admin_users: List[int], admin_roles: List[int]) -> bool:
    if user.guild_permissions.administrator:
        return True
    if user.id in admin_users:
        return True
    user_role_ids = {r.id for r in user.roles}
    if any(rid in user_role_ids for rid in admin_roles):
        return True
    return False
