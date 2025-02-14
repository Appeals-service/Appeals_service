"""Role checker module"""

from fastapi import Depends, HTTPException, status

from src.dto.schemas.users import JWTUserData
from src.utils.auth import get_current_user_data
from src.utils.enums import UserRole


class RoleChecker:

    def __init__(self, allowed_roles: set[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user_data: dict[str, str | UserRole] = Depends(get_current_user_data)) -> JWTUserData:

        if user_data.get("role") not in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access is denied")
        return JWTUserData(**user_data)


allowed_for_admin = RoleChecker({UserRole.admin})
allowed_for_admin_user = RoleChecker({UserRole.admin, UserRole.user})
allowed_for_admin_executor = RoleChecker({UserRole.admin, UserRole.executor})
allowed_for_all = RoleChecker({role for role in UserRole})
