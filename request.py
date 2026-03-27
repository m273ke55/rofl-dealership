from datetime import datetime

from base_entity import BaseEntity


class Request(BaseEntity):
    def __init__(self, request_id, request_type, date=None, status="active", io=None):
        super().__init__(io)

        if request_type not in ("consultation", "service"):
            raise ValueError("Тип заявки должен быть 'consultation' или 'service'.")
        if status not in ("active", "cancelled"):
            raise ValueError("Статус заявки должен быть 'active' или 'cancelled'.")

        if request_type == "consultation":
            if date is not None:
                raise ValueError("Для заявки consultation дата должна быть пустой.")
        else:
            if date is None:
                raise ValueError("Для заявки service дата обязательна.")
            self._validate_date(date)

        self.id = request_id
        self.type = request_type
        self.date = date
        self.status = status

    @staticmethod
    def _validate_date(value):
        datetime.strptime(value, "%d.%m.%Y")

    def cancel(self):
        self.status = "cancelled"

    def __str__(self):
        if self.type == "consultation":
            request_type = "Консультация"
        else:
            request_type = "Сервис"

        if self.date is None:
            date_text = "не требуется"
        else:
            date_text = self.date

        if self.status == "active":
            status_text = "активна"
        else:
            status_text = "отменена"

        return f"Заявка #{self.id}: тип={request_type}, дата={date_text}, статус={status_text}"

    def write(self):
        if self.io is None:
            return

        if self.type == "consultation":
            request_type = "Консультация"
        else:
            request_type = "Сервис"

        if self.status == "active":
            status_text = "активна"
        else:
            status_text = "отменена"

        self.io.output_separator()
        self.io.output_field("ID заявки", self.id)
        self.io.output_field("Тип", request_type)
        self.io.output_field("Дата", self.date if self.date is not None else "-")
        self.io.output_field("Статус", status_text)
