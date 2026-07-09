from flask import request, render_template, redirect, flash, session, current_app
from model.model import *


def login():
    if request.method == "GET":
        form_fields = [
            {"name": "email", "type": "email", "placeholder": "Enter your email"},
            {
                "name": "password",
                "type": "password",
                "placeholder": "Enter your password",
            },
            {
                "name": "role",
                "type": "radio",
                "options": [
                    {"value": UserRole.TREKKER.value.lower(), "label": "Trekker"},
                    {"value": UserRole.STAFF.value.lower(), "label": "Trek Staff"},
                    {"value": UserRole.ADMIN.value.lower(), "label": "Admin"},
                ],
            },
        ]
        return render_template("login.html", form_fields=form_fields)

    email = request.form.get("email")
    password = request.form.get("password")
    role = request.form.get("role")

    if not email or not password or not role:
        flash("Please provide all required fields.", "danger")
        return redirect("/auth/login")

    user = UserModel.query.filter(UserModel.email == email).first()

    if not user:
        flash("User not found. Please register first.", "danger")
        return redirect("/auth/register")

    if user.role.value.lower() != role.lower():
        flash("Incorrect role selected for this user.", "danger")
        return redirect("/auth/login")

    # if the user is a staff [pending]
    if user.role == UserRole.STAFF:
        staff_status = user.staff_profile.Profile_status

        if staff_status == StaffStatus.PENDING:
            flash(
                "Your staff account is pending approval. Please wait for admin approval.",
                "info",
            )
            return redirect("/auth/login")

        if staff_status == StaffStatus.REJECTED:
            flash("Your staff account has been rejected.", "danger")
            return redirect("/auth/login")

        if staff_status == StaffStatus.BLACKLISTED:
            flash("Your staff account has been blacklisted.", "danger")
            return redirect("/auth/login")

    # if the user is a trekker [deactivated or blacklisted]
    if user.role == UserRole.TREKKER:
        if not user.is_active:
            flash("Your trekker account has been deactivated. Contact admin.", "danger")
            return redirect("/auth/login")

        if user.is_blacklisted:
            flash("Your trekker account has been blacklisted.", "danger")
            return redirect("/auth/login")

    if not user.check_password(password):
        flash("Invalid user role.", "danger")
        return redirect("/auth/login")

    session["user_id"] = user.id
    session["user_role"] = user.role
    flash("Login successful!", "success")

    if user.role == UserRole.TREKKER:
        return redirect("/trekker/dashboard")
    if user.role == UserRole.STAFF:
        return redirect("/trekstaff/dashboard")
    if user.role == UserRole.ADMIN:
        return redirect("/admin/dashboard")

    flash("Invalid user role.", "danger")
    return redirect("/auth/login")


def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect("/")


def register():
    if request.method == "GET":
        form_fields = [
            {
                "name": "username",
                "label": "Username",
                "type": "text",
                "placeholder": "Enter your username",
                "required": True,
            },
            {
                "name": "email",
                "label": "Email Address",
                "type": "email",
                "placeholder": "Enter your email",
                "required": True,
            },
            {
                "name": "phone",
                "label": "Phone Number",
                "type": "tel",
                "placeholder": "Enter your phone number",
                "required": True,
            },
            {
                "name": "password",
                "label": "Password",
                "type": "password",
                "placeholder": "Enter your password",
                "required": True,
            },
            {
                "name": "confirm_password",
                "label": "Confirm Password",
                "type": "password",
                "placeholder": "Re-enter your password",
                "required": True,
            },
        ]
        return render_template("register.html", form_fields=form_fields)

    try:
        username = request.form.get("username")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if (
            not username
            or not email
            or not phone
            or not password
            or not confirm_password
        ):
            flash("Please provide all required fields.", "danger")
            return redirect("/auth/register")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect("/auth/register")

        user_email_exists = UserModel.query.filter_by(email=email).first()
        user_phone_exists = UserModel.query.filter_by(phone=phone).first()
        if user_email_exists or user_phone_exists:
            flash(
                "An user with this email/phone already exists. Please log in.",
                "danger",
            )
            return redirect("/auth/login")

        user = UserModel(
            username=username, email=email, phone=phone, role=UserRole.TREKKER
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Trekker Registration successful! Please log in.", "success")
        return redirect("/auth/login")

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error during registration: {e}")
        flash("An error occurred during registration", "danger")
        return redirect("/auth/register")
