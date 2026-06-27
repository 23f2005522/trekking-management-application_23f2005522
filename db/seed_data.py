from db.db import db
from model.model import *
from datetime import datetime, timedelta, timezone


def seed_Admin():
    # check if admin exists in the DB
    try:
        admin = UserModel.query.filter_by(role=UserRole.ADMIN).first()
        
        if admin:
            print("Super admin ✔️  already exists")
            return
        
        if not admin:
            # create admin user
            admin = UserModel(
                username = "SUPER_ADMIN" , 
                email ="admin@tma.com" ,
                phone = "1001001001", 
                role = UserRole.ADMIN,
            )
            
            admin.set_password("admin")  
            db.session.add(admin)
            db.session.commit()

            print("Super admin created successfully")

    except Exception as e:
        print("Error occurred while seeding super admin:", str(e))
        db.session.rollback()
        return None

def seed_trekker(): 
    
    try : 
        dummy_trekker = UserModel.query.filter_by(email="dummy@tma.com").first()
        
        if dummy_trekker:
            print("Dummy trekker ✔️  already exists")
            return
        
        new_dummy_trekker = UserModel(
            username = "DUMMY_TREKKER" , 
            email ="dummy@tma.com",
            phone = "2002002002",
            role = UserRole.TREKKER,
            
        )
        new_dummy_trekker.set_password("trekker")
        db.session.add(new_dummy_trekker)
        db.session.commit()
        
        print("Dummy trekker created successfully")
        
        return new_dummy_trekker
    except Exception as e:
        print("Error occurred while seeding dummy trekker:", str(e))
        db.session.rollback()
        return None


def seed_trek():
    
    try : 
        trek = TrekModel.query.filter_by(name="Dummy Mountain Trek").first()
        
        if trek:
            print("Dummy trek ✔️  already exists")
            return
        
        new_trek = TrekModel(
            name = "Dummy Mountain Trek" ,
            description = "This is a dummy trek for testing purposes. It is a 5 days trek to the Dummy Mountain. The trek is suitable for beginners and experienced trekkers alike. The trek offers beautiful views of the surrounding mountains and valleys. The trek is also a great opportunity to learn about the local culture and traditions.",
            location = "Himalayas, India",
            difficulty = TrekDifficulty.MODERATE,
            duration = 5, #in days
            total_slots = 20,
            available_slots = 20,
            price = 6500.00,
            starting_at = datetime.now(timezone.utc), 
            ending_at = datetime.now(timezone.utc) + timedelta(days=5) , 
            status = TrekStatus.PENDING
            
        )
        
        db.session.add(new_trek)
        db.session.commit()
        
        print("Dummy trek created successfully")
        
        return new_trek
    
    except Exception as e:
        print("Error occurred while seeding dummy trek:", str(e))
        db.session.rollback()
        return None

def seed_dummy_trek_staff() : 
    try : 
        staff = UserModel.query.filter_by(email="dummy_staff@tma.com").first()
        
        if staff:
            print("Dummy trek staff ✔️  already exists")
            return
        
        # create dummy trek user with role as STAFF and then add the user id in to the StaffModel table
       
        new_dummy_staff = UserModel(
            username = "DUMMY_TREK_STAFF" , 
            email ="dummy_staff@tma.com",
            phone = "3003003003",
            role = UserRole.STAFF,
            
        )
        new_dummy_staff.set_password("staff")
        db.session.add(new_dummy_staff)
        db.session.commit()
        
        # add the userid in to the StaffModel table
        new_staff = StaffModel(
            user_id = new_dummy_staff.id,
            joining_date = datetime.now(timezone.utc),
            experience = 2, # in years
            address = "123 Dummy Street, Dummy City, Dummy Country",
            contact_number = "3003003003",
            staff_bio = "I am a dummy trek staff for testing purposes. I have 2 years of experience in guiding treks and ensuring the safety of trekkers. I am passionate about trekking and love to share my knowledge and experience with others.",
            Profile_status = StaffStatus.PENDING
        )
        db.session.add(new_staff)
        db.session.commit()
        
        print("Dummy trek staff created successfully")
        
        return new_dummy_staff
    except Exception as e:
        print("Error occurred while seeding dummy trek staff:", str(e))
        db.session.rollback()
        return None

def seed_dummy_booking():

    try : 
        user = UserModel.query.filter_by(
            email="dummy@tma.com"
        ).first()
        
        trek = TrekModel.query.filter_by(
            name="Dummy Mountain Trek",
            location="Himalayas, India"
        ).first()

        if not user or not trek:
            print("User or Trek does not exist")
            return

        booking = BookingModel.query.filter_by(
            user_id=user.id,
            trek_id=trek.id
        ).first()

        if booking:
            print("Booking ✔️  already exists")
            return

        booking = BookingModel(
            user_id=user.id,
            trek_id=trek.id,
            status=BookingStatus.BOOKED,
            payment_status=PaymentStatus.PAID,
            amount_paid=trek.price
        )

        db.session.add(booking)
        db.session.commit()

        print("Dummy booking created")
    
    except Exception as e:
        print("Error occurred while seeding dummy booking:", str(e))
        db.session.rollback()
        return None

def master_seed():
    seed_Admin()
    seed_trekker()
    seed_dummy_trek_staff()
    seed_trek()
    seed_dummy_booking()
    print("Seeding completed successfully")




