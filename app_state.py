from __future__ import annotations

import os
from dataclasses import dataclass

from user_book import UserBook
from user import User


DATA_FILE = os.environ.get("ROFL_DATA_FILE", "data.dat")
DEFAULT_ADMIN_EMAIL = os.environ.get("ROFL_ADMIN_EMAIL", "admin@rofl.local")
DEFAULT_ADMIN_PASSWORD = os.environ.get("ROFL_ADMIN_PASSWORD", "admin123")


class NullIO:
    def output_message(self, message):
        return None

    def output_error(self, message):
        return None


@dataclass
class AppState:
    user_book: UserBook
    data_file: str = DATA_FILE

    def load(self):
        if os.path.exists(self.data_file):
            self.user_book.storage.load(self.data_file)
        self.ensure_user_roles()
        self.ensure_default_admin()

    def save(self):
        self.ensure_user_roles()
        self.user_book.storage.save(self.data_file)

    def ensure_user_roles(self):
        for user in self.user_book.users.values():
            if not hasattr(user, "role"):
                user.role = "user"

    def ensure_default_admin(self):
        admin_user = self.find_user_by_email(DEFAULT_ADMIN_EMAIL)
        if admin_user is not None:
            admin_user.role = "admin"
            return admin_user

        new_id = self.user_book.max_user_id + 1
        admin = User(
            user_id=new_id,
            first_name="Админ",
            last_name="Системный",
            middle_name="",
            phone="+70000000000",
            email=DEFAULT_ADMIN_EMAIL,
            password=DEFAULT_ADMIN_PASSWORD,
            io=self.user_book.io,
            role="admin",
        )
        self.user_book.users[new_id] = admin
        self.user_book.max_user_id = new_id
        return admin

    def find_user_by_email(self, email):
        email = email.strip().lower()
        for user in self.user_book.users.values():
            if user.email.lower() == email:
                return user
        return None


_state: AppState | None = None


def get_state() -> AppState:
    global _state
    if _state is None:
        book = UserBook(io=NullIO())
        _state = AppState(user_book=book)
        _state.load()
    return _state
