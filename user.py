from base_entity import BaseEntity


class User(BaseEntity):
    def __init__(
        self,
        user_id,
        first_name="",
        last_name="",
        middle_name="",
        phone="",
        email="",
        password="",
        requests=None,
        io=None,
        role="user",
    ):
        super().__init__(io)
        self.id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.middle_name = middle_name
        self.phone = phone
        self.email = email
        self.password = password
        self.role = role
        if requests is None:
            self.requests = []
        else:
            self.requests = requests

    def __str__(self):
        return (
            f"Пользователь #{self.id}: {self.last_name} {self.first_name} {self.middle_name}, "
            f"тел.: {self.phone}, email: {self.email}, заявок: {len(self.requests)}"
        )

    def read(self):
        if self.io is None:
            raise RuntimeError("Стратегия ввода-вывода не установлена.")

        self.first_name = self._input_required_text("Имя")
        self.last_name = self._input_required_text("Фамилия")
        self.middle_name = self._input_required_text("Отчество")
        self.phone = self._input_required_text("Телефон")
        self.email = self._input_email("Email")
        self.password = self._input_password_with_confirmation()

    def write(self):
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

    def show_password(self):
        if self.io is None:
            return
        self.io.output_field("Пароль", self.password)

    def get_masked_password(self):
        return "*" * len(self.password)

    def edit(self):
        if self.io is None:
            raise RuntimeError("Стратегия ввода-вывода не установлена.")

        while True:
            self.io.output_separator()
            self.io.output_message("Редактирование пользователя:")
            self.io.output_message(f"1. Имя ({self.first_name})")
            self.io.output_message(f"2. Фамилия ({self.last_name})")
            self.io.output_message(f"3. Отчество ({self.middle_name})")
            self.io.output_message(f"4. Телефон ({self.phone})")
            self.io.output_message(f"5. Email ({self.email})")
            self.io.output_message(f"6. Пароль ({self.get_masked_password()})")
            self.io.output_message("0. Завершить редактирование")

            choice = self.io.input_int("Выберите номер поля")

            if choice == 0:
                self.io.output_message("Редактирование завершено.")
                return

            if choice == 1:
                self._edit_text_field("Имя", "first_name")
            elif choice == 2:
                self._edit_text_field("Фамилия", "last_name")
            elif choice == 3:
                self._edit_text_field("Отчество", "middle_name")
            elif choice == 4:
                self._edit_text_field("Телефон", "phone")
            elif choice == 5:
                self._edit_email()
            elif choice == 6:
                self._edit_password()
            else:
                self.io.output_error("Некорректный номер пункта меню.")

    def _edit_text_field(self, title, attr_name):
        new_value = self.io.input_field(f"Новое значение для '{title}'")
        if new_value == "":
            self.io.output_message("Значение оставлено без изменений.")
            return

        if new_value.strip() == "":
            self.io.output_error("Поле не может быть пустым.")
            return

        setattr(self, attr_name, new_value.strip())
        self.io.output_message("Поле успешно обновлено.")

    def _edit_email(self):
        new_value = self.io.input_field("Новое значение для 'Email'")
        if new_value == "":
            self.io.output_message("Значение оставлено без изменений.")
            return

        new_value = new_value.strip()
        if new_value == "":
            self.io.output_error("Поле не может быть пустым.")
            return
        if "@" not in new_value:
            self.io.output_error("Email должен содержать символ '@'.")
            return

        self.email = new_value
        self.io.output_message("Поле успешно обновлено.")

    def _edit_password(self):
        change = self.io.input_field("Изменить пароль? (y/n)").lower()
        if change != "y":
            self.io.output_message("Смена пароля отменена.")
            return

        self.password = self._input_password_with_confirmation()
        self.io.output_message("Пароль успешно обновлен.")

    def add_request(self, request):
        if self.io is not None:
            request.set_io(self.io)
        self.requests.append(request)

    def list_requests(self):
        if self.io is None:
            return

        if len(self.requests) == 0:
            self.io.output_message("У пользователя нет заявок.")
            return

        self.io.output_message("Заявки пользователя:")
        for request in self.requests:
            request.write()

    def find_request_by_id(self, request_id):
        for request in self.requests:
            if request.id == request_id:
                return request
        return None

    def cancel_request(self, request_id):
        request = self.find_request_by_id(request_id)
        if request is None:
            return False

        if request.status == "cancelled":
            if self.io is not None:
                self.io.output_message("Заявка уже была отменена ранее.")
            return True

        request.cancel()
        return True

    def _input_required_text(self, field_name):
        return self.io.input_nonempty(field_name).strip()

    def _input_email(self, field_name):
        while True:
            value = self.io.input_nonempty(field_name).strip()
            if "@" in value:
                return value
            self.io.output_error("Email должен содержать символ '@'.")

    def _input_password_with_confirmation(self):
        while True:
            password = self.io.input_nonempty("Пароль").strip()
            confirm_password = self.io.input_nonempty("Подтверждение пароля").strip()

            if password != confirm_password:
                self.io.output_error("Пароли не совпадают.")
                continue

            return password
