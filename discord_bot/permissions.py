def is_admin(user, admin_users, admin_roles) -> bool:
    user_id = str(user.id)

    # Check admin users
    if user_id in [str(u) for u in admin_users]:
        return True

    # Check admin roles
    if hasattr(user, "roles"):
        for role in user.roles:
            if str(role.id) in [str(r) for r in admin_roles]:
                return True

    return False
