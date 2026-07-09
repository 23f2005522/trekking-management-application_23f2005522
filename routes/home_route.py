from flask import Blueprint
from controller import home_controller as home_ctrl

home_bp = Blueprint("home", __name__, url_prefix="/")


@home_bp.route("/", methods=["GET"])
def home():
    return home_ctrl.home()
