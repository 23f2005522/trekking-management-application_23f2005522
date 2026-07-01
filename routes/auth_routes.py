from flask import (
    request,
    Blueprint,
    render_template,
    redirect,
    flash,
    session,
    current_app,
)
from model.model import *

auth_bp = Blueprint("authentication", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
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

    if request.method == "POST":
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

        # check if the role matches
        if user.role.value.lower() != role.lower():
            flash("Incorrect role selected for this user.", "danger")
            return redirect("/auth/login")

        # if user is staff and not approved yet
        if (
            user.role == UserRole.STAFF
            and not user.staff_profile.Profile_status == StaffStatus.APPROVED
        ):
            flash(
                "Your staff registration is pending approval. Please wait for admin approval.",
                "info",
            )
            return redirect("/auth/login")

        # check password
        if not user.check_password(password):
            flash("Invalid user role.", "danger")
            return redirect("/auth/login")
        session["user_id"] = user.id
        session["user_role"] = user.role  
        flash("Login successful!", "success")

        # redirect to role-based dashboard
        if user.role == UserRole.TREKKER:
            return redirect("/trekker/dashboard")
        elif user.role == UserRole.STAFF:
            return redirect("/trekstaff/dashboard")
        elif user.role == UserRole.ADMIN:
            return redirect("/admin/dashboard")
        else:
            flash("Invalid user role.", "danger")
            return redirect("/auth/login")


@auth_bp.route("/logout", methods=["GET"])
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect("/")


@auth_bp.route("/register", methods=["GET", "POST"])
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
            {
                "name": "role",
                "label": "Register As",
                "type": "radio",
                "required": True,
                "options": [
                    {
                        "value": UserRole.TREKKER.value,
                        "label": "Trekker",
                    },
                    {
                        "value": UserRole.STAFF.value,
                        "label": "Trek Staff",
                    },
                ],
            },
        ]

        return render_template("register.html", form_fields=form_fields)
    if request.method == "POST":
        try:
            # form Data
            username = request.form.get("username")
            email = request.form.get("email")
            phone = request.form.get("phone")
            password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")
            role = request.form.get("role")

            # if any data is missing
            if (
                not username
                or not email
                or not phone
                or not password
                or not confirm_password
                or not role
            ):
                flash("Please provide all required fields.", "danger")
                return redirect("/auth/register")

            # check if passwords match
            if password != confirm_password:
                flash("Passwords do not match.", "danger")
                return redirect("/auth/register")

            # if anyuser with same email or phone already exists
            user_email_exists = UserModel.query.filter_by(email=email).first()
            user_phone_exists = UserModel.query.filter_by(phone=phone).first()
            if user_email_exists or user_phone_exists:
                flash(
                    "An user with this email/phone already exists. Please log in.",
                    "danger",
                )
                return redirect("/auth/login")

            # for trekker registration
            if role == UserRole.TREKKER.value:
                user = UserModel(
                    username=username, email=email, phone=phone, role=UserRole.TREKKER
                )
                user.set_password(password)
                db.session.add(user)
                db.session.commit()

                flash("Trekker Registration successful! Please log in.", "success")
                return redirect("/auth/login")

            # for trek staff registration
            if role == UserRole.STAFF.value:

                # if trek staff already was created but not approved yet by admin
                if user and user.role == UserRole.STAFF and user.is_approved == False:
                    flash(
                        "Your staff registration is pending approval. Please wait for admin approval.",
                        "info",
                    )
                    return redirect("/auth/login")

                user = UserModel(
                    username=username, email=email, phone=phone, role=UserRole.STAFF
                )
                user.set_password(password)
                db.session.add(user)
                db.session.flush()
                staff_profile = StaffModel(user_id=user.id)
                db.session.add(staff_profile)
                db.session.commit()

                flash(
                    "Trek Staff Registration successful! Please wait for admin approval.",
                    "success",
                )
                return redirect("/auth/login")

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error during registration: {e}")
            flash("An error occurred during registration", "danger")
            return redirect("/auth/register")
