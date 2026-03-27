import pickle


class PickleStorage:
    def __init__(self, user_system):
        self.user_system = user_system

    def save(self, filename="data.dat"):
        try:
            data = {
                "users": self.user_system.users,
                "max_user_id": self.user_system.max_user_id,
                "max_request_id": self.user_system.max_request_id,
            }
            with open(filename, "wb") as file:
                pickle.dump(data, file)

            self.user_system.io.output_message(f"Данные успешно сохранены в файл '{filename}'.")
            return True
        except FileNotFoundError:
            self.user_system.io.output_error(f"Файл '{filename}' не найден.")
        except OSError as error:
            self.user_system.io.output_error(f"Ошибка ввода-вывода при сохранении: {error}")
        except Exception as error:
            self.user_system.io.output_error(f"Непредвиденная ошибка при сохранении: {error}")

        return False

    def load(self, filename="data.dat"):
        try:
            with open(filename, "rb") as file:
                data = pickle.load(file)

            if not isinstance(data, dict):
                raise ValueError("Некорректная структура данных в файле.")

            self.user_system.users = data.get("users", {})
            self.user_system.max_user_id = data.get("max_user_id", 0)
            self.user_system.max_request_id = data.get("max_request_id", 0)
            self.user_system.restore_io_links()
            self.user_system.io.output_message(f"Данные успешно загружены из файла '{filename}'.")
            return True
        except FileNotFoundError:
            self.user_system.io.output_error(f"Файл '{filename}' не найден.")
        except EOFError:
            self.user_system.io.output_error("Файл пуст или данные в нем неполные.")
        except pickle.UnpicklingError:
            self.user_system.io.output_error("Не удалось распознать данные файла pickle.")
        except OSError as error:
            self.user_system.io.output_error(f"Ошибка ввода-вывода при загрузке: {error}")
        except Exception as error:
            self.user_system.io.output_error(f"Непредвиденная ошибка при загрузке: {error}")

        return False
