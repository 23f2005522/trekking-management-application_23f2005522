from flask import Blueprint
from controller import auth_controller as auth_ctrl

auth_bp = Blueprint("authentication", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    return auth_ctrl.login()


@auth_bp.route("/logout", methods=["GET"])
def logout():
    return auth_ctrl.logout()


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    return auth_ctrl.register()
