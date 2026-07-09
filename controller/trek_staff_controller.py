from flask import render_template, redirect, session, url_for, flash, request
from model.model import *


def get_current_staff():
    """Returns the staff profile of the logged-in user using session user_id."""
    user_id = session.get("user_id")
    return StaffModel.query.filter_by(user_id=user_id).first()


def get_assigned_trek(staff, trek_id):
    """Returns the trek only if it is assigned to the given staff member."""
    if not staff:
        return None
    return TrekModel.query.filter_by(
        id=trek_id, assigned_staff_id=staff.id
    ).first()


def load_trek_stats(treks):
    """Adds booked_participants count on each trek (only BOOKED bookings)."""
    for trek in treks:
        trek.booked_participants = len(
            [b for b in trek.bookings if b.status == BookingStatus.BOOKED]
        )
    return treks


# Staff dashboard with stats and recent assigned treks
def dashboard():
    staff = get_current_staff()
    if not staff:
        flash("Staff not found.", "danger")
        return redirect(url_for("authentication.login"))

    all_assigned_treks = (
        TrekModel.query.filter_by(assigned_staff_id=staff.id)
        .order_by(TrekModel.id.desc())
        .all()
    )
    load_trek_stats(all_assigned_treks)

    total_assigned_treks = len(all_assigned_treks)
    total_participants = sum(t.booked_participants for t in all_assigned_treks)
    open_treks_count = len(
        [t for t in all_assigned_treks if t.status == TrekStatus.OPEN]
    )
    started_treks_count = len(
        [t for t in all_assigned_treks if t.status == TrekStatus.STARTED]
    )

    assigned_treks = all_assigned_treks[:5]

    return render_template(
        "trekStaff/dashboard.html",
        staff=staff,
        user=staff.user,
        assigned_treks=assigned_treks,
        total_assigned_treks=total_assigned_treks,
        total_participants=total_participants,
        open_treks_count=open_treks_count,
        started_treks_count=started_treks_count,
    )


# Shows all treks assigned to the logged-in staff member
def my_treks():
    staff = get_current_staff()
    if not staff:
        flash("Staff not found.", "danger")
        return redirect(url_for("authentication.login"))

    assigned_treks = (
        TrekModel.query.filter_by(assigned_staff_id=staff.id)
        .order_by(TrekModel.id.desc())
        .all()
    )
    load_trek_stats(assigned_treks)

    return render_template(
        "trekStaff/my_treks.html",
        staff=staff,
        assigned_treks=assigned_treks,
    )


# View or update one assigned trek (slots, status, participants)
def manage_trek(trek_id):
    staff = get_current_staff()
    if not staff:
        flash("Staff not found.", "danger")
        return redirect(url_for("authentication.login"))

    trek = get_assigned_trek(staff, trek_id)
    if not trek:
        flash("Trek not found or not assigned to you.", "danger")
        return redirect(url_for("trekk_staff_routes.my_treks"))

    load_trek_stats([trek])

    bookings = (
        BookingModel.query.filter_by(trek_id=trek.id)
        .order_by(BookingModel.booking_date.desc())
        .all()
    )

    # total booked slots
    booked_count = len([b for b in trek.bookings if b.status == BookingStatus.BOOKED])
    
    if request.method == "POST":
        try:
            available_slots = request.form.get("available_slots")
            status = request.form.get("status")

            if available_slots is None or available_slots == "":
                flash("Available slots is required.", "danger")
                return redirect(url_for("trekk_staff_routes.manage_trek", trek_id=trek_id))

            available_slots = int(available_slots)

            if available_slots < 0:
                flash("Available slots cannot be negative.", "danger")
                return redirect(url_for("trekk_staff_routes.manage_trek", trek_id=trek_id))

            max_available = trek.total_slots - booked_count
            if available_slots > max_available:
                flash(
                    f"This trek has {trek.total_slots} total slots. "
                    f"This trek already has {booked_count} booking(s). "
                    f"You can keep at most {max_available} slot(s) open.",
                    "danger",
                )
                return redirect(url_for("trekk_staff_routes.manage_trek", trek_id=trek_id))

            trek.available_slots = available_slots

            if trek.status in [TrekStatus.STARTED, TrekStatus.COMPLETED]:
                db.session.commit()
                flash("Available slots updated successfully.", "success")
                return redirect(url_for("trekk_staff_routes.manage_trek", trek_id=trek_id))

            if status not in [TrekStatus.OPEN.value, TrekStatus.CLOSED.value]:
                flash("Booking status can only be Open or Closed.", "danger")
                return redirect(url_for("trekk_staff_routes.manage_trek", trek_id=trek_id))

            trek.status = TrekStatus(status)
            db.session.commit()

            flash("Trek updated successfully.", "success")
            return redirect(url_for("trekk_staff_routes.manage_trek", trek_id=trek_id))

        except Exception:
            db.session.rollback()
            flash("An error occurred while updating the trek.", "danger")
            return redirect(url_for("trekk_staff_routes.manage_trek", trek_id=trek_id))

    return render_template(
        "trekStaff/manage_trek.html",
        staff=staff,
        trek=trek,
        bookings=bookings,
    )


# Marks an assigned trek as started (status = STARTED)
def mark_trek_started(trek_id):
    staff = get_current_staff()
    if not staff:
        flash("Staff not found.", "danger")
        return redirect(url_for("authentication.login"))

    trek = get_assigned_trek(staff, trek_id)
    if not trek:
        flash("Trek not found or not assigned to you.", "danger")
        return redirect(url_for("trekk_staff_routes.my_treks"))

    if trek.status == TrekStatus.COMPLETED:
        flash("This trek is already completed.", "danger")
        return redirect(url_for("trekk_staff_routes.manage_trek", trek_id=trek_id))

    if trek.status == TrekStatus.STARTED:
        flash("This trek is already started.", "info")
        return redirect(url_for("trekk_staff_routes.manage_trek", trek_id=trek_id))

    trek.status = TrekStatus.STARTED
    db.session.commit()
    flash("Trek marked as started.", "success")
    return redirect(url_for("trekk_staff_routes.manage_trek", trek_id=trek_id))


# Marks an assigned trek as completed (status = COMPLETED)
def mark_trek_completed(trek_id):
    staff = get_current_staff()
    if not staff:
        flash("Staff not found.", "danger")
        return redirect(url_for("authentication.login"))

    trek = get_assigned_trek(staff, trek_id)
    if not trek:
        flash("Trek not found or not assigned to you.", "danger")
        return redirect(url_for("trekk_staff_routes.my_treks"))

    if trek.status == TrekStatus.COMPLETED:
        flash("This trek is already completed.", "info")
        return redirect(url_for("trekk_staff_routes.manage_trek", trek_id=trek_id))

    if trek.status != TrekStatus.STARTED:
        flash("Please mark the trek as started before completing it.", "danger")
        return redirect(url_for("trekk_staff_routes.manage_trek", trek_id=trek_id))

    trek.status = TrekStatus.COMPLETED
    db.session.commit()
    flash("Trek marked as completed.", "success")
    return redirect(url_for("trekk_staff_routes.manage_trek", trek_id=trek_id))


# Shows registered trekkers grouped by each assigned trek (all statuses)
def participants():
    staff = get_current_staff()
    if not staff:
        flash("Staff not found.", "danger")
        return redirect(url_for("authentication.login"))

    assigned_treks = (
        TrekModel.query.filter_by(assigned_staff_id=staff.id)
        .order_by(TrekModel.id.desc())
        .all()
    )
    load_trek_stats(assigned_treks)

    trek_participants = []
    for trek in assigned_treks:
        bookings = (
            BookingModel.query.filter_by(trek_id=trek.id)
            .order_by(BookingModel.booking_date.desc())
            .all()
        )
        trek_participants.append({"trek": trek, "bookings": bookings})

    return render_template(
        "trekStaff/participants.html",
        staff=staff,
        trek_participants=trek_participants,
    )


# Toggles booking payment status between PAID and PENDING
def toggle_payment(booking_id):
    staff = get_current_staff()
    if not staff:
        flash("Staff not found.", "danger")
        return redirect(url_for("authentication.login"))

    booking = BookingModel.query.get(booking_id)
    if not booking:
        flash("Booking not found.", "danger")
        return redirect(url_for("trekk_staff_routes.participants"))

    trek = get_assigned_trek(staff, booking.trek_id)
    if not trek:
        flash("You can only manage bookings for your assigned treks.", "danger")
        return redirect(url_for("trekk_staff_routes.participants"))

    if booking.payment_status == PaymentStatus.PAID:
        booking.payment_status = PaymentStatus.PENDING
        flash("Payment status set to Pending.", "info")
    else:
        booking.payment_status = PaymentStatus.PAID
        flash("Payment status set to Paid.", "success")

    db.session.commit()

    next_page = request.form.get("next", "")
    if next_page == "manage_trek":
        return redirect(url_for("trekk_staff_routes.manage_trek", trek_id=trek.id))

    return redirect(url_for("trekk_staff_routes.participants"))


# Shows logged-in staff user and profile details
def staff_profile():
    staff = get_current_staff()
    if not staff:
        flash("Staff not found.", "danger")
        return redirect(url_for("authentication.login"))

    user = staff.user
    assigned_treks_count = TrekModel.query.filter_by(
        assigned_staff_id=staff.id
    ).count()

    return render_template(
        "trekStaff/staff_profile.html",
        user=user,
        staff=staff,
        assigned_treks_count=assigned_treks_count,
    )
