import re

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app_state import get_state
from domain_service import create_consultation_request

public_bp = Blueprint("public", __name__)

PHONE_PATTERN = re.compile(r"^\+?\d{10,15}$")

CARS = [
    {
        "id": 1,
        "model": "Audi Q5",
        "price": 4200000,
        "condition": "new",
        "image": "images/cars/car_audi_q5.png",
        "year": 2026,
    },
    {
        "id": 2,
        "model": "BMW X3",
        "price": 3600000,
        "condition": "new",
        "image": "images/cars/buy_page_car.png",
        "year": 2025,
    },
    {
        "id": 3,
        "model": "Kia Sportage",
        "price": 2800000,
        "condition": "new",
        "image": "images/cars/sell_page_car.png",
        "year": 2025,
    },
]


@public_bp.get("/")
def index():
    return render_template("index.html")


@public_bp.get("/buy")
def buy():
    condition = request.args.get("condition", "all")
    price_from = request.args.get("price_from", "")
    price_to = request.args.get("price_to", "")
    error = None

    cars = CARS
    used_exists = any(car["condition"] == "used" for car in CARS)

    if condition in {"new", "used"}:
        cars = [car for car in cars if car["condition"] == condition]

    if price_from or price_to:
        try:
            min_price = int(price_from) if price_from else None
            max_price = int(price_to) if price_to else None
            if min_price is not None and max_price is not None and min_price > max_price:
                error = "Некорректный диапазон цен: поле «от» больше поля «до»."
                cars = []
            else:
                if min_price is not None:
                    cars = [car for car in cars if car["price"] >= min_price]
                if max_price is not None:
                    cars = [car for car in cars if car["price"] <= max_price]
        except ValueError:
            error = "Некорректный диапазон цен: введите целые числа."
            cars = []

    return render_template(
        "buy.html",
        cars=cars,
        condition=condition,
        price_from=price_from,
        price_to=price_to,
        error=error,
        used_exists=used_exists,
    )


@public_bp.post("/consultation")
def consultation_submit():
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    next_url = request.form.get("next", url_for("public.services"))

    if not name:
        flash("Заполните имя для консультации.", "error")
        return redirect(next_url)

    if not PHONE_PATTERN.match(phone):
        flash("Неверный номер телефона для консультации.", "error")
        return redirect(next_url)

    user_id = session.get("user_id")
    if user_id:
        user = get_state().user_book.find_user_by_id(user_id)
        if user is not None:
            create_consultation_request(get_state().user_book, user)
            get_state().save()
            flash("Заявка на консультацию создана и добавлена в личный кабинет.", "success")
            return redirect(next_url)

    flash("Заявка на консультацию отправлена. Мы свяжемся с вами.", "success")
    return redirect(next_url)


@public_bp.route("/sell", methods=["GET", "POST"])
def sell():
    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        if not PHONE_PATTERN.match(phone):
            flash("Неверный номер телефона.", "error")
            return render_template("sell.html")
        flash("Заявка на продажу отправлена.", "success")
    return render_template("sell.html")


@public_bp.get("/services")
def services():
    return render_template("services.html")


@public_bp.get("/service")
def service_landing():
    return render_template("service.html")
