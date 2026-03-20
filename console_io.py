from __future__ import annotations

from datetime import datetime


class ConsoleIO:
    DATE_FORMAT = "%d.%m.%Y"

    def input_field(self, field_name: str, default: str | None = None) -> str:
        prompt = f"{field_name}"
        if default is not None:
            prompt += f" [{default}]"
        prompt += ": "
        value = input(prompt).strip()
        if value == "" and default is not None:
            return default
        return value

    def input_int(self, prompt: str, allow_empty: bool = False) -> int | None:
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

    def input_nonempty(self, field_name: str, default: str | None = None) -> str:
        while True:
            value = self.input_field(field_name, default=default)
            if value.strip() == "":
                self.output_error(f"Поле '{field_name}' не может быть пустым.")
                continue
            return value.strip()

    def input_date(
        self,
        field_name: str,
        allow_empty: bool = False,
        default: str | None = None,
    ) -> str | None:
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

    def output_field(self, title: str, value: object) -> None:
        print(f"{title}: {value}")

    def output_message(self, message: str) -> None:
        print(message)

    def output_error(self, message: str) -> None:
        print(f"Ошибка: {message}")

    def output_separator(self) -> None:
        print("-" * 40)
