from flask import request,Blueprint,render_template,redirect,flash,session
from utils.authentication import is_logged_in, role_required
from model.model import *
trekker_bp = Blueprint("trekker_routes", __name__, url_prefix="/trekker")


@trekker_bp.route("/dashboard")
@is_logged_in
@role_required(UserRole.TREKKER)
def dashboard():
    if request.method == "GET":
        return render_template("trekker/dashboard.html")