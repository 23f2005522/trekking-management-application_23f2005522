from flask import request,Blueprint,render_template,redirect,flash,session
from utils.authentication import is_logged_in, role_required
from model.model import *
trek_staff_bp = Blueprint("trekk_staff_routes", __name__, url_prefix="/trekstaff")


@trek_staff_bp.route("/dashboard")
@is_logged_in
@role_required(UserRole.STAFF)
def dashboard():
    if request.method == "GET":
        return render_template("trekStaff/dashboard.html")