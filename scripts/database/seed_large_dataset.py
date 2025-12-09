#!/usr/bin/env python3
"""
Large Dataset Seeding Script
Seeds 10,000+ users, flights, hotels, cars and 100,000+ bookings/billings
For performance testing and project requirements.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import logging
from datetime import datetime, timedelta
from decimal import Decimal
import random
import string
from typing import List
from sqlalchemy import func

# Database imports
from backend.common.database import SessionLocal
from backend.models.mysql_models import (
    User, Flight, Hotel, HotelRoom, Car, Booking, Billing,
    FlightClass, RoomType, CarType, TransmissionType, BookingType, PaymentStatus
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
CONFIG = {
    'users': 12000,
    'flights': 15000,
    'hotels': 2000,
    'hotel_rooms_per_hotel': 8,  # Will create 16,000 hotel rooms
    'cars': 10000,
    'bookings': 120000,
    'billings': 120000,  # One billing per booking
    'batch_size': 1000,  # Commit every N records
}

# Data sources
FIRST_NAMES = ['James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda', 
               'William', 'Barbara', 'David', 'Elizabeth', 'Richard', 'Susan', 'Joseph', 'Jessica']

LAST_NAMES = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
              'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson']

US_STATES = ['CA', 'NY', 'TX', 'FL', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI', 'NJ', 'VA', 'WA', 'AZ', 'MA']

US_CITIES = {
    'CA': ['Los Angeles', 'San Francisco', 'San Diego', 'San Jose', 'Sacramento'],
    'NY': ['New York', 'Buffalo', 'Rochester', 'Albany', 'Syracuse'],
    'TX': ['Houston', 'Dallas', 'Austin', 'San Antonio', 'Fort Worth'],
    'FL': ['Miami', 'Orlando', 'Tampa', 'Jacksonville', 'Fort Lauderdale'],
    'IL': ['Chicago', 'Aurora', 'Naperville', 'Joliet', 'Rockford'],
}

AIRLINES = {
    'AA': 'American Airlines',
    'UA': 'United Airlines',
    'DL': 'Delta Air Lines',
    'SW': 'Southwest Airlines',
    'JB': 'JetBlue Airways',
    'AS': 'Alaska Airlines',
    'NK': 'Spirit Airlines',
    'F9': 'Frontier Airlines',
    'B6': 'JetBlue',
    'WN': 'Southwest'
}

AIRPORTS = ['SFO', 'JFK', 'LAX', 'ORD', 'DFW', 'SEA', 'BOS', 'MIA', 'ATL', 'DEN', 'LAS', 'PHX']

HOTEL_CHAINS = ['Marriott', 'Hilton', 'Hyatt', 'Holiday Inn', 'Best Western', 'Sheraton', 
                'Westin', 'Four Seasons', 'Ritz Carlton', 'InterContinental']

CAR_PROVIDERS = ['Enterprise', 'Hertz', 'Avis', 'Budget', 'National', 'Alamo', 'Thrifty']

CAR_MAKES = ['Toyota', 'Honda', 'Ford', 'Chevrolet', 'Nissan', 'BMW', 'Mercedes-Benz', 'Audi']


def generate_user_id(index):
    """Generate user_id in SSN format."""
    return f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}"


def generate_email(first_name, last_name, index):
    """Generate unique email."""
    providers = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
    return f"{first_name.lower()}.{last_name.lower()}{index}@{random.choice(providers)}"


def generate_phone():
    """Generate US phone number."""
    return f"{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}"


def generate_profile_image_url(first_name: str, last_name: str) -> str:
    """Generate a profile picture URL using UI Avatars service."""
    # Use UI Avatars API to generate profile pictures
    # Options: different styles, colors, backgrounds
    styles = ['avataaars', 'personas', 'initials', 'lorelei', 'micah']
    style = random.choice(styles)
    
    # Generate random colors for variety
    colors = ['0D8ABC', '1abc9c', '2ecc71', '3498db', '9b59b6', 'e74c3c', 'f39c12', 'e67e22']
    background_colors = ['random', '0D8ABC', '1abc9c', '2ecc71', '3498db']
    
    name = f"{first_name}+{last_name}"
    color = random.choice(colors)
    bg_color = random.choice(background_colors)
    
    # UI Avatars API
    return f"https://ui-avatars.com/api/?name={name}&size=200&background={bg_color}&color=fff&bold=true&format=png"


def seed_users(db: SessionLocal, count: int):
    """Seed users in batches."""
    logger.info(f"Seeding {count} users...")
    
    existing_count = db.query(User).count()
    if existing_count >= count:
        logger.info(f"Already have {existing_count} users, skipping...")
        return
    
    users_to_create = count - existing_count
    created = 0
    
    for i in range(users_to_create):
        state = random.choice(US_STATES)
        city = random.choice(US_CITIES.get(state, ['City']))
        
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        
        # Generate profile picture URL
        profile_image_url = generate_profile_image_url(first_name, last_name)
        
        user = User(
            user_id=generate_user_id(existing_count + i),
            first_name=first_name,
            last_name=last_name,
            email=generate_email(first_name, last_name, existing_count + i),
            phone_number=generate_phone(),
            address=f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Maple', 'Pine'])} St",
            city=city,
            state=state,
            zip_code=f"{random.randint(10000, 99999)}",
            profile_image_url=profile_image_url,
            credit_card_last_four=f"{random.randint(1000, 9999)}",
            credit_card_type=random.choice(['Visa', 'Mastercard', 'Amex']),
            is_active=True,
            password_hash='$2b$12$placeholder_hash_for_seeding'
        )
        
        db.add(user)
        created += 1
        
        if created % CONFIG['batch_size'] == 0:
            db.commit()
            logger.info(f"  Created {created}/{users_to_create} users...")
    
    db.commit()
    logger.info(f"✅ Created {created} users (Total: {db.query(User).count()})")


def seed_flights(db: SessionLocal, count: int):
    """Seed flights in batches."""
    logger.info(f"Seeding {count} flights...")
    
    existing_count = db.query(Flight).count()
    if existing_count >= count:
        logger.info(f"Already have {existing_count} flights, skipping...")
        return
    
    flights_to_create = count - existing_count
    created = 0
    
    for i in range(flights_to_create):
        airline_code = random.choice(list(AIRLINES.keys()))
        dep_airport = random.choice(AIRPORTS)
        arr_airport = random.choice([a for a in AIRPORTS if a != dep_airport])
        
        base_date = datetime.now() + timedelta(days=random.randint(1, 90))
        departure_time = base_date.replace(hour=random.randint(6, 22), minute=random.choice([0, 30]))
        duration_hours = random.randint(1, 6)
        arrival_time = departure_time + timedelta(hours=duration_hours)
        
        flight_class = random.choice([FlightClass.ECONOMY, FlightClass.BUSINESS, FlightClass.FIRST])
        total_seats = 180 if flight_class == FlightClass.ECONOMY else 50
        
        flight = Flight(
            flight_id=f"FL{existing_count + i + 1:06d}",  # Use unique FL prefix to avoid conflicts
            airline_name=AIRLINES[airline_code],
            operator_name=AIRLINES[airline_code],
            departure_airport=dep_airport,
            arrival_airport=arr_airport,
            departure_datetime=departure_time,
            arrival_datetime=arrival_time,
            duration_minutes=duration_hours * 60,
            flight_class=flight_class.value,  # Use .value for enum
            base_price=Decimal(random.uniform(100, 800)),
            total_seats=total_seats,
            available_seats=random.randint(0, total_seats),
            rating=random.uniform(3.5, 5.0),
            total_reviews=random.randint(10, 500),
            is_active=True
        )
        
        db.add(flight)
        created += 1
        
        if created % CONFIG['batch_size'] == 0:
            db.commit()
            logger.info(f"  Created {created}/{flights_to_create} flights...")
    
    db.commit()
    logger.info(f"✅ Created {created} flights (Total: {db.query(Flight).count()})")


def seed_hotels(db: SessionLocal, count: int):
    """Seed hotels in batches."""
    logger.info(f"Seeding {count} hotels...")
    
    existing_count = db.query(Hotel).count()
    if existing_count >= count:
        logger.info(f"Already have {existing_count} hotels, skipping...")
        return
    
    hotels_to_create = count - existing_count
    created = 0
    
    for i in range(hotels_to_create):
        state = random.choice(US_STATES)
        city = random.choice(US_CITIES.get(state, ['City']))
        
        hotel = Hotel(
            hotel_id=f"H{existing_count + i + 1:07d}",
            hotel_name=f"{random.choice(HOTEL_CHAINS)} {city}",
            description=f"Luxury hotel in downtown {city}. Free cancellation up to 24 hours before check-in.",
            address=f"{random.randint(100, 9999)} {random.choice(['Broadway', 'Main', 'Park'])} Ave",
            city=city,
            state=state,
            zip_code=f"{random.randint(10000, 99999)}",
            star_rating=random.randint(3, 5),
            rating=random.uniform(3.5, 5.0),
            total_reviews=random.randint(50, 1000),
            amenities="WiFi,Parking,Pool,Gym,Restaurant,Bar,Room Service",
            phone_number=generate_phone(),
            email=f"reservations.{city.lower().replace(' ', '')}@hotel.com",
            website=f"https://www.{random.choice(HOTEL_CHAINS).lower().replace(' ', '')}.com",
            is_active=True
        )
        
        db.add(hotel)
        db.flush()  # Get hotel_id for rooms
        
        # Add rooms for this hotel
        room_types = [RoomType.SINGLE, RoomType.DOUBLE, RoomType.SUITE, RoomType.DELUXE]
        for room_type in room_types:
            base_price = {
                RoomType.SINGLE: 100,
                RoomType.DOUBLE: 150,
                RoomType.SUITE: 300,
                RoomType.DELUXE: 200
            }[room_type]
            
            room = HotelRoom(
                room_id=f"{hotel.hotel_id}_R{room_type.value}_{random.randint(1, 999)}",
                hotel_id=hotel.hotel_id,
                room_type=room_type.value,  # Use .value for enum
                room_number=f"{random.randint(1, 9)}{random.randint(0, 9)}{random.randint(1, 9)}",
                price_per_night=Decimal(base_price + random.uniform(-20, 50)),
                max_occupancy=random.randint(2, 4),
                total_rooms=random.randint(10, 50),
                available_rooms=random.randint(0, 50),
                is_active=True
            )
            db.add(room)
        
        created += 1
        
        if created % (CONFIG['batch_size'] // 10) == 0:  # Less frequent commits due to rooms
            db.commit()
            logger.info(f"  Created {created}/{hotels_to_create} hotels...")
    
    db.commit()
    logger.info(f"✅ Created {created} hotels (Total: {db.query(Hotel).count()})")
    logger.info(f"✅ Created hotel rooms (Total: {db.query(HotelRoom).count()})")


def seed_cars(db: SessionLocal, count: int):
    """Seed cars in batches."""
    logger.info(f"Seeding {count} cars...")
    
    existing_count = db.query(Car).count()
    if existing_count >= count:
        logger.info(f"Already have {existing_count} cars, skipping...")
        return
    
    cars_to_create = count - existing_count
    created = 0
    
    for i in range(cars_to_create):
        car_type = random.choice([CarType.COMPACT, CarType.SEDAN, CarType.SUV, CarType.LUXURY, CarType.VAN])
        state = random.choice(US_STATES)
        city = random.choice(US_CITIES.get(state, ['City']))
        airport = random.choice(AIRPORTS)
        
        car = Car(
            car_id=f"C{existing_count + i + 1:07d}",
            car_type=car_type.value,  # Use .value for enum
            make=random.choice(CAR_MAKES),
            model=random.choice(['Camry', 'Accord', 'F-150', 'Model 3', 'Explorer']),
            year=random.randint(2019, 2024),
            provider_name=random.choice(CAR_PROVIDERS),
            transmission_type=random.choice([TransmissionType.AUTOMATIC, TransmissionType.MANUAL]).value,
            seats=random.choice([4, 5, 7]),
            doors=random.choice([2, 4]),
            daily_rental_price=Decimal(random.uniform(30, 200)),
            pickup_location=f"{airport} Airport",
            city=city,
            state=state,
            rating=random.uniform(3.5, 5.0),
            total_reviews=random.randint(10, 500),
            is_available=True,
            is_active=True
        )
        
        db.add(car)
        created += 1
        
        if created % CONFIG['batch_size'] == 0:
            db.commit()
            logger.info(f"  Created {created}/{cars_to_create} cars...")
    
    db.commit()
    logger.info(f"✅ Created {created} cars (Total: {db.query(Car).count()})")


def seed_bookings_and_billings(db: SessionLocal, booking_count: int):
    """Seed bookings and corresponding billings."""
    logger.info(f"Seeding {booking_count} bookings and billings...")
    
    existing_bookings = db.query(Booking).count()
    if existing_bookings >= booking_count:
        logger.info(f"Already have {existing_bookings} bookings, skipping...")
        return
    
    # Get all users, flights, hotels, cars
    users = db.query(User.user_id).all()
    flights = db.query(Flight.flight_id).all()
    hotels = db.query(Hotel.hotel_id).all()
    cars = db.query(Car.car_id).all()
    
    if not users or not (flights or hotels or cars):
        logger.error("Need users and listings to create bookings!")
        return
    
    user_ids = [u[0] for u in users]
    flight_ids = [f[0] for f in flights]
    hotel_ids = [h[0] for h in hotels]
    car_ids = [c[0] for c in cars]
    
    bookings_to_create = booking_count - existing_bookings
    created = 0
    
    for i in range(bookings_to_create):
        # Random booking type
        booking_type_choice = random.choices(
            [BookingType.FLIGHT, BookingType.HOTEL, BookingType.CAR],
            weights=[0.4, 0.4, 0.2]
        )[0]
        
        if booking_type_choice == BookingType.FLIGHT and flight_ids:
            listing_id = random.choice(flight_ids)
            num_passengers = random.randint(1, 4)
            num_rooms = 0
            num_nights = 0
            base_price = Decimal(random.uniform(150, 800))
        elif booking_type_choice == BookingType.HOTEL and hotel_ids:
            listing_id = random.choice(hotel_ids)
            num_passengers = 0
            num_rooms = random.randint(1, 3)
            num_nights = random.randint(1, 7)
            base_price = Decimal(random.uniform(100, 300)) * num_nights * num_rooms
        elif car_ids:
            listing_id = random.choice(car_ids)
            num_passengers = 0
            num_rooms = 0
            num_nights = random.randint(1, 7)
            base_price = Decimal(random.uniform(30, 150)) * num_nights
        else:
            continue
        
        booking_date = datetime.now() - timedelta(days=random.randint(0, 180))
        check_in = booking_date + timedelta(days=random.randint(1, 30))
        check_out = check_in + timedelta(days=max(1, num_nights))
        
        booking = Booking(
            booking_id=f"B{existing_bookings + i + 1:07d}",
            user_id=random.choice(user_ids),
            booking_type=booking_type_choice.value,  # Use .value for enum
            listing_id=listing_id,
            check_in_date=check_in,
            check_out_date=check_out if num_nights > 0 else None,
            num_passengers=num_passengers,
            num_rooms=num_rooms,
            num_nights=num_nights,
            status=random.choices(['CONFIRMED', 'PENDING', 'CANCELLED'], weights=[0.7, 0.2, 0.1])[0],
            total_price=base_price,
            booking_date=booking_date
        )
        
        db.add(booking)
        db.flush()  # Get booking_id
        
        # Create corresponding billing
        payment_status = PaymentStatus.COMPLETED.value if booking.status == 'CONFIRMED' else PaymentStatus.PENDING.value
        tax = base_price * Decimal('0.08')
        
        billing = Billing(
            billing_id=f"BL{existing_bookings + i + 1:07d}",
            booking_id=booking.booking_id,
            user_id=booking.user_id,
            booking_type=booking.booking_type,
            transaction_date=booking_date,
            subtotal=base_price,
            tax_amount=tax,
            total_amount=base_price + tax,
            payment_method=random.choice(['CREDIT_CARD', 'DEBIT_CARD', 'PAYPAL']),
            payment_status=payment_status,
            card_last_four=f"{random.randint(1000, 9999)}",
            invoice_number=f"INV{existing_bookings + i + 1:07d}"
        )
        
        db.add(billing)
        created += 1
        
        if created % CONFIG['batch_size'] == 0:
            db.commit()
            logger.info(f"  Created {created}/{bookings_to_create} bookings and billings...")
    
    db.commit()
    logger.info(f"✅ Created {created} bookings (Total: {db.query(Booking).count()})")
    logger.info(f"✅ Created {created} billings (Total: {db.query(Billing).count()})")


def verify_counts(db: SessionLocal):
    """Verify and display all record counts."""
    logger.info("\n" + "="*60)
    logger.info("DATABASE VERIFICATION")
    logger.info("="*60)
    
    counts = {
        'Users': db.query(User).count(),
        'Flights': db.query(Flight).count(),
        'Hotels': db.query(Hotel).count(),
        'Hotel Rooms': db.query(HotelRoom).count(),
        'Cars': db.query(Car).count(),
        'Bookings': db.query(Booking).count(),
        'Billings': db.query(Billing).count(),
    }
    
    for entity, count in counts.items():
        status = "✅" if count > 0 else "❌"
        logger.info(f"{status} {entity:15s}: {count:,}")
    
    # Check if targets met
    logger.info("\n" + "="*60)
    logger.info("TARGET VERIFICATION")
    logger.info("="*60)
    
    targets = {
        'Users (10K+)': (counts['Users'], 10000),
        'Flights (10K+)': (counts['Flights'], 10000),
        'Hotels (1K+)': (counts['Hotels'], 1000),
        'Hotel Rooms (10K+)': (counts['Hotel Rooms'], 10000),
        'Cars (10K+)': (counts['Cars'], 10000),
        'Bookings (100K+)': (counts['Bookings'], 100000),
        'Billings (100K+)': (counts['Billings'], 100000),
    }
    
    all_met = True
    for name, (actual, target) in targets.items():
        met = actual >= target
        status = "✅" if met else "❌"
        percentage = (actual / target * 100) if target > 0 else 0
        logger.info(f"{status} {name:20s}: {actual:>8,} / {target:>8,} ({percentage:>6.1f}%)")
        if not met:
            all_met = False
    
    logger.info("="*60)
    if all_met:
        logger.info("🎉 ALL TARGETS MET!")
    else:
        logger.info("⚠️  Some targets not yet met. Run again to continue seeding.")
    logger.info("="*60 + "\n")
    
    return counts


def main():
    """Main seeding function."""
    logger.info("\n" + "="*60)
    logger.info("LARGE DATASET SEEDING")
    logger.info("="*60)
    logger.info(f"Targets:")
    logger.info(f"  Users:    {CONFIG['users']:,}")
    logger.info(f"  Flights:  {CONFIG['flights']:,}")
    logger.info(f"  Hotels:   {CONFIG['hotels']:,}")
    logger.info(f"  Cars:     {CONFIG['cars']:,}")
    logger.info(f"  Bookings: {CONFIG['bookings']:,}")
    logger.info(f"  Billings: {CONFIG['billings']:,}")
    logger.info("="*60 + "\n")
    
    db = SessionLocal()
    
    try:
        # Seed in order (dependencies)
        seed_users(db, CONFIG['users'])
        seed_flights(db, CONFIG['flights'])
        seed_hotels(db, CONFIG['hotels'])
        seed_cars(db, CONFIG['cars'])
        seed_bookings_and_billings(db, CONFIG['bookings'])
        
        # Verify all counts
        verify_counts(db)
        
    except Exception as e:
        logger.error(f"Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
