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


@trekker_bp.route("/treks", methods=["GET"])
@is_logged_in
@role_required(UserRole.TREKKER)
def browse_treks():
    return trekker_ctrl.browse_treks()


@trekker_bp.route("/booktrek", methods=["POST"])
@is_logged_in
@role_required(UserRole.TREKKER)
def book_trek():
    return trekker_ctrl.book_trek()


@trekker_bp.route("/bookings", methods=["GET"])
@is_logged_in
@role_required(UserRole.TREKKER)
def my_bookings():
    return trekker_ctrl.my_bookings()


@trekker_bp.route("/deletebooking/<int:booking_id>", methods=["GET"])
@is_logged_in
@role_required(UserRole.TREKKER)
def cancel_booking(booking_id):
    return trekker_ctrl.cancel_booking(booking_id)


@trekker_bp.route("/history", methods=["GET"])
@is_logged_in
@role_required(UserRole.TREKKER)
def trekking_history():
    return trekker_ctrl.trekking_history()


@trekker_bp.route("/profile", methods=["GET", "POST"])
@is_logged_in
@role_required(UserRole.TREKKER)
def trekker_profile():
    return trekker_ctrl.trekker_profile()
