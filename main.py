from __future__ import annotations

from user_book import UserBook


def main() -> None:
    book = UserBook()
    actions = {
        1: book.list_users,
        2: book.add_user,
        3: book.edit_user,
        4: book.delete_user,
        5: book.login_user,
        6: book.save_to_file,
        7: book.load_from_file,
        8: book.clear,
    }

    while True:
        book.io.output_separator()
        book.io.output_message("Главное меню")
        book.io.output_message("1. Все пользователи")
        book.io.output_message("2. Новый пользователь")
        book.io.output_message("3. Изменить пользователя")
        book.io.output_message("4. Удалить пользователя")
        book.io.output_message("5. Войти в пользователя")
        book.io.output_message("6. Сохранить")
        book.io.output_message("7. Загрузить")
        book.io.output_message("8. Очистить список")
        book.io.output_message("0. Выход")

        choice = book.io.input_int("Выберите пункт меню")
        if choice == 0:
            book.io.output_message("Программа завершена.")
            break

        action = actions.get(choice)
        if action is None:
            book.io.output_error("Некорректный выбор пункта меню.")
            continue
        action()


if __name__ == "__main__":
    main()
