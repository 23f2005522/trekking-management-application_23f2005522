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


@trek_staff_bp.route("/my-treks")
@is_logged_in
@role_required(UserRole.STAFF)
def my_treks():
    return trek_staff_ctrl.my_treks()


@trek_staff_bp.route("/manage-trek/<int:trek_id>", methods=["GET", "POST"])
@is_logged_in
@role_required(UserRole.STAFF)
def manage_trek(trek_id):
    return trek_staff_ctrl.manage_trek(trek_id)


@trek_staff_bp.route("/manage-trek/<int:trek_id>/mark-started", methods=["POST"])
@is_logged_in
@role_required(UserRole.STAFF)
def mark_trek_started(trek_id):
    return trek_staff_ctrl.mark_trek_started(trek_id)


@trek_staff_bp.route("/manage-trek/<int:trek_id>/mark-completed", methods=["POST"])
@is_logged_in
@role_required(UserRole.STAFF)
def mark_trek_completed(trek_id):
    return trek_staff_ctrl.mark_trek_completed(trek_id)


@trek_staff_bp.route("/participants")
@is_logged_in
@role_required(UserRole.STAFF)
def participants():
    return trek_staff_ctrl.participants()


@trek_staff_bp.route("/toggle-payment/<int:booking_id>", methods=["POST"])
@is_logged_in
@role_required(UserRole.STAFF)
def toggle_payment(booking_id):
    return trek_staff_ctrl.toggle_payment(booking_id)


@trek_staff_bp.route("/profile")
@is_logged_in
@role_required(UserRole.STAFF)
def staff_profile():
    return trek_staff_ctrl.staff_profile()
