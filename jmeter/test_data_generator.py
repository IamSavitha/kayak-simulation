#!/usr/bin/env python3
"""
Generate 10,000+ test records for JMeter performance testing
"""
import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from backend.common.database import SessionLocal
from backend.models.mysql_models import User, Flight, Hotel, HotelRoom, Car
from faker import Faker
import random
from datetime import datetime, timedelta
import hashlib

fake = Faker()

def generate_ssn():
    """Generate valid SSN format: ###-##-####"""
    return f"{random.randint(100,999)}-{random.randint(10,99)}-{random.randint(1000,9999)}"

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def populate_users(db, count=10000):
    """Generate users for testing"""
    print(f"Generating {count} users...")
    users = []
    
    for i in range(count):
        user = User(
            user_id=generate_ssn(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            password_hash=hash_password("Test123!"),
            phone_number=fake.phone_number()[:15],
            address=fake.street_address(),
            city=fake.city(),
            state=fake.state_abbr(),
            zip_code=fake.zipcode(),
            is_active=True
        )
        users.append(user)
        
        if (i + 1) % 1000 == 0:
            print(f"  Created {i + 1} users...")
            db.bulk_save_objects(users)
            db.commit()
            users = []
    
    if users:
        db.bulk_save_objects(users)
        db.commit()
    
    print(f"✅ {count} users created")

def populate_flights(db, count=10000):
    """Generate flights for testing"""
    print(f"Generating {count} flights...")
    
    airlines = ["Delta", "United", "American", "Southwest", "JetBlue", "Alaska"]
    airports = ["SFO", "LAX", "JFK", "ORD", "DFW", "ATL", "SEA", "BOS", "MIA", "DEN"]
    classes = ["economy", "business", "first"]
    
    flights = []
    
    for i in range(count):
        dep_airport = random.choice(airports)
        arr_airport = random.choice([a for a in airports if a != dep_airport])
        
        dep_time = datetime.now() + timedelta(days=random.randint(1, 90))
        arr_time = dep_time + timedelta(hours=random.randint(2, 8))
        
        flight = Flight(
            flight_id=f"{random.choice(['AA', 'DL', 'UA', 'WN', 'B6'])}{random.randint(1000, 9999)}",
            airline_name=random.choice(airlines),
            operator_name=random.choice(airlines),
            departure_airport=dep_airport,
            arrival_airport=arr_airport,
            departure_datetime=dep_time,
            arrival_datetime=arr_time,
            flight_class=random.choice(classes),
            base_price=round(random.uniform(100, 1500), 2),
            total_seats=random.randint(100, 300),
            available_seats=random.randint(0, 200),
            is_active=True,
            rating=round(random.uniform(3.0, 5.0), 2)
        )
        flights.append(flight)
        
        if (i + 1) % 1000 == 0:
            print(f"  Created {i + 1} flights...")
            db.bulk_save_objects(flights)
            db.commit()
            flights = []
    
    if flights:
        db.bulk_save_objects(flights)
        db.commit()
    
    print(f"✅ {count} flights created")

def populate_hotels(db, count=2000):
    """Generate hotels with rooms"""
    print(f"Generating {count} hotels...")
    
    hotel_names = ["Marriott", "Hilton", "Hyatt", "Sheraton", "Westin", "Ritz Carlton"]
    cities = ["San Francisco", "Los Angeles", "New York", "Chicago", "Miami", "Boston", "Seattle"]
    
    hotels = []
    rooms = []
    
    for i in range(count):
        city = random.choice(cities)
        
        hotel = Hotel(
            hotel_id=f"H{str(i+1).zfill(7)}",
            hotel_name=f"{random.choice(hotel_names)} {city}",
            description=fake.text(max_nb_chars=200),
            address=fake.street_address(),
            city=city,
            state=fake.state_abbr(),
            zip_code=fake.zipcode(),
            star_rating=random.randint(3, 5),
            amenities="WiFi,Parking,Pool,Gym,Restaurant",
            phone_number=fake.phone_number()[:15],
            email=fake.email(),
            is_active=True,
            rating=round(random.uniform(3.5, 5.0), 2),
            total_reviews=random.randint(10, 1000)
        )
        hotels.append(hotel)
        
        # Create 4 room types per hotel
        room_types = ["single", "double", "deluxe", "suite"]
        for room_type in room_types:
            room = HotelRoom(
                room_id=f"{hotel.hotel_id}_R{room_type}_{random.randint(1,999)}",
                hotel_id=hotel.hotel_id,
                room_type=room_type,
                room_number=str(random.randint(100, 999)),
                price_per_night=round(random.uniform(80, 500), 2),
                max_occupancy=random.randint(2, 4),
                total_rooms=random.randint(10, 50),
                available_rooms=random.randint(0, 40),
                is_active=True
            )
            rooms.append(room)
        
        if (i + 1) % 500 == 0:
            print(f"  Created {i + 1} hotels...")
            db.bulk_save_objects(hotels)
            db.bulk_save_objects(rooms)
            db.commit()
            hotels = []
            rooms = []
    
    if hotels:
        db.bulk_save_objects(hotels)
        db.bulk_save_objects(rooms)
        db.commit()
    
    print(f"✅ {count} hotels with rooms created")

def populate_cars(db, count=5000):
    """Generate cars for testing"""
    print(f"Generating {count} cars...")
    
    companies = ["Hertz", "Enterprise", "Avis", "Budget", "National"]
    car_types = ["sedan", "suv", "compact", "luxury"]
    transmissions = ["automatic", "manual"]
    
    cars = []
    
    for i in range(count):
        car = Car(
            car_id=f"CAR{str(i+1).zfill(6)}",
            car_type=random.choice(car_types),
            company_name=random.choice(companies),
            model=fake.company(),
            year=random.randint(2018, 2024),
            transmission_type=random.choice(transmissions),
            num_seats=random.randint(4, 7),
            daily_price=round(random.uniform(30, 200), 2),
            available_quantity=random.randint(0, 20),
            is_active=True,
            rating=round(random.uniform(3.5, 5.0), 2)
        )
        cars.append(car)
        
        if (i + 1) % 1000 == 0:
            print(f"  Created {i + 1} cars...")
            db.bulk_save_objects(cars)
            db.commit()
            cars = []
    
    if cars:
        db.bulk_save_objects(cars)
        db.commit()
    
    print(f"✅ {count} cars created")

def main():
    """Main function to populate all test data"""
    print("=" * 60)
    print("KAYAK PERFORMANCE TEST DATA GENERATOR")
    print("=" * 60)
    print()
    
    db = SessionLocal()
    
    try:
        # Check current counts
        user_count = db.query(User).count()
        flight_count = db.query(Flight).count()
        hotel_count = db.query(Hotel).count()
        car_count = db.query(Car).count()
        
        print(f"Current database status:")
        print(f"  Users: {user_count}")
        print(f"  Flights: {flight_count}")
        print(f"  Hotels: {hotel_count}")
        print(f"  Cars: {car_count}")
        print()
        
        # Populate if needed
        if user_count < 10000:
            populate_users(db, 10000 - user_count)
        else:
            print(f"✅ Already have {user_count} users")
        
        if flight_count < 10000:
            populate_flights(db, 10000 - flight_count)
        else:
            print(f"✅ Already have {flight_count} flights")
        
        if hotel_count < 2000:
            populate_hotels(db, 2000 - hotel_count)
        else:
            print(f"✅ Already have {hotel_count} hotels")
        
        if car_count < 5000:
            populate_cars(db, 5000 - car_count)
        else:
            print(f"✅ Already have {car_count} cars")
        
        print()
        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total Users: {db.query(User).count()}")
        print(f"Total Flights: {db.query(Flight).count()}")
        print(f"Total Hotels: {db.query(Hotel).count()}")
        print(f"Total Hotel Rooms: {db.query(HotelRoom).count()}")
        print(f"Total Cars: {db.query(Car).count()}")
        print()
        print("✅ Database ready for performance testing!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
