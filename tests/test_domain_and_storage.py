import os
import tempfile
import unittest

from app_state import AppState, NullIO
from domain_service import (
    authenticate,
    cancel_request,
    change_password,
    create_consultation_request,
    create_service_request,
    get_free_service_dates,
    register_user,
    update_profile,
)
from request import Request
from user import User
from user_book import UserBook


class DomainFlowTests(unittest.TestCase):
    def setUp(self):
        self.book = UserBook(io=NullIO())

    def test_registration_and_duplicate_and_password_mismatch(self):
        user, error = register_user(
            self.book,
            "Иван",
            "Иванов",
            "Иванович",
            "+79991234567",
            "ivan@example.com",
            "secret",
            "secret",
        )
        self.assertIsNotNone(user)
        self.assertIsNone(error)

        duplicate_user, duplicate_error = register_user(
            self.book,
            "Иван",
            "Иванов",
            "Иванович",
            "+79991234567",
            "ivan@example.com",
            "secret",
            "secret",
        )
        self.assertIsNone(duplicate_user)
        self.assertIn("уже существует", duplicate_error)

        bad_user, bad_error = register_user(
            self.book,
            "Петр",
            "Петров",
            "Петрович",
            "+79997654321",
            "petr@example.com",
            "a",
            "b",
        )
        self.assertIsNone(bad_user)
        self.assertIn("не совпадают", bad_error)

    def test_auth_update_password_and_requests_lifecycle(self):
        user, _ = register_user(
            self.book,
            "Анна",
            "Сидорова",
            "Игоревна",
            "+79990001122",
            "anna@example.com",
            "123",
            "123",
        )

        auth_user, auth_error = authenticate(self.book, "anna@example.com", "123")
        self.assertIsNotNone(auth_user)
        self.assertIsNone(auth_error)

        missing_user, missing_error = authenticate(self.book, "absent@example.com", "123")
        self.assertIsNone(missing_user)
        self.assertIn("не зарегистрированы", missing_error)

        wrong_user, wrong_error = authenticate(self.book, "anna@example.com", "bad")
        self.assertIsNone(wrong_user)
        self.assertIn("Неверный логин", wrong_error)

        self.assertIsNone(
            update_profile(
                user,
                "Анна",
                "Сидорова",
                "Игоревна",
                "+79995554433",
                "anna2@example.com",
            )
        )
        self.assertIn(
            "Неверный номер",
            update_profile(user, "Анна", "Сидорова", "Игоревна", "123", "anna2@example.com"),
        )

        self.assertIsNone(change_password(user, "123", "new-password", "new-password"))
        self.assertIn("Неверный текущий", change_password(user, "123", "x", "x"))

        self.assertIsNotNone(authenticate(self.book, "anna2@example.com", "new-password")[0])
        self.assertIn("Неверный логин", authenticate(self.book, "anna2@example.com", "123")[1])

        consultation = create_consultation_request(self.book, user)
        self.assertEqual("consultation", consultation.type)

        free_dates = get_free_service_dates(self.book)
        self.assertTrue(free_dates)

        service_request, service_error = create_service_request(self.book, user, free_dates[0])
        self.assertIsNotNone(service_request)
        self.assertIsNone(service_error)

        _, busy_error = create_service_request(self.book, user, free_dates[0])
        self.assertIn("занята", busy_error)

        self.assertIsNone(cancel_request(user, service_request.id))
        self.assertIn("уже отменена", cancel_request(user, service_request.id))


class StorageCompatibilityTests(unittest.TestCase):
    def test_pickle_compatibility_without_role_field(self):
        fd, path = tempfile.mkstemp(suffix=".dat")
        os.close(fd)

        try:
            source_book = UserBook(io=NullIO())
            source_state = AppState(source_book, data_file=path)

            legacy_user = User(
                1,
                "Алексей",
                "Тестов",
                "Старый",
                "+79990000000",
                "legacy@example.com",
                "pwd",
                io=source_book.io,
            )
            delattr(legacy_user, "role")
            legacy_user.add_request(Request(1, "consultation", io=source_book.io))

            source_book.users[1] = legacy_user
            source_book.max_user_id = 1
            source_book.max_request_id = 1
            source_state.save()

            loaded_book = UserBook(io=NullIO())
            loaded_state = AppState(loaded_book, data_file=path)
            loaded_state.load()

            restored = loaded_book.find_user_by_id(1)
            self.assertIsNotNone(restored)
            self.assertEqual("user", getattr(restored, "role", None))
            self.assertEqual(1, loaded_book.max_request_id)
            self.assertGreaterEqual(loaded_book.max_user_id, 1)
        finally:
            if os.path.exists(path):
                os.remove(path)


if __name__ == "__main__":
    unittest.main()
