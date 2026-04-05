# ROFL Dealership — Flask WSGI

Веб-версия лабораторной работы на Flask с сохранением доменной модели и pickle-хранения из консольной версии.

## Запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install flask
python app.py
```

или через WSGI entrypoint:

```bash
python wsgi.py
```

## Legacy-консоль

Консольная версия сохранена:

```bash
python legacy/main_console.py
```

## Администратор по умолчанию

- Логин (email): `admin@rofl.local`
- Пароль: `admin123`

## Важно про хранение

Используется тот же pickle-формат (`users`, `max_user_id`, `max_request_id`), что и в консольной лабораторной.
Файл по умолчанию: `data.dat`.
