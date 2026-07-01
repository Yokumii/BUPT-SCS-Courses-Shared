from typing import Optional

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.repositories.user_repo import UserRepo
from app.services.user_service import UserService


def get_current_user(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录或 Token 缺失")

    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = UserService.verify_token(token)
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="无效或已过期的 Token")

    user = UserRepo(db).find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


def require_customer(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(status_code=403, detail="仅普通用户可执行该操作")
    return current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(status_code=403, detail="仅管理员可执行该操作")
    return current_user
