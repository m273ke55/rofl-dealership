from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, session, url_for

from app_state import get_state
from domain_service import cancel_request, create_consultation_request, create_service_request, get_free_service_dates

requests_bp = Blueprint("requests", __name__, url_prefix="/requests")


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return get_state().user_book.find_user_by_id(user_id)


def _service_calendar_context(selected_date=""):
    book = get_state().user_book
    free_dates = get_free_service_dates(book)
    busy_dates = [date for date in book.service_dates if date not in free_dates]
    return {
        "all_dates": book.service_dates,
        "free_dates": free_dates,
        "busy_dates": busy_dates,
        "selected_date": selected_date,
    }


@requests_bp.get("")
def list_requests():
    user = get_current_user()
    if user is None:
        flash("Требуется авторизация.", "error")
        return redirect(url_for("auth.login"))

    active_requests = [r for r in user.requests if r.status == "active"]
    return render_template("profile/requests.html", user=user, active_requests=active_requests)


@requests_bp.post("/consultation")
def consultation_create():
    user = get_current_user()
    if user is None:
        flash("Требуется авторизация.", "error")
        return redirect(url_for("auth.login"))

    create_consultation_request(get_state().user_book, user)
    get_state().save()
    flash("Заявка на консультацию создана.", "success")
    return redirect(url_for("requests.list_requests"))


@requests_bp.get("/service")
def service_form():
    user = get_current_user()
    if user is None:
        flash("Требуется авторизация.", "error")
        return redirect(url_for("auth.login"))

    return render_template("service_booking.html", **_service_calendar_context())


@requests_bp.post("/service")
def service_create():
    user = get_current_user()
    if user is None:
        flash("Требуется авторизация.", "error")
        return redirect(url_for("auth.login"))

    date = request.form.get("date", "")
    ctx = _service_calendar_context(selected_date=date)

    if not ctx["free_dates"]:
        flash("Нет доступных дат для сервиса.", "error")
        return render_template("service_booking.html", **ctx)

    req, error = create_service_request(get_state().user_book, user, date)
    if error:
        if "занята" in error:
            flash("Выбранная дата уже занята. Выберите другую.", "error")
        else:
            flash(error, "error")
        return render_template("service_booking.html", **ctx)

    get_state().save()
    flash(f"Сервисная заявка №{req.id} создана.", "success")
    return redirect(url_for("requests.list_requests"))


@requests_bp.delete("/<int:request_id>")
def request_delete(request_id):
    user = get_current_user()
    if user is None:
        abort(401)

    error = cancel_request(user, request_id)
    if error:
        return jsonify({"ok": False, "error": error}), 404

    get_state().save()
    return jsonify({"ok": True, "message": "Заявка отменена."})
