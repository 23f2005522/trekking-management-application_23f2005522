from flask import render_template, redirect, session, flash, request
from datetime import datetime
from model.model import *


def get_current_trekker():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return UserModel.query.filter_by(id=user_id, role=UserRole.TREKKER).first()


def get_booking_stats(bookings):
    active_bookings = 0
    completed_bookings = 0
    canceled_bookings = 0

    for booking in bookings:
        if booking.status == BookingStatus.BOOKED:
            active_bookings += 1
        elif booking.status == BookingStatus.COMPLETED:
            completed_bookings += 1
        elif booking.status == BookingStatus.CANCELED:
            canceled_bookings += 1

    return {
        "total_bookings": len(bookings),
        "active_bookings": active_bookings,
        "completed_bookings": completed_bookings,
        "canceled_bookings": canceled_bookings,
    }


def dashboard():
    user = get_current_trekker()
    if not user:
        flash("Trekker not found.", "danger")
        return redirect("/auth/login")

    bookings = BookingModel.query.filter_by(user_id=user.id).all()
    stats = get_booking_stats(bookings)

    recent_bookings = sorted(
        bookings,
        key=lambda booking: booking.booking_date,
        reverse=True,
    )[:5]

    recent_open_treks = (
        TrekModel.query.filter_by(status=TrekStatus.OPEN)
        .order_by(TrekModel.created_at.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "trekker/dashboard.html",
        user=user,
        stats=stats,
        recent_bookings=recent_bookings,
        recent_open_treks=recent_open_treks,
    )


def browse_treks():
    user = get_current_trekker()
    if not user:
        flash("Trekker not found.", "danger")
        return redirect("/auth/login")

    query = TrekModel.query.filter_by(status=TrekStatus.OPEN) # first select all open treks

    difficulty = request.args.get("difficulty", "")
    location = request.args.get("location", "")
    duration = request.args.get("duration", "")
    search = request.args.get("search", "")


    # then based on the difficulty, location, duration, and search, filter the treks
    if difficulty:
        query = query.filter(TrekModel.difficulty == TrekDifficulty(difficulty))

    if location:
        query = query.filter(TrekModel.location == location)

    if duration:
        query = query.filter(TrekModel.duration == int(duration))

    if search:
        query = query.filter(TrekModel.name.contains(search))

    treks = query.order_by(TrekModel.created_at.desc()).all()

    open_treks = TrekModel.query.filter_by(status=TrekStatus.OPEN).all() # all open treks
    locations = sorted({trek.location for trek in open_treks}) # location of the open treks 
    durations = sorted({trek.duration for trek in open_treks}) # duration of the open trek

    return render_template(
        "trekker/treks.html",
        user=user,
        treks=treks,
        locations=locations,
        durations=durations,
        # previous selected difficulty, location, duration, and search
        selected_difficulty=difficulty,
        selected_location=location,
        selected_duration=duration,
        search=search,
    )


def book_trek():
    user = get_current_trekker()
    if not user:
        flash("Trekker not found.", "danger")
        return redirect("/auth/login")

    trek_id = request.form.get("trek_id")
    if not trek_id:
        flash("Trek ID is required.", "danger")
        return redirect("/trekker/treks")

    trek = TrekModel.query.get(trek_id)
    if not trek:
        flash("Trek not found.", "danger")
        return redirect("/trekker/treks")

    if trek.status != TrekStatus.OPEN:
        flash("Trek is not open for booking.", "danger")
        return redirect("/trekker/treks")

    if trek.available_slots <= 0:
        flash("No available slots for this trek.", "danger")
        return redirect("/trekker/treks")

    existing_booking = BookingModel.query.filter_by(
        user_id=user.id,
        trek_id=trek.id,
    ).first()

    if existing_booking:
        if existing_booking.status == BookingStatus.CANCELED:
            existing_booking.status = BookingStatus.BOOKED
            existing_booking.booking_date = datetime.utcnow()
            existing_booking.payment_status = PaymentStatus.PENDING
            existing_booking.amount_paid = 0.0

            trek.available_slots -= 1
            db.session.commit()

            flash("Trek booked successfully.", "success")
            return redirect("/trekker/treks")

        flash("You have already booked this trek.", "danger")
        return redirect("/trekker/treks")

    new_booking = BookingModel(
        user_id=user.id,
        trek_id=trek.id,
        booking_date=datetime.utcnow(),
        status=BookingStatus.BOOKED,
        payment_status=PaymentStatus.PENDING,
        amount_paid=0.0,
    )

    try:
        db.session.add(new_booking)
        trek.available_slots -= 1
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash("An error occurred while booking the trek.", "danger")
        return redirect("/trekker/treks")

    flash("Trek booked successfully.", "success")
    return redirect("/trekker/treks")


def my_bookings():
    user = get_current_trekker()
    if not user:
        flash("Trekker not found.", "danger")
        return redirect("/auth/login")

    bookings = (
        BookingModel.query.filter_by(user_id=user.id)
        .order_by(BookingModel.booking_date.desc())
        .all()
    )

    return render_template(
        "trekker/bookings.html",
        user=user,
        bookings=bookings,
    )


def cancel_booking(booking_id):
    user = get_current_trekker()
    if not user:
        flash("Trekker not found.", "danger")
        return redirect("/auth/login")

    booking = BookingModel.query.get(booking_id)
    if not booking:
        flash("Booking not found.", "danger")
        return redirect("/trekker/bookings")

    if booking.user_id != user.id:
        flash("You are not authorized to cancel this booking.", "danger")
        return redirect("/trekker/bookings")

    if booking.status != BookingStatus.BOOKED:
        flash("Only booked treks can be canceled.", "danger")
        return redirect("/trekker/bookings")

    try:
        booking.status = BookingStatus.CANCELED
        booking.payment_status = PaymentStatus.FAILED
        booking.trek.available_slots += 1
        booking.booking_cancel_date = datetime.utcnow()
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash("An error occurred while canceling the booking.", "danger")
        return redirect("/trekker/bookings")

    flash("Booking canceled successfully.", "success")
    return redirect("/trekker/bookings")


def trekking_history():
    user = get_current_trekker()
    if not user:
        flash("Trekker not found.", "danger")
        return redirect("/auth/login")

    bookings = (
        BookingModel.query.filter_by(user_id=user.id)
        .order_by(BookingModel.booking_date.desc())
        .all()
    )

    return render_template(
        "trekker/history.html",
        user=user,
        bookings=bookings,
    )


def trekker_profile():
    user = get_current_trekker()
    if not user:
        flash("Trekker not found.", "danger")
        return redirect("/auth/login")

    if request.method == "GET":
        return render_template(
            "trekker/profile.html",
            user=user,
        )

    username = request.form.get("username", user.username)
    email = request.form.get("email", user.email)
    phone = request.form.get("phone", user.phone)

    username = username.strip() if isinstance(username, str) else user.username
    email = email.strip() if isinstance(email, str) else user.email
    phone = phone.strip() if isinstance(phone, str) else user.phone

    if not username or not email or not phone:
        flash("Username, email, and phone are required.", "danger")
        return redirect("/trekker/profile")

    email_exists = UserModel.query.filter(
        UserModel.email == email,
        UserModel.id != user.id,
    ).first()

    if email_exists:
        flash("Email is already used by another user.", "danger")
        return redirect("/trekker/profile")

    phone_exists = UserModel.query.filter(
        UserModel.phone == phone,
        UserModel.id != user.id,
    ).first()

    if phone_exists:
        flash("Phone is already used by another user.", "danger")
        return redirect("/trekker/profile")

    try:
        user.username = username
        user.email = email
        user.phone = phone
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash("An error occurred while updating profile.", "danger")
        return redirect("/trekker/profile")

    flash("Trekker profile updated successfully.", "success")
    return redirect("/trekker/profile")
