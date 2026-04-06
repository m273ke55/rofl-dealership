import re

from request import Request
from user import User

PHONE_PATTERN = re.compile(r"^\+?\d{10,15}$")


def validate_profile_data(first_name, last_name, middle_name, phone, email):
    if not first_name.strip() or not last_name.strip() or not middle_name.strip():
        return "ФИО должно быть заполнено полностью."
    if not PHONE_PATTERN.match(phone.strip()):
        return "Неверный номер телефона. Используйте формат +79991234567."
    if "@" not in email or email.startswith("@") or email.endswith("@"):
        return "Неверный формат email."
    return None


def register_user(book, first_name, last_name, middle_name, phone, email, password, password_confirm):
    error = validate_profile_data(first_name, last_name, middle_name, phone, email)
    if error:
        return None, error
    if password != password_confirm:
        return None, "Пароли не совпадают."
    if not password:
        return None, "Пароль не может быть пустым."

    for user in book.users.values():
        if user.email.lower() == email.lower():
            return None, "Пользователь с таким email уже существует."

    new_id = book.max_user_id + 1
    user = User(
        user_id=new_id,
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        middle_name=middle_name.strip(),
        phone=phone.strip(),
        email=email.strip(),
        password=password,
        io=book.io,
    )
    book.users[new_id] = user
    book.max_user_id = new_id
    return user, None


def authenticate(book, email, password):
    for user in book.users.values():
        if user.email.lower() == email.lower():
            if user.password == password:
                return user, None
            return None, "Неверный логин или пароль."
    return None, "Вы не зарегистрированы."


def update_profile(user, first_name, last_name, middle_name, phone, email):
    error = validate_profile_data(first_name, last_name, middle_name, phone, email)
    if error:
        return error

    user.first_name = first_name.strip()
    user.last_name = last_name.strip()
    user.middle_name = middle_name.strip()
    user.phone = phone.strip()
    user.email = email.strip()
    return None


def change_password(user, old_password, new_password, confirm_password):
    if user.password != old_password:
        return "Неверный текущий пароль."
    if new_password != confirm_password:
        return "Пароли не совпадают."
    if not new_password:
        return "Новый пароль не может быть пустым."
    user.password = new_password
    return None


def create_consultation_request(book, user):
    new_id = book.max_request_id + 1
    request = Request(request_id=new_id, request_type="consultation", date=None, status="active", io=book.io)
    user.add_request(request)
    book.max_request_id = new_id
    return request


def get_free_service_dates(book):
    return book._get_free_service_dates()


def create_service_request(book, user, date):
    free_dates = get_free_service_dates(book)
    if date not in book.service_dates:
        return None, "Некорректная дата сервиса."
    if date not in free_dates:
        return None, "Выбранная дата уже занята."

    new_id = book.max_request_id + 1
    request = Request(request_id=new_id, request_type="service", date=date, status="active", io=book.io)
    user.add_request(request)
    book.max_request_id = new_id
    return request, None


def cancel_request(user, request_id):
    request = user.find_request_by_id(request_id)
    if request is None:
        return "Заявка не найдена."
    if request.status == "cancelled":
        return "Заявка уже отменена."
    user.cancel_request(request_id)
    return None
