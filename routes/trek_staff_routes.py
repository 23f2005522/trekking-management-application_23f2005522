from flask import Blueprint
from utils.authentication import is_logged_in, role_required
from model.model import UserRole
from controller import trek_staff_controller as trek_staff_ctrl

trek_staff_bp = Blueprint("trekk_staff_routes", __name__, url_prefix="/trekstaff")


@trek_staff_bp.route("/dashboard")
@is_logged_in
@role_required(UserRole.STAFF)
def dashboard():
    return trek_staff_ctrl.dashboard()
