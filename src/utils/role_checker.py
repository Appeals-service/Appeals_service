"""Role checker module"""

from fastapi import Depends, HTTPException, status

from utils.auth import get_current_user_data
from utils.enums import UserRole


class RoleChecker:

    def __init__(self, allowed_roles: set[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, role_n_id: tuple[UserRole, str] = Depends(get_current_user_data)) -> tuple[UserRole, str]:

        if role_n_id[0] not in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access is denied")
        return role_n_id


allowed_for_admin = RoleChecker({UserRole.admin})
allowed_for_user = RoleChecker({UserRole.admin, UserRole.user})
allowed_for_all = RoleChecker({role for role in UserRole})
