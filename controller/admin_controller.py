from flask import request, render_template, redirect, flash, session
from sqlalchemy import func
from datetime import datetime
from model.model import *


def get_approved_staff_users():
    approved_staff_profiles = StaffModel.query.filter_by(
        Profile_status=StaffStatus.APPROVED
    ).all()
    return [staff.user for staff in approved_staff_profiles if staff.user]


def validate_assignable_staff(assigned_staff_id):
    if not assigned_staff_id:
        return None, "Assigned staff ID is required."

    staff_member = StaffModel.query.filter_by(id=int(assigned_staff_id)).first()
    if not staff_member:
        return None, "The assigned staff member does not exist."

    if staff_member.Profile_status == StaffStatus.PENDING:
        return None, "Cannot assign staff with pending approval."

    if staff_member.Profile_status == StaffStatus.BLACKLISTED:
        return None, "Cannot assign a blacklisted staff member."

    if staff_member.Profile_status == StaffStatus.REJECTED:
        return None, "Cannot assign a rejected staff member."

    if staff_member.Profile_status != StaffStatus.APPROVED:
        return None, "Only approved staff members can be assigned to a trek."

    if staff_member.user and staff_member.user.is_blacklisted:
        return None, "Cannot assign a blacklisted staff member."

    return staff_member, None


def search_all(query):
    query = query.strip()
    if not query:
        return {"trekkers": [], "staff": [], "treks": []}

    like = f"%{query}%" # if query is a string

    trekkers = UserModel.query.filter(
        UserModel.role == UserRole.TREKKER,
        UserModel.username.ilike(like),
    ).all()

    staff = (
        StaffModel.query.join(UserModel)
        .filter(
            UserModel.role == UserRole.STAFF,
            UserModel.username.ilike(like),
        )
        .all()
    )

    treks = TrekModel.query.filter(TrekModel.name.ilike(like)).all()

    if query.isdigit(): # if query is a number
        num = int(query)

        trekker = UserModel.query.filter_by(id=num, role=UserRole.TREKKER).first()
        if trekker and trekker not in trekkers:
            trekkers.append(trekker)

        staff_member = StaffModel.query.filter_by(id=num).first()
        if staff_member and staff_member not in staff:
            staff.append(staff_member)

        trek = TrekModel.query.filter_by(id=num).first()
        if trek and trek not in treks:
            treks.append(trek)

    return {"trekkers": trekkers, "staff": staff, "treks": treks}


def form_data_from_trek(trek_obj):
    return {
        "name": trek_obj.name,
        "location": trek_obj.location,
        "difficulty": trek_obj.difficulty.value,
        "duration": trek_obj.duration,
        "total_slots": trek_obj.total_slots,
        "price": float(trek_obj.price),
        "starting_at": trek_obj.starting_at.strftime("%Y-%m-%dT%H:%M"),
        "ending_at": trek_obj.ending_at.strftime("%Y-%m-%dT%H:%M"),
        "assigned_staff_id": trek_obj.assigned_staff_id,
        "status": trek_obj.status.value,
        "image_url": trek_obj.image_url or "",
        "description": trek_obj.description or "",
    }


def form_data_from_request():
    return {
        "name": request.form.get("name", ""),
        "location": request.form.get("location", ""),
        "difficulty": request.form.get("difficulty", ""),
        "duration": request.form.get("duration", ""),
        "total_slots": request.form.get("total_slots", ""),
        "price": request.form.get("price", ""),
        "starting_at": request.form.get("starting_at", ""),
        "ending_at": request.form.get("ending_at", ""),
        "assigned_staff_id": request.form.get("assigned_staff_id", ""),
        "status": request.form.get("status", ""),
        "image_url": request.form.get("image_url", ""),
        "description": request.form.get("description", ""),
    }


def dashboard():
    admin_user = UserModel.query.filter_by(id=session["user_id"]).first()

    total_trekkers = UserModel.query.filter_by(role=UserRole.TREKKER).count()
    total_staff = UserModel.query.filter_by(role=UserRole.STAFF).count()
    total_bookings = BookingModel.query.count()
    total_treks = TrekModel.query.count()

    fresh_bookings = (
        BookingModel.query.order_by(BookingModel.booking_date.desc()).limit(3).all()
    )

    total_revenue_till_data = (
        db.session.query(func.sum(BookingModel.amount_paid)).scalar() or 0
    )

    treks_approved = TrekModel.query.filter(
        TrekModel.status == TrekStatus.APPROVED
    ).count()

    total_treks_pending = TrekModel.query.filter(
        TrekModel.status == TrekStatus.PENDING
    ).count()

    return render_template(
        "admin/dashboard.html",
        admin_user=admin_user,
        total_trekkers=total_trekkers,
        total_staff=total_staff,
        total_bookings=total_bookings,
        total_treks=total_treks,
        fresh_bookings=fresh_bookings,
        total_revenue_till_data=total_revenue_till_data,
        treks_approved=treks_approved,
        treks_pending=total_treks_pending,
    )


def manage_staff():
    staff_members = UserModel.query.filter_by(role=UserRole.STAFF).all()

    pending_staff_members = [
        staff
        for staff in staff_members
        if staff.staff_profile.Profile_status == StaffStatus.PENDING
    ]

    approved_staff_members = [
        staff
        for staff in staff_members
        if staff.staff_profile.Profile_status == StaffStatus.APPROVED
    ]

    blacklisted_staff_members = [
        staff
        for staff in staff_members
        if staff.staff_profile.Profile_status == StaffStatus.BLACKLISTED
    ]

    return render_template(
        "admin/manage_staff.html",
        staff_members=staff_members,
        pending_staff_members=pending_staff_members,
        approved_staff_members=approved_staff_members,
        blacklisted_staff_members=blacklisted_staff_members,
    )


def create_staff():
    try:
        username = request.form.get("username")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        address = request.form.get("address")
        staff_bio = request.form.get("staff_bio")
        experience = request.form.get("experience", 0)

        if (
            not username
            or not email
            or not phone
            or not password
            or not confirm_password
        ):
            flash("Please provide all required fields.", "danger")
            return redirect("/admin/manage_staff")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect("/admin/manage_staff")

        if UserModel.query.filter_by(email=email).first():
            flash("A user with this email already exists.", "danger")
            return redirect("/admin/manage_staff")

        if UserModel.query.filter_by(phone=phone).first():
            flash("A user with this phone number already exists.", "danger")
            return redirect("/admin/manage_staff")

        user = UserModel(
            username=username,
            email=email,
            phone=phone,
            role=UserRole.STAFF,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        staff_profile = StaffModel(
            user_id=user.id,
            experience=int(experience) if experience else 0,
            address=address or "Add your address now",
            contact_number=phone,
            staff_bio=staff_bio or "Add your bio now",
            Profile_status=StaffStatus.PENDING,
        )
        db.session.add(staff_profile)
        db.session.commit()

        flash("Staff created successfully. Approve the staff to allow login.", "success")
        return redirect("/admin/manage_staff")

    except Exception:
        db.session.rollback()
        flash("An error occurred while creating staff.", "danger")
        return redirect("/admin/manage_staff")


def approve_staff(user_id):
    staff = UserModel.query.get(user_id)

    if staff and staff.role == UserRole.STAFF:
        staff.is_active = True
        staff.is_blacklisted = False
        staff.blacklisted_reason = None
        staff.staff_profile.Profile_status = StaffStatus.APPROVED
        db.session.commit()
        flash("Staff approved successfully.", "success")
        return redirect("/admin/manage_staff")

    flash("Staff not found or not a staff member.", "danger")
    return redirect("/admin/manage_staff")


def reject_staff(user_id):
    staff = UserModel.query.get(user_id)
    if staff and staff.role == UserRole.STAFF:
        staff.is_active = False
        staff.staff_profile.Profile_status = StaffStatus.REJECTED
        db.session.commit()
        flash("Staff rejected successfully.", "success")
        return redirect("/admin/manage_staff")

    flash("Staff not found or not a staff member.", "danger")
    return redirect("/admin/manage_staff")


def blacklist_staff(user_id):
    staff = UserModel.query.get(user_id)
    blacklisted_reason = request.form.get("blacklisted_reason")

    if (
        staff
        and staff.role == UserRole.STAFF
        and staff.staff_profile.Profile_status == StaffStatus.APPROVED
    ):
        staff.is_active = False
        staff.is_blacklisted = True
        staff.blacklisted_reason = blacklisted_reason or "Blacklisted by admin"
        staff.staff_profile.Profile_status = StaffStatus.BLACKLISTED
        db.session.commit()
        flash("Staff blacklisted successfully.", "success")
        return redirect("/admin/manage_staff")

    flash("Staff not found or cannot be blacklisted.", "danger")
    return redirect("/admin/manage_staff")


def deblacklist_staff(user_id):
    staff = UserModel.query.get(user_id)

    if (
        staff
        and staff.role == UserRole.STAFF
        and staff.staff_profile.Profile_status == StaffStatus.BLACKLISTED
    ):
        staff.is_active = True
        staff.is_blacklisted = False
        staff.blacklisted_reason = None
        staff.staff_profile.Profile_status = StaffStatus.APPROVED
        db.session.commit()
        flash("Staff approved again successfully.", "success")
        return redirect("/admin/manage_staff")

    flash("Staff not found or not blacklisted.", "danger")
    return redirect("/admin/manage_staff")


def delete_staff_permanently(user_id):
    staff_user = UserModel.query.get(user_id)

    if not staff_user or staff_user.role != UserRole.STAFF:
        flash("Staff not found or not a staff member.", "danger")
        return redirect("/admin/manage_staff")

    if not staff_user.staff_profile:
        flash("Staff profile not found.", "danger")
        return redirect("/admin/manage_staff")

    if staff_user.staff_profile.Profile_status != StaffStatus.BLACKLISTED:
        flash("Only blacklisted staff can be permanently deleted.", "danger")
        return redirect("/admin/manage_staff")

    try:
        staff_profile_id = staff_user.staff_profile.id

        assigned_treks = TrekModel.query.filter_by(
            assigned_staff_id=staff_profile_id
        ).all()
        for trek in assigned_treks:
            trek.assigned_staff_id = None

        db.session.delete(staff_user)
        db.session.commit()

        flash("Trek staff permanently deleted from the system.", "success")
        return redirect("/admin/manage_staff")

    except Exception:
        db.session.rollback()
        flash("An error occurred while deleting the staff member.", "danger")
        return redirect("/admin/manage_staff")


def manage_treks():
    treks = TrekModel.query.all()
    approved_staffs = get_approved_staff_users()
    return render_template(
        "admin/manage_treks.html", treks=treks, staffs=approved_staffs
    )


def create_trek():
    try:
        name = request.form.get("name")
        location = request.form.get("location")
        difficulty = request.form.get("difficulty")
        duration = request.form.get("duration")
        total_slots = request.form.get("total_slots")
        price = request.form.get("price")
        image_url = request.form.get("image_url")
        description = request.form.get("description")
        starting_at_str = request.form.get("starting_at")
        ending_at_str = request.form.get("ending_at")
        assigned_staff_id = request.form.get("assigned_staff_id")
        status = request.form.get("status")

        if (
            not name
            or not location
            or not difficulty
            or not duration
            or not total_slots
            or not price
            or not starting_at_str
            or not ending_at_str
            or not assigned_staff_id
            or not status
        ):
            flash("Please provide all required fields.", "danger")
            return redirect("/admin/manage_treks")

        if assigned_staff_id == "" or assigned_staff_id is None:
            flash("Assigned staff ID is required.", "danger")
            return redirect("/admin/manage_treks")

        existing_trek = TrekModel.query.filter_by(name=name).first()
        if existing_trek:
            flash(
                "A trek with the same name already exists. Please wait for the previous trek to be completed before adding a new one.",
                "danger",
            )
            return redirect("/admin/manage_treks")

        staff_member, staff_error = validate_assignable_staff(assigned_staff_id)
        if staff_error:
            flash(staff_error, "danger")
            return redirect("/admin/manage_treks")

        starting_at = datetime.fromisoformat(starting_at_str)
        ending_at = datetime.fromisoformat(ending_at_str)

        if starting_at >= ending_at:
            flash("End date must be after start date.", "danger")
            return redirect("/admin/manage_treks")

        calculated_duration = (ending_at.date() - starting_at.date()).days
        if calculated_duration != int(duration):
            flash(
                "The provided duration does not match the difference between the start and end dates.",
                "danger",
            )
            return redirect("/admin/manage_treks")

        trek_status = (
            TrekStatus.APPROVED
            if status == TrekStatus.APPROVED.value
            else TrekStatus(status)
        )

        new_trek = TrekModel(
            name=name,
            location=location,
            difficulty=TrekDifficulty(difficulty),
            duration=int(duration),
            total_slots=int(total_slots),
            available_slots=int(total_slots),
            price=float(price),
            image_url=image_url or None,
            description=description or None,
            starting_at=starting_at,
            ending_at=ending_at,
            assigned_staff_id=int(assigned_staff_id),
            status=trek_status,
        )

        db.session.add(new_trek)
        db.session.commit()

        flash("Trek added successfully.", "success")
        return redirect("/admin/manage_treks")

    except Exception:
        db.session.rollback()
        flash("An error occurred while creating the trek.", "danger")
        return redirect("/admin/manage_treks")


def edit_trek(trek_id):
    approved_staffs = get_approved_staff_users()

    trek = TrekModel.query.get(trek_id)
    if not trek:
        flash("Trek not found.", "danger")
        return redirect("/admin/manage_treks")

    if request.method == "GET":
        return render_template(
            "admin/edit_trek.html",
            trek=trek,
            form_data=form_data_from_trek(trek),
            staffs=approved_staffs,
        )

    try:
        form_data = form_data_from_request()

        name = form_data["name"]
        location = form_data["location"]
        difficulty = form_data["difficulty"]
        duration = form_data["duration"]
        total_slots = form_data["total_slots"]
        price = form_data["price"]
        image_url = form_data["image_url"]
        description = form_data["description"]
        starting_at_str = form_data["starting_at"]
        ending_at_str = form_data["ending_at"]
        assigned_staff_id = form_data["assigned_staff_id"]
        status = form_data["status"]

        if (
            not name
            or not location
            or not difficulty
            or not duration
            or not total_slots
            or not price
            or not starting_at_str
            or not ending_at_str
            or not assigned_staff_id
            or not status
        ):
            flash("Please provide all required fields.", "danger")
            return render_template(
                "admin/edit_trek.html",
                trek=trek,
                form_data=form_data,
                staffs=approved_staffs,
            )

        if assigned_staff_id == "" or assigned_staff_id is None:
            flash("Assigned staff ID is required.", "danger")
            return render_template(
                "admin/edit_trek.html",
                trek=trek,
                form_data=form_data,
                staffs=approved_staffs,
            )

        existing_trek = TrekModel.query.filter_by(name=name).first()
        if existing_trek and existing_trek.id != trek_id:
            flash("A trek with the same name already exists.", "danger")
            return render_template(
                "admin/edit_trek.html",
                trek=trek,
                form_data=form_data,
                staffs=approved_staffs,
            )

        staff_member, staff_error = validate_assignable_staff(assigned_staff_id)
        if staff_error:
            flash(staff_error, "danger")
            return render_template(
                "admin/edit_trek.html",
                trek=trek,
                form_data=form_data,
                staffs=approved_staffs,
            )

        starting_at = datetime.fromisoformat(starting_at_str)
        ending_at = datetime.fromisoformat(ending_at_str)

        if starting_at >= ending_at:
            flash("End date must be after start date.", "danger")
            return render_template(
                "admin/edit_trek.html",
                trek=trek,
                form_data=form_data,
                staffs=approved_staffs,
            )

        calculated_duration = (ending_at.date() - starting_at.date()).days
        if calculated_duration != int(duration):
            flash(
                "The provided duration does not match the difference between the start and end dates.",
                "danger",
            )
            return render_template(
                "admin/edit_trek.html",
                trek=trek,
                form_data=form_data,
                staffs=approved_staffs,
            )

        booked_slots = trek.total_slots - trek.available_slots
        new_total_slots = int(total_slots)
        new_available_slots = new_total_slots - booked_slots

        if new_available_slots < 0:
            flash(
                "Total slots cannot be less than the number of already booked slots.",
                "danger",
            )
            return render_template(
                "admin/edit_trek.html",
                trek=trek,
                form_data=form_data,
                staffs=approved_staffs,
            )

        trek_status = (
            TrekStatus.APPROVED
            if status == TrekStatus.APPROVED.value
            else TrekStatus(status)
        )

        trek.name = name
        trek.location = location
        trek.difficulty = TrekDifficulty(difficulty)
        trek.duration = int(duration)
        trek.total_slots = new_total_slots
        trek.available_slots = new_available_slots
        trek.price = float(price)
        trek.image_url = image_url or None
        trek.description = description or None
        trek.starting_at = starting_at
        trek.ending_at = ending_at
        trek.assigned_staff_id = int(assigned_staff_id)
        trek.status = trek_status

        db.session.commit()

        flash("Trek updated successfully.", "success")
        return redirect("/admin/manage_treks")

    except Exception:
        db.session.rollback()
        flash("An error occurred while updating the trek.", "danger")
        return render_template(
            "admin/edit_trek.html",
            trek=trek,
            form_data=form_data_from_request(),
            staffs=approved_staffs,
        )


def delete_trek(trek_id):
    try:
        trek = TrekModel.query.get(trek_id)

        if not trek:
            flash("Trek not found.", "danger")
            return redirect("/admin/manage_treks")

        db.session.delete(trek)
        db.session.commit()

        flash("Trek deleted successfully.", "success")
        return redirect("/admin/manage_treks")

    except Exception:
        db.session.rollback()
        flash("An error occurred while deleting the trek.", "danger")
        return redirect("/admin/manage_treks")


def manage_trekkers():
    trekkers = UserModel.query.filter_by(role=UserRole.TREKKER).all()
    return render_template("admin/manage_trekkers.html", trekkers=trekkers)


def deactivate_trekker(user_id):
    trekker = UserModel.query.get(user_id)

    if not trekker or trekker.role != UserRole.TREKKER:
        flash("Trekker not found.", "danger")
        return redirect("/admin/manage_trekkers")

    if not trekker.is_active:
        flash("This trekker account is already inactive.", "info")
        return redirect("/admin/manage_trekkers")

    trekker.is_active = False
    db.session.commit()

    flash("Trekker deactivated successfully.", "success")
    return redirect("/admin/manage_trekkers")


def reactivate_trekker(user_id):
    trekker = UserModel.query.get(user_id)

    if not trekker or trekker.role != UserRole.TREKKER:
        flash("Trekker not found.", "danger")
        return redirect("/admin/manage_trekkers")

    if trekker.is_blacklisted:
        flash("This trekker is blacklisted. Remove blacklist first.", "danger")
        return redirect("/admin/manage_trekkers")

    if trekker.is_active:
        flash("This trekker account is already active.", "info")
        return redirect("/admin/manage_trekkers")

    trekker.is_active = True
    db.session.commit()

    flash("Trekker reactivated successfully.", "success")
    return redirect("/admin/manage_trekkers")


def blacklist_trekker(user_id):
    trekker = UserModel.query.get(user_id)
    blacklisted_reason = request.form.get("blacklisted_reason")

    if not trekker or trekker.role != UserRole.TREKKER:
        flash("Trekker not found.", "danger")
        return redirect("/admin/manage_trekkers")

    if trekker.is_blacklisted:
        flash("This trekker is already blacklisted.", "info")
        return redirect("/admin/manage_trekkers")

    if not trekker.is_active:
        flash("Only active trekkers can be blacklisted.", "danger")
        return redirect("/admin/manage_trekkers")

    trekker.is_active = False
    trekker.is_blacklisted = True
    trekker.blacklisted_reason = blacklisted_reason or "Blacklisted by admin"
    db.session.commit()

    flash("Trekker blacklisted successfully.", "success")
    return redirect("/admin/manage_trekkers")


def deblacklist_trekker(user_id):
    trekker = UserModel.query.get(user_id)

    if not trekker or trekker.role != UserRole.TREKKER:
        flash("Trekker not found.", "danger")
        return redirect("/admin/manage_trekkers")

    if not trekker.is_blacklisted:
        flash("This trekker is not blacklisted.", "danger")
        return redirect("/admin/manage_trekkers")

    trekker.is_active = True
    trekker.is_blacklisted = False
    trekker.blacklisted_reason = None
    db.session.commit()

    flash("Trekker removed from blacklist successfully.", "success")
    return redirect("/admin/manage_trekkers")


def manage_bookings():
    bookings = BookingModel.query.order_by(BookingModel.booking_date.desc()).all()
    return render_template("admin/bookings.html", bookings=bookings)


def search_page():
    query = request.args.get("q", "").strip()
    trekkers = []
    staff = []
    treks = []

    if query:
        results = search_all(query)
        trekkers = results["trekkers"]
        staff = results["staff"]
        treks = results["treks"]

    return render_template(
        "admin/search.html",
        query=query,
        trekkers=trekkers,
        staff=staff,
        treks=treks,
    )


def generate_report():
    overview = {
        "total_trekkers": UserModel.query.filter_by(role=UserRole.TREKKER).count(),
        "total_staff": UserModel.query.filter_by(role=UserRole.STAFF).count(),
        "total_treks": TrekModel.query.count(),
        "total_bookings": BookingModel.query.count(),
    }

    trek_status = {
        "open": TrekModel.query.filter_by(status=TrekStatus.OPEN).count(),
        "closed": TrekModel.query.filter_by(status=TrekStatus.CLOSED).count(),
        "started": TrekModel.query.filter_by(status=TrekStatus.STARTED).count(),
        "completed": TrekModel.query.filter_by(status=TrekStatus.COMPLETED).count(),
        "pending": TrekModel.query.filter_by(status=TrekStatus.PENDING).count(),
        "approved": TrekModel.query.filter_by(status=TrekStatus.APPROVED).count(),
    }

    booking_status = {
        "booked": BookingModel.query.filter_by(status=BookingStatus.BOOKED).count(),
        "completed": BookingModel.query.filter_by(status=BookingStatus.COMPLETED).count(),
        "canceled": BookingModel.query.filter_by(status=BookingStatus.CANCELED).count(),
    }

    payment_statistics = {
        "paid": BookingModel.query.filter_by(payment_status=PaymentStatus.PAID).count(),
        "pending": BookingModel.query.filter_by(
            payment_status=PaymentStatus.PENDING
        ).count(),
        "revenue": db.session.query(func.sum(BookingModel.amount_paid)).scalar() or 0,
    }

    popular_treks_raw = (
        db.session.query(
            TrekModel.name,
            func.count(BookingModel.id).label("booking_count"),
        )
        .join(BookingModel, BookingModel.trek_id == TrekModel.id)
        .group_by(TrekModel.id)
        .order_by(func.count(BookingModel.id).desc())
        .limit(5)
        .all()
    )

    popular_treks = [
        {"trek_name": trek.name, "booking_count": trek.booking_count}
        for trek in popular_treks_raw
    ]

    return render_template(
        "admin/reports.html",
        overview=overview,
        trek_status=trek_status,
        booking_status=booking_status,
        payment_statistics=payment_statistics,
        popular_treks=popular_treks,
    )
