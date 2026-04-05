from flask import Blueprint, abort, flash, jsonify, redirect, render_template, session, url_for

from app_state import get_state

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def ensure_admin():
    user_id = session.get("user_id")
    is_admin = session.get("is_admin", False)
    if not user_id or not is_admin:
        abort(403)


@admin_bp.get("")
def dashboard():
    ensure_admin()
    users = list(get_state().user_book.users.values())
    total_requests = sum(len(u.requests) for u in users)
    return render_template("admin/dashboard.html", users=users, total_requests=total_requests)


@admin_bp.get("/users")
def users_list():
    ensure_admin()
    users = sorted(get_state().user_book.users.values(), key=lambda u: u.id)
    return render_template("admin/users.html", users=users)


@admin_bp.get("/users/<int:user_id>")
def user_detail(user_id):
    ensure_admin()
    user = get_state().user_book.find_user_by_id(user_id)
    if user is None:
        flash("Пользователь не найден.", "error")
        return redirect(url_for("admin.users_list"))
    return render_template("admin/user_detail.html", user=user)


@admin_bp.delete("/users/<int:user_id>")
def user_delete(user_id):
    ensure_admin()
    state = get_state()
    user = state.user_book.find_user_by_id(user_id)
    if user is None:
        return jsonify({"ok": False, "error": "Пользователь не найден."}), 404

    if getattr(user, "role", "user") == "admin":
        return jsonify({"ok": False, "error": "Нельзя удалить администратора."}), 400

    del state.user_book.users[user_id]
    state.save()
    return jsonify({"ok": True, "message": "Пользователь удалён."})


@admin_bp.post("/storage/save")
def save_data():
    ensure_admin()
    get_state().save()
    flash("Данные сохранены в файл.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.post("/storage/load")
def load_data():
    ensure_admin()
    get_state().load()
    flash("Данные загружены из файла.", "success")
    return redirect(url_for("admin.dashboard"))
