
from datetime import datetime, timedelta
from typing import Optional

import hashlib

from jose import jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User, UserRole
from app.repositories.user_repo import UserRepo


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _verify_password(password: str, hashed: str) -> bool:
    return hashlib.sha256(password.encode()).hexdigest() == hashed


class UserService:

    def register(self, username: str, password: str, phone: Optional[str], db: Session) -> User:
        repo = UserRepo(db)
        existing = repo.find_by_username(username)
        if existing:
            raise ValueError("用户名已存在")

        user = User(
            username=username,
            password_hash=_hash_password(password),
            phone=phone,
            role=UserRole.CUSTOMER,
            created_at=datetime.now(),
        )
        return repo.save(user)

    def login(self, username: str, password: str, db: Session) -> dict:
        repo = UserRepo(db)
        user = repo.find_by_username(username)
        if not user:
            raise ValueError("用户不存在")
        if not _verify_password(password, user.password_hash):
            raise ValueError("密码错误")

        repo.update_last_login(user.id)
        token = self._create_token(user)
        return {
            "access_token": token,
            "token_type": "bearer",
            "role": user.role.value,
            "user_id": user.id,
            "username": user.username,
        }

    def get_user(self, user_id: int, db: Session) -> Optional[User]:
        repo = UserRepo(db)
        return repo.find_by_id(user_id)

    def update_vehicle(self, user_id: int, vehicle_id: str, battery_capacity: float, db: Session) -> User:
        repo = UserRepo(db)
        return repo.update_vehicle(user_id, vehicle_id, battery_capacity)

    def recharge(self, user_id: int, amount: float, db: Session) -> User:
        if amount <= 0:
            raise ValueError("充值金额必须大于 0")
        repo = UserRepo(db)
        user = repo.add_balance(user_id, amount)
        if not user:
            raise ValueError("用户不存在")
        return user

    def _create_token(self, user: User) -> str:
        expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role.value,
            "exp": expire,
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> dict:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except Exception:
            raise ValueError("无效的 Token")
