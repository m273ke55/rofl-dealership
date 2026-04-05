from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, session, url_for

from app_state import get_state
from domain_service import change_password, update_profile

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return get_state().user_book.find_user_by_id(user_id)


@profile_bp.get("")
def profile():
    user = get_current_user()
    if user is None:
        flash("Требуется авторизация.", "error")
        return redirect(url_for("auth.login"))
    active_requests = [r for r in user.requests if r.status == "active"]
    return render_template("profile/profile.html", user=user, active_requests=active_requests)


@profile_bp.get("/edit")
def edit_profile_page():
    user = get_current_user()
    if user is None:
        flash("Требуется авторизация.", "error")
        return redirect(url_for("auth.login"))
    return render_template("profile/edit_profile.html", user=user)


@profile_bp.put("/edit")
def edit_profile_put():
    user = get_current_user()
    if user is None:
        abort(401)

    data = request.get_json(silent=True) or request.form
    error = update_profile(
        user,
        data.get("first_name", ""),
        data.get("last_name", ""),
        data.get("middle_name", ""),
        data.get("phone", ""),
        data.get("email", ""),
    )
    if error:
        return jsonify({"ok": False, "error": f"Неверный формат данных: {error}"}), 400

    get_state().save()
    return jsonify({"ok": True, "message": "Профиль обновлён."})


@profile_bp.get("/change-password")
def change_password_page():
    user = get_current_user()
    if user is None:
        flash("Требуется авторизация.", "error")
        return redirect(url_for("auth.login"))
    return render_template("profile/change_password.html")


@profile_bp.put("/change-password")
def change_password_put():
    user = get_current_user()
    if user is None:
        abort(401)

    data = request.get_json(silent=True) or request.form
    error = change_password(
        user,
        data.get("old_password", ""),
        data.get("new_password", ""),
        data.get("confirm_password", ""),
    )
    if error:
        return jsonify({"ok": False, "error": error}), 400

    get_state().save()
    return jsonify({"ok": True, "message": "Пароль изменён."})
