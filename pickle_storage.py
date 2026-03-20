from __future__ import annotations

import pickle
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from user_book import UserBook


class PickleStorage:
    def __init__(self, book: "UserBook") -> None:
        self.book = book

    def save(self, filename: str = "data.dat") -> bool:
        try:
            data = {
                "users": self.book.users,
                "max_user_id": self.book.max_user_id,
                "max_request_id": self.book.max_request_id,
            }
            with open(filename, "wb") as file:
                pickle.dump(data, file)
            self.book.io.output_message(f"Данные успешно сохранены в файл '{filename}'.")
            return True
        except FileNotFoundError:
            self.book.io.output_error(f"Файл '{filename}' не найден.")
        except OSError as error:
            self.book.io.output_error(f"Ошибка ввода-вывода при сохранении: {error}")
        except Exception as error:
            self.book.io.output_error(f"Непредвиденная ошибка при сохранении: {error}")
        return False

    def load(self, filename: str = "data.dat") -> bool:
        try:
            with open(filename, "rb") as file:
                data = pickle.load(file)
                if not isinstance(data, dict):
                    raise ValueError("Некорректная структура данных в файле.")

            self.book.users = data.get("users", {})
            self.book.max_user_id = data.get("max_user_id", 0)
            self.book.max_request_id = data.get("max_request_id", 0)
            self.book.restore_io_links()
            self.book.io.output_message(f"Данные успешно загружены из файла '{filename}'.")
            return True
        except FileNotFoundError:
            self.book.io.output_error(f"Файл '{filename}' не найден.")
        except EOFError:
            self.book.io.output_error("Файл пуст или данные в нем неполные.")
        except pickle.UnpicklingError:
            self.book.io.output_error("Не удалось распознать данные файла pickle.")
        except OSError as error:
            self.book.io.output_error(f"Ошибка ввода-вывода при загрузке: {error}")
        except Exception as error:
            self.book.io.output_error(f"Непредвиденная ошибка при загрузке: {error}")
        return False
