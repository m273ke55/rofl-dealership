from __future__ import annotations

from console_io import ConsoleIO
from pickle_storage import PickleStorage
from request import Request
from user import User


class UserBook:
    def __init__(self, io: ConsoleIO | None = None) -> None:
        self.io = io if io is not None else ConsoleIO()
        self.users: dict[int, User] = {}
        self.max_user_id = 0
        self.max_request_id = 0
        self.storage = PickleStorage(self)

    def add_user(self) -> None:
        new_id = self.max_user_id + 1
        user = User(id=new_id, io=self.io)
        try:
            user.read()
        except Exception as error:
            self.io.output_error(f"Не удалось создать пользователя: {error}")
            return
        self.users[new_id] = user
        self.max_user_id = new_id
        self.io.output_message(f"Пользователь успешно создан с ID {new_id}.")

    def list_users(self) -> None:
        if not self.users:
            self.io.output_message("Список пользователей пуст")
            return
        self.io.output_message("Список пользователей:")
        for user in self.users.values():
            user.write()

    def find_user_by_id(self, user_id: int) -> User | None:
        return self.users.get(user_id)

    def edit_user(self) -> None:
        user_id = self.io.input_int("Введите ID пользователя для редактирования")
        if user_id is None:
            self.io.output_error("ID пользователя не указан.")
            return
        user = self.find_user_by_id(user_id)
        if user is None:
            self.io.output_error("Пользователь с таким ID не найден.")
            return
        user.edit()

    def delete_user(self) -> None:
        user_id = self.io.input_int("Введите ID пользователя для удаления")
        if user_id is None:
            self.io.output_error("ID пользователя не указан.")
            return
        user = self.find_user_by_id(user_id)
        if user is None:
            self.io.output_error("Пользователь с таким ID не найден.")
            return
        confirmation = self.io.input_field("Подтвердите удаление (y/n)").lower()
        if confirmation != "y":
            self.io.output_message("Удаление отменено.")
            return
        del self.users[user_id]
        self.io.output_message("Пользователь удален.")

    def login_user(self) -> None:
        user_id = self.io.input_int("Введите ID пользователя для входа")
        if user_id is None:
            self.io.output_error("ID пользователя не указан.")
            return
        user = self.find_user_by_id(user_id)
        if user is None:
            self.io.output_error("Пользователь с таким ID не найден.")
            return
        self._user_menu(user)

    def save_to_file(self) -> None:
        self.storage.save()

    def load_from_file(self) -> None:
        self.storage.load()

    def clear(self) -> None:
        confirmation = self.io.input_field("Подтвердите очистку списка пользователей (y/n)").lower()
        if confirmation != "y":
            self.io.output_message("Очистка отменена.")
            return
        self.users.clear()
        self.max_user_id = 0
        self.max_request_id = 0
        self.io.output_message("Список пользователей очищен.")

    def restore_io_links(self) -> None:
        for user in self.users.values():
            user.set_io(self.io)
            for request in user.requests:
                request.set_io(self.io)

    def _user_menu(self, user: User) -> None:
        actions = {
            1: user.write,
            2: user.list_requests,
            3: lambda: self._create_request_for_user(user),
            4: lambda: self._cancel_request_for_user(user),
        }
        while True:
            self.io.output_separator()
            self.io.output_message(f"Меню пользователя #{user.id}")
            self.io.output_message("1. Показать данные пользователя")
            self.io.output_message("2. Показать все заявки")
            self.io.output_message("3. Создать заявку")
            self.io.output_message("4. Отменить заявку")
            self.io.output_message("0. Вернуться в главное меню")
            choice = self.io.input_int("Выберите пункт меню")
            if choice == 0:
                return
            action = actions.get(choice)
            if action is None:
                self.io.output_error("Некорректный выбор пункта меню.")
                continue
            action()

    def _create_request_for_user(self, user: User) -> None:
        self.io.output_message("Выберите тип заявки:")
        self.io.output_message("1. consultation")
        self.io.output_message("2. service")
        self.io.output_message("0. отмена")
        choice = self.io.input_int("Ваш выбор")
        if choice == 0:
            self.io.output_message("Создание заявки отменено.")
            return
        if choice == 1:
            request_type = "consultation"
            date = None
        elif choice == 2:
            request_type = "service"
            date = self.io.input_date("Введите дату обслуживания")
        else:
            self.io.output_error("Некорректный выбор типа заявки.")
            return

        new_id = self.max_request_id + 1
        try:
            request = Request(id=new_id, type=request_type, date=date, status="active", io=self.io)
        except ValueError as error:
            self.io.output_error(f"Не удалось создать заявку: {error}")
            return
        user.add_request(request)
        self.max_request_id = new_id
        self.io.output_message(f"Заявка успешно создана с ID {new_id}.")

    def _cancel_request_for_user(self, user: User) -> None:
        if not user.requests:
            self.io.output_message("У пользователя нет заявок для отмены.")
            return
        request_id = self.io.input_int("Введите ID заявки для отмены")
        if request_id is None:
            self.io.output_error("ID заявки не указан.")
            return
        request = user.find_request_by_id(request_id)
        if request is None:
            self.io.output_error("Заявка с таким ID не найдена.")
            return
        if request.status == "cancelled":
            self.io.output_message("Заявка уже отменена.")
            return
        confirmation = self.io.input_field("Подтвердите отмену заявки (y/n)").lower()
        if confirmation != "y":
            self.io.output_message("Отмена заявки прервана.")
            return
        user.cancel_request(request_id)
        self.io.output_message("Заявка отменена.")
