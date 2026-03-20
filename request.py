from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar

from base_entity import BaseEntity


@dataclass
class Request(BaseEntity):
    ALLOWED_TYPES: ClassVar[set[str]] = {"consultation", "service"}
    ALLOWED_STATUSES: ClassVar[set[str]] = {"active", "cancelled"}

    id: int
    type: str
    date: str | None
    status: str = "active"
    io: object | None = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        BaseEntity.__init__(self, self.io)
        if self.type not in self.ALLOWED_TYPES:
            raise ValueError("Тип заявки должен быть 'consultation' или 'service'.")
        if self.status not in self.ALLOWED_STATUSES:
            raise ValueError("Статус заявки должен быть 'active' или 'cancelled'.")
        if self.type == "consultation":
            if self.date is not None:
                raise ValueError("Для заявки consultation дата должна быть пустой.")
        else:
            if self.date is None:
                raise ValueError("Для заявки service дата обязательна.")
            self._validate_date(self.date)

    @staticmethod
    def _validate_date(value: str) -> None:
        datetime.strptime(value, "%d.%m.%Y")

    def cancel(self) -> None:
        self.status = "cancelled"

    def __str__(self) -> str:
        request_type = "Консультация" if self.type == "consultation" else "Сервис"
        date_text = self.date if self.date is not None else "не требуется"
        status_text = "активна" if self.status == "active" else "отменена"
        return (
            f"Заявка #{self.id}: тип={request_type}, дата={date_text}, статус={status_text}"
        )

    def write(self) -> None:
        if self.io is None:
            return
        self.io.output_separator()
        self.io.output_field("ID заявки", self.id)
        self.io.output_field("Тип", self.type)
        self.io.output_field("Дата", self.date if self.date is not None else "-")
        self.io.output_field("Статус", self.status)
