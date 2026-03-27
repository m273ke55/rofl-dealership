from user_book import UserBook


def main():
    system = UserBook()

    while True:
        system.io.output_separator()
        system.io.output_message("Главное меню")
        system.io.output_message("1. Все пользователи")
        system.io.output_message("2. Новый пользователь")
        system.io.output_message("3. Изменить пользователя")
        system.io.output_message("4. Удалить пользователя")
        system.io.output_message("5. Войти в пользователя")
        system.io.output_message("6. Сохранить")
        system.io.output_message("7. Загрузить")
        system.io.output_message("8. Очистить список")
        system.io.output_message("0. Выход")

        choice = system.io.input_int("Выберите пункт меню")

        if choice == 0:
            system.io.output_message("Программа завершена.")
            break
        elif choice == 1:
            system.list_users()
        elif choice == 2:
            system.add_user()
        elif choice == 3:
            system.edit_user()
        elif choice == 4:
            system.delete_user()
        elif choice == 5:
            system.login_user()
        elif choice == 6:
            system.save_to_file()
        elif choice == 7:
            system.load_from_file()
        elif choice == 8:
            system.clear()
        else:
            system.io.output_error("Некорректный выбор пункта меню.")


main()
