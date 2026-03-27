from console_io import ConsoleIO
from pickle_storage import PickleStorage
from request import Request
from user import User


class UserBook:
    def __init__(self, io=None):
        if io is None:
            io = ConsoleIO()
        self.io = io
        self.users = {}
        self.max_user_id = 0
        self.max_request_id = 0
        self.storage = PickleStorage(self)

        self.service_dates = [
            "01.04.2026",
            "02.04.2026",
            "03.04.2026",
            "04.04.2026",
            "05.04.2026",
            "06.04.2026",
            "07.04.2026",
        ]

    def add_user(self):
        new_id = self.max_user_id + 1
        user = User(user_id=new_id, io=self.io)

        try:
            user.read()
        except Exception as error:
            self.io.output_error(f"Не удалось создать пользователя: {error}")
            return

        self.users[new_id] = user
        self.max_user_id = new_id
        self.io.output_message(f"Пользователь успешно создан с ID {new_id}.")

    def list_users(self):
        if len(self.users) == 0:
            self.io.output_message("Список пользователей пуст")
            return

        self.io.output_message("Список пользователей:")
        for user in self.users.values():
            user.write()

    def find_user_by_id(self, user_id):
        return self.users.get(user_id)

    def edit_user(self):
        user_id = self.io.input_int("Введите ID пользователя для редактирования")
        if user_id is None:
            self.io.output_error("ID пользователя не указан.")
            return

        user = self.find_user_by_id(user_id)
        if user is None:
            self.io.output_error("Пользователь с таким ID не найден.")
            return

        user.edit()

    def delete_user(self):
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

    def login_user(self):
        user_id = self.io.input_int("Введите ID пользователя для входа")
        if user_id is None:
            self.io.output_error("ID пользователя не указан.")
            return

        user = self.find_user_by_id(user_id)
        if user is None:
            self.io.output_error("Пользователь с таким ID не найден.")
            return

        password = self.io.input_nonempty("Введите пароль").strip()
        if password != user.password:
            self.io.output_error("Неверный пароль.")
            return

        self.io.output_message("Вход выполнен успешно.")
        self._user_menu(user)

    def save_to_file(self):
        filename = self.io.input_field("Введите имя файла (или Enter для data.dat)")
        if filename == "":
            filename = "data.dat"
        self.storage.save(filename)

    def load_from_file(self):
        filename = self.io.input_field("Введите имя файла для загрузки (или Enter для data.dat)")
        if filename == "":
            filename = "data.dat"
        self.storage.load(filename)

    def clear(self):
        confirmation = self.io.input_field("Подтвердите очистку списка пользователей (y/n)").lower()
        if confirmation != "y":
            self.io.output_message("Очистка отменена.")
            return

        self.users.clear()
        self.max_user_id = 0
        self.max_request_id = 0
        self.io.output_message("Список пользователей очищен.")

    def restore_io_links(self):
        for user in self.users.values():
            user.set_io(self.io)
            for request in user.requests:
                request.set_io(self.io)

    def _user_menu(self, user):
        while True:
            self.io.output_separator()
            self.io.output_message(f"Меню пользователя #{user.id}")
            self.io.output_message("1. Показать данные пользователя")
            self.io.output_message("2. Показать пароль")
            self.io.output_message("3. Показать все заявки")
            self.io.output_message("4. Создать заявку")
            self.io.output_message("5. Отменить заявку")
            self.io.output_message("0. Вернуться в главное меню")

            choice = self.io.input_int("Выберите пункт меню")
            if choice == 0:
                return
            elif choice == 1:
                user.write()
            elif choice == 2:
                user.show_password()
            elif choice == 3:
                user.list_requests()
            elif choice == 4:
                self._create_request_for_user(user)
            elif choice == 5:
                self._cancel_request_for_user(user)
            else:
                self.io.output_error("Некорректный выбор пункта меню.")

    def _create_request_for_user(self, user):
        self.io.output_message("Выберите тип заявки:")
        self.io.output_message("1. Консультация")
        self.io.output_message("2. Сервис")
        self.io.output_message("0. Отмена")

        choice = self.io.input_int("Ваш выбор")
        if choice == 0:
            self.io.output_message("Создание заявки отменено.")
            return

        if choice == 1:
            request_type = "consultation"
            date = None
        elif choice == 2:
            request_type = "service"
            date = self._choose_service_date()
            if date is None:
                return
        else:
            self.io.output_error("Некорректный выбор типа заявки.")
            return

        new_id = self.max_request_id + 1

        try:
            request = Request(
                request_id=new_id,
                request_type=request_type,
                date=date,
                status="active",
                io=self.io,
            )
        except ValueError as error:
            self.io.output_error(f"Не удалось создать заявку: {error}")
            return

        user.add_request(request)
        self.max_request_id = new_id
        self.io.output_message(f"Заявка успешно создана с ID {new_id}.")

    def _choose_service_date(self):
        free_dates = self._get_free_service_dates()

        if len(free_dates) == 0:
            self.io.output_message("Свободных дат для сервиса нет.")
            return None

        self.io.output_message("Доступные даты сервиса:")
        for index in range(len(free_dates)):
            self.io.output_message(f"{index + 1}. {free_dates[index]}")
        self.io.output_message("0. Отмена")

        while True:
            choice = self.io.input_int("Выберите номер даты")
            if choice == 0:
                self.io.output_message("Создание заявки отменено.")
                return None

            if choice is None:
                self.io.output_error("Некорректный ввод.")
                continue

            if 1 <= choice <= len(free_dates):
                return free_dates[choice - 1]

            self.io.output_error("Некорректный номер даты.")

    def _get_free_service_dates(self):
        busy_dates = set()

        for user in self.users.values():
            for request in user.requests:
                if request.type == "service" and request.status == "active" and request.date is not None:
                    busy_dates.add(request.date)

        free_dates = []
        for date in self.service_dates:
            if date not in busy_dates:
                free_dates.append(date)

        return free_dates

    def _cancel_request_for_user(self, user):
        if len(user.requests) == 0:
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
