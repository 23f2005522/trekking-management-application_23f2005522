from flask import request,Blueprint,render_template,redirect,flash,session
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
                    {"value": UserRole.TREKKER, "label": "Trekker"},
                    {"value": UserRole.STAFF, "label": "Trek Staff"},
                    {"value": UserRole.ADMIN, "label": "Admin"},
                ],
            },
        ]

        return render_template("login.html", form_fields=form_fields)
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:

            flash("Please provide both email and password.", "danger")
            return redirect("/auth/login")

        user = UserModel.query.filter(UserModel.email == email).first()

        if not user:
            flash("User not found. Please register first.", "danger")
            return redirect("/auth/register")

        if user.check_password(password):
            session["user_id"] = user.id
            session["user_role"] = user.role  # Store the user's role in the session
            flash("Login successful!", "success")

        return redirect


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
        return
