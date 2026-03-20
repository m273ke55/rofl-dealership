from __future__ import annotations

from dataclasses import dataclass, field

from base_entity import BaseEntity
from request import Request


@dataclass
class User(BaseEntity):
    id: int
    first_name: str = ""
    last_name: str = ""
    middle_name: str = ""
    phone: str = ""
    email: str = ""
    password: str = ""
    requests: list[Request] = field(default_factory=list)
    io: object | None = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        BaseEntity.__init__(self, self.io)

    def __str__(self) -> str:
        return (
            f"Пользователь #{self.id}: {self.last_name} {self.first_name} {self.middle_name}, "
            f"тел.: {self.phone}, email: {self.email}, заявок: {len(self.requests)}"
        )

    def read(self) -> None:
        if self.io is None:
            raise RuntimeError("Стратегия ввода-вывода не установлена.")
        self.first_name = self._input_required_text("Имя")
        self.last_name = self._input_required_text("Фамилия")
        self.middle_name = self._input_required_text("Отчество")
        self.phone = self._input_required_text("Телефон")
        self.email = self._input_email("Email")
        self.password = self._input_password_with_confirmation()

    def write(self) -> None:
        if self.io is None:
            return
        self.io.output_separator()
        self.io.output_field("ID пользователя", self.id)
        self.io.output_field("Фамилия", self.last_name)
        self.io.output_field("Имя", self.first_name)
        self.io.output_field("Отчество", self.middle_name)
        self.io.output_field("Телефон", self.phone)
        self.io.output_field("Email", self.email)
        self.io.output_field("Пароль", self.get_masked_password())
        self.io.output_field("Количество заявок", len(self.requests))

    def show_password(self) -> None:
        if self.io is None:
            return
        self.io.output_field("Пароль", self.password)

    def get_masked_password(self) -> str:
        if not self.password:
            return ""
        return "*" * len(self.password)

    def edit(self) -> None:
        if self.io is None:
            raise RuntimeError("Стратегия ввода-вывода не установлена.")

        fields = [
            ("Имя", "first_name", self._validate_nonempty),
            ("Фамилия", "last_name", self._validate_nonempty),
            ("Отчество", "middle_name", self._validate_nonempty),
            ("Телефон", "phone", self._validate_nonempty),
            ("Email", "email", self._validate_email),
            ("Пароль", "password", None),
        ]

        while True:
            self.io.output_separator()
            self.io.output_message("Редактирование пользователя:")
            for index, (title, attr_name, _) in enumerate(fields, start=1):
                if attr_name == "password":
                    shown_value = self.get_masked_password()
                else:
                    shown_value = getattr(self, attr_name)
                self.io.output_message(f"{index}. {title} ({shown_value})")
            self.io.output_message("0. Завершить редактирование")

            choice = self.io.input_int("Выберите номер поля", allow_empty=False)

            if choice == 0:
                self.io.output_message("Редактирование завершено.")
                return
            if choice is None or not (1 <= choice <= len(fields)):
                self.io.output_error("Некорректный номер пункта меню.")
                continue

            title, attr_name, validator = fields[choice - 1]

            if attr_name == "password":
                change = self.io.input_field("Изменить пароль? (y/n)").lower()
                if change != "y":
                    self.io.output_message("Смена пароля отменена.")
                    continue
                new_password = self._input_password_with_confirmation()
                self.password = new_password
                self.io.output_message("Пароль успешно обновлен.")
                continue

            while True:
                new_value = self.io.input_field(f"Новое значение для '{title}'")
                if new_value == "":
                    self.io.output_message("Значение оставлено без изменений.")
                    break
                validation_error = validator(new_value)
                if validation_error is not None:
                    self.io.output_error(validation_error)
                    continue
                setattr(self, attr_name, new_value.strip())
                self.io.output_message("Поле успешно обновлено.")
                break

    def add_request(self, request: Request) -> None:
        if self.io is not None:
            request.set_io(self.io)
        self.requests.append(request)

    def list_requests(self) -> None:
        if self.io is None:
            return
        if not self.requests:
            self.io.output_message("У пользователя нет заявок.")
            return
        self.io.output_message("Заявки пользователя:")
        for request in self.requests:
            request.write()

    def find_request_by_id(self, request_id: int) -> Request | None:
        for request in self.requests:
            if request.id == request_id:
                return request
        return None

    def cancel_request(self, request_id: int) -> bool:
        request = self.find_request_by_id(request_id)
        if request is None:
            return False

        if request.status == "cancelled":
            if self.io is not None:
                self.io.output_message("Заявка уже была отменена ранее.")
            return True

        request.cancel()
        return True

    def _input_required_text(self, field_name: str) -> str:
        return self.io.input_nonempty(field_name).strip()

    def _input_email(self, field_name: str) -> str:
        while True:
            value = self.io.input_nonempty(field_name).strip()
            validation_error = self._validate_email(value)
            if validation_error is None:
                return value
            self.io.output_error(validation_error)

    def _input_password_with_confirmation(self) -> str:
        while True:
            password = self.io.input_nonempty("Пароль").strip()
            confirm_password = self.io.input_nonempty("Подтверждение пароля").strip()

            if password != confirm_password:
                self.io.output_error("Пароли не совпадают.")
                continue

            return password

    @staticmethod
    def _validate_nonempty(value: str) -> str | None:
        if value.strip() == "":
            return "Поле не может быть пустым."
        return None

    @staticmethod
    def _validate_email(value: str) -> str | None:
        if value.strip() == "":
            return "Поле не может быть пустым."
        if "@" not in value:
            return "Email должен содержать символ '@'."
        return None