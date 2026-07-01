from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User, UserRole


class UserRepo:
    def __init__(self, db: Session):
        self.db = db

    def find_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def find_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def save(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_last_login(self, user_id: int):
        user = self.find_by_id(user_id)
        if user:
            user.last_login_at = datetime.now()
            self.db.commit()

    def update_vehicle(self, user_id: int, vehicle_id: str, battery_capacity: float):
        user = self.find_by_id(user_id)
        if user:
            user.vehicle_id = vehicle_id
            user.battery_capacity = battery_capacity
            self.db.commit()
            self.db.refresh(user)
        return user

    def add_balance(self, user_id: int, amount: float):
        user = self.find_by_id(user_id)
        if user:
            user.balance = round((user.balance or 0.0) + amount, 2)
            self.db.commit()
            self.db.refresh(user)
        return user

    def deduct_balance(self, user_id: int, amount: float):
        user = self.find_by_id(user_id)
        if user:
            user.balance = round(max((user.balance or 0.0) - amount, 0.0), 2)
            self.db.commit()
            self.db.refresh(user)
        return user
