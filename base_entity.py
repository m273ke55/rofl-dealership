from __future__ import annotations

from typing import Any


class BaseEntity:
    def __init__(self, io: Any | None = None) -> None:
        self.io = io

    def set_io(self, io_obj: Any) -> None:
        self.io = io_obj

    def __getstate__(self) -> dict[str, Any]:
        state = self.__dict__.copy()
        state.pop("io", None)
        return state

    def __setstate__(self, state: dict[str, Any]) -> None:
        self.__dict__.update(state)
        self.io = None

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"
