from db.db import db  # creating model using DB object instance from  db.py
from datetime import datetime
from enum import Enum
from werkzeug.security import generate_password_hash, check_password_hash

# Enums


# userRoles
class UserRole(str, Enum):
    ADMIN = "admin"
    TREKKER = "trekker"
    STAFF = "staff"


# trekdifficulty
class TrekDifficulty(str, Enum):
    EASY = "easy"
    MODERATE = "moderate"
    DIFFICULT = "difficult"


# trekstatus
class TrekStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    OPEN = "open"
    CLOSED = "closed"
    COMPLETED = "completed"


# BookingStatus
class BookingStatus(str, Enum):
    BOOKED = "booked"
    COMPLETED = "comepleted"
    CANCELED = "canceled"


# PaymentStatus
class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    PAID = "paid"


# StaffStatus
class StaffStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLACKLISTED = "blacklisted"


# Mixins {using Multiple Inheritance to create common fields for all models}
class TimeStampMixin(db.Model):
    __abstract__ = True
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


# BaseModel
class BaseModel(TimeStampMixin, db.Model):
    __abstract__ = True  ## means this class is not a table in the database, but it can be inherited by other models to have common fields [new concept of abstract base class in SQLAlchemy]
    id = db.Column(db.Integer, primary_key=True)


# Models
class UserModel(BaseModel):  ## trekkers [by default] , staff [call StaffModel] , admin [programitically created]

    __tablename__ = "users"

    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.TREKKER, nullable=False)
    """
    # db.Enum is used to store the enum values in the database as strings, and it will automatically handle the conversion between the enum and the string representation in the database.
    # raw syntax : db.Enum("admin" , "user" , "staff" , name = "user_roles")  # this is the raw syntax to create enum in SQLAlchemy, but we are using python enum class to create enum and then using it in the model.
    """

    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_blacklisted = db.Column(db.Boolean, default=False, nullable=False)
    blacklisted_reason = db.Column(db.String(500), nullable=True)

    bookings = db.relationship(
        "BookingModel",  ## here we specify the python model name not the table name
        backref=db.backref("user", lazy=True), # gives booking132.user to access the user who made the booking
        foreign_keys="BookingModel.user_id",  # which foreign key should be used
        lazy=True,
        cascade="all, delete-orphan",  # if a user is deleted, all their bookings will be deleted as well
    )

    staff = db.relationship(
        "StaffModel",
        backref=db.backref("user", uselist=False),
        uselist=False,
        cascade="all, delete-orphan",
    )

    reviews = db.relationship(
        "TrekReviewModel",
        backref=db.backref("user", lazy=True),
        foreign_keys="TrekReviewModel.user_id",
        lazy=True,
        cascade="all, delete-orphan",
    )
    ###

    # methods to check user roles
    def is_admin(self):
        return self.role == UserRole.ADMIN

    def is_staff(self):
        return self.role == UserRole.STAFF

    def is_trekker(self):
        return self.role == UserRole.TREKKER

    # methods to set and check password
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Staff Model
class StaffModel(BaseModel):
    __tablename__ = "staffs"

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True
    )
    
    # user relationship is now automatically handled by UserModel's staff backref

    joining_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    experience = db.Column(db.Integer, nullable=False, default=0)  # in years
    address = db.Column(db.String(200), nullable=True, default="Add your address now")
    contact_number = db.Column(
        db.String(15), nullable=True, default="Add your contact number now"
    )
    status = db.Column(db.Enum(StaffStatus), default=StaffStatus.ACTIVE, nullable=False)
    bio = db.Column(db.String(500), nullable=True, default="Add your bio now")
    Profile_verification_status = db.Column(db.Boolean, default=False, nullable=False)

    treks = db.relationship(
        "TrekModel",
        backref=db.backref("staff", lazy=True),
        foreign_keys="TrekModel.assigned_staff_id",
        lazy=True,
    )  # one to many relationship with TrekModel


# Trek Model
class TrekModel(BaseModel):
    __tablename__ = "treks"

    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.Enum(TrekDifficulty), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in days
    total_slots = db.Column(db.Integer, nullable=False, default=10)
    available_slots = db.Column(db.Integer, nullable=False, default=10)

    price = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String(600), nullable=True)
    image_url = db.Column(db.String(200), nullable=True)
    starting_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ending_at = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum(TrekStatus), default=TrekStatus.PENDING, nullable=False)

    # relationship with user model (staff) [one] to [many] Trek Model
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey("staffs.id"), nullable=True)
    
    # staff relationship is now automatically handled by StaffModel's treks backref
    
    bookings = db.relationship(
        "BookingModel", backref=db.backref("trek", lazy=True), lazy=True, cascade="all, delete-orphan"
    )  # one to many relationship with BookingModel
    reviews = db.relationship(
        "TrekReviewModel", backref=db.backref("trek", lazy=True), lazy=True, cascade="all, delete-orphan"
    )  # one to many relationship with ReviewModel

    __table_args__ = (
        db.CheckConstraint(
            "available_slots <= total_slots", name="check_available_slots"
        ),
        db.CheckConstraint("starting_at < ending_at", name="ending before start constraint"),
        db.CheckConstraint("price >= 0", name="zero_price_constraint"),
    )

    # computed property to calculate available slots
    @property  # @property decorator is used to define a method as a property, so that it can be accessed like an attribute.
    def calculate_available_slots(self):
        already_blooked = [b for b in self.bookings if b.status == BookingStatus.BOOKED]
        booked_slots = len(already_blooked)
        return self.total_slots - booked_slots


# Booking Model
class BookingModel(BaseModel):
    __tablename__ = "bookings"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey("treks.id"), nullable=False)

    booking_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(
        db.Enum(BookingStatus), default=BookingStatus.BOOKED, nullable=False
    )
    payment_status = db.Column(
        db.Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False
    )

    amount_paid = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    booking_cancel_date = db.Column(db.DateTime, nullable=True)
    booking_cancel_reason = db.Column(db.String(500), nullable=True)

    # relationships (automatically generated via backrefs on UserModel and TrekModel)

    # constraints to ensure data integrity
    __table_args__ = (
        db.UniqueConstraint(
            "user_id", "trek_id", name="unique_user_trek_booking"
        ),  ## only one user can book a trek at a time
    )


# Review Model
class TrekReviewModel(BaseModel):

    __tablename__ = "reviews"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey("treks.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=5)
    comment = db.Column(db.String(500), nullable=True)

    # relationships (automatically generated via backrefs on UserModel and TrekModel)