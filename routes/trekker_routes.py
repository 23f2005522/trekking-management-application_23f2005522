from flask import Blueprint
from utils.authentication import is_logged_in, role_required
from model.model import UserRole
from controller import trekker_controller as trekker_ctrl

trekker_bp = Blueprint("trekker_routes", __name__, url_prefix="/trekker")


@trekker_bp.route("/dashboard")
@is_logged_in
@role_required(UserRole.TREKKER)
def dashboard():
    return trekker_ctrl.dashboard()
