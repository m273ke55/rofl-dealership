from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app_state import get_state
from domain_service import authenticate, register_user

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        user, error = authenticate(get_state().user_book, email, password)
        if error:
            flash(error, "error")
            return render_template("auth/login.html")

        session["user_id"] = user.id
        session["is_admin"] = getattr(user, "role", "user") == "admin"
        flash("Вход выполнен успешно.", "success")
        if session["is_admin"]:
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("profile.profile"))

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        form = request.form
        user, error = register_user(
            get_state().user_book,
            form.get("first_name", ""),
            form.get("last_name", ""),
            form.get("middle_name", ""),
            form.get("phone", ""),
            form.get("email", ""),
            form.get("password", ""),
            form.get("password_confirm", ""),
        )
        if error:
            flash(error, "error")
            return render_template("auth/register.html")

        state = get_state()
        state.save()
        session["user_id"] = user.id
        session["is_admin"] = False
        flash("Регистрация прошла успешно.", "success")
        return redirect(url_for("profile.profile"))

    return render_template("auth/register.html")


@auth_bp.post("/logout")
def logout():
    session.clear()
    flash("Вы вышли из аккаунта.", "success")
    return redirect(url_for("public.index"))
