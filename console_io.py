from datetime import datetime


class ConsoleIO:
    DATE_FORMAT = "%d.%m.%Y"

    def input_field(self, field_name, default=None):
        prompt = field_name
        if default is not None:
            prompt += f" [{default}]"
        prompt += ": "

        value = input(prompt).strip()
        if value == "" and default is not None:
            return default
        return value

    def input_int(self, prompt, allow_empty=False):
        while True:
            raw_value = input(f"{prompt}: ").strip()
            if raw_value == "":
                if allow_empty:
                    return None
                self.output_error("Введите целое число.")
                continue

            try:
                return int(raw_value)
            except ValueError:
                self.output_error("Некорректный ввод. Нужно ввести целое число.")

    def input_nonempty(self, field_name, default=None):
        while True:
            value = self.input_field(field_name, default=default)
            if value.strip() == "":
                self.output_error(f"Поле '{field_name}' не может быть пустым.")
                continue
            return value.strip()

    def input_date(self, field_name, allow_empty=False, default=None):
        while True:
            value = self.input_field(field_name, default=default)
            if value == "":
                if allow_empty:
                    return None
                self.output_error("Дата не может быть пустой.")
                continue

            try:
                datetime.strptime(value, self.DATE_FORMAT)
                return value
            except ValueError:
                self.output_error("Некорректная дата. Используйте формат ДД.ММ.ГГГГ.")

    def output_field(self, title, value):
        print(f"{title}: {value}")

    def output_message(self, message):
        print(message)

    def output_error(self, message):
        print(f"Ошибка: {message}")

    def output_separator(self):
        print("-" * 40)
