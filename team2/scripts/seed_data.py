"""
Data seeding script for flights, hotels, and cars
Populates 10,000+ listings
"""
import random
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.repositories.flight_repository import FlightRepository
from backend.repositories.hotel_repository import HotelRepository
from backend.repositories.car_repository import CarRepository

# Airport codes
AIRPORTS = [
    'JFK', 'LAX', 'ORD', 'DFW', 'DEN', 'SFO', 'SEA', 'LAS', 'MIA', 'PHX',
    'IAH', 'MCO', 'MSP', 'DTW', 'BOS', 'PHL', 'LGA', 'BWI', 'SLC', 'DCA',
    'MDW', 'HNL', 'FLL', 'IAD', 'SAN', 'STL', 'TPA', 'PDX', 'HOU', 'OAK'
]

AIRLINES = [
    'American Airlines', 'Delta Air Lines', 'United Airlines', 'Southwest Airlines',
    'JetBlue Airways', 'Alaska Airlines', 'Spirit Airlines', 'Frontier Airlines'
]

FLIGHT_CLASSES = ['Economy', 'Business', 'First']

CITIES_STATES = [
    ('New York', 'NY'), ('Los Angeles', 'CA'), ('Chicago', 'IL'), ('Houston', 'TX'),
    ('Phoenix', 'AZ'), ('Philadelphia', 'PA'), ('San Antonio', 'TX'), ('San Diego', 'CA'),
    ('Dallas', 'TX'), ('San Jose', 'CA'), ('Austin', 'TX'), ('Jacksonville', 'FL'),
    ('San Francisco', 'CA'), ('Indianapolis', 'IN'), ('Columbus', 'OH'), ('Fort Worth', 'TX'),
    ('Charlotte', 'NC'), ('Seattle', 'WA'), ('Denver', 'CO'), ('Washington', 'DC'),
    ('Boston', 'MA'), ('El Paso', 'TX'), ('Detroit', 'MI'), ('Nashville', 'TN'),
    ('Portland', 'OR'), ('Oklahoma City', 'OK'), ('Las Vegas', 'NV'), ('Memphis', 'TN'),
    ('Louisville', 'KY'), ('Baltimore', 'MD'), ('Milwaukee', 'WI'), ('Albuquerque', 'NM'),
    ('Tucson', 'AZ'), ('Fresno', 'CA'), ('Sacramento', 'CA'), ('Kansas City', 'MO'),
    ('Mesa', 'AZ'), ('Atlanta', 'GA'), ('Omaha', 'NE'), ('Colorado Springs', 'CO')
]

AMENITIES_LIST = [
    'Wi-Fi', 'Breakfast', 'Parking', 'Pool', 'Gym', 'Spa', 'Restaurant',
    'Bar', 'Room Service', 'Laundry', 'Business Center', 'Pet Friendly',
    'Air Conditioning', 'Heating', 'TV', 'Refrigerator', 'Microwave'
]

CAR_TYPES = ['SUV', 'Sedan', 'Compact', 'Luxury', 'Convertible', 'Truck', 'Van', 'Hatchback']

CAR_PROVIDERS = [
    'Hertz', 'Enterprise', 'Avis', 'Budget', 'National', 'Alamo', 'Dollar',
    'Thrifty', 'Sixt', 'Payless'
]

CAR_MODELS = [
    'Toyota Camry 2023', 'Honda Accord 2023', 'Ford F-150 2023', 'Chevrolet Silverado 2023',
    'Nissan Altima 2023', 'Toyota RAV4 2023', 'Honda CR-V 2023', 'Ford Explorer 2023',
    'Jeep Grand Cherokee 2023', 'Chevrolet Equinox 2023', 'BMW 3 Series 2023',
    'Mercedes-Benz C-Class 2023', 'Audi A4 2023', 'Lexus ES 2023', 'Tesla Model 3 2023'
]

def generate_flights(count=3000):
    """Generate flight data"""
    print(f"Generating {count} flights...")
    flights = []
    
    for i in range(count):
        departure_airport = random.choice(AIRPORTS)
        arrival_airport = random.choice([a for a in AIRPORTS if a != departure_airport])
        
        days_ahead = random.randint(1, 180)
        departure_date = datetime.now() + timedelta(days=days_ahead)
        departure_time = departure_date.replace(
            hour=random.randint(6, 22),
            minute=random.choice([0, 15, 30, 45])
        )
        
        duration_minutes = random.randint(60, 720)
        arrival_time = departure_time + timedelta(minutes=duration_minutes)
        
        flight_class = random.choice(FLIGHT_CLASSES)
        base_price = random.uniform(100, 800)
        if flight_class == 'Business':
            base_price *= 2.5
        elif flight_class == 'First':
            base_price *= 4
        
        total_seats = random.randint(50, 300)
        
        flight = {
            'airline': random.choice(AIRLINES),
            'departure_airport': departure_airport,
            'arrival_airport': arrival_airport,
            'departure_date_time': departure_time,
            'arrival_date_time': arrival_time,
            'duration_minutes': duration_minutes,
            'flight_class': flight_class,
            'ticket_price': round(base_price, 2),
            'total_available_seats': total_seats,
            'current_available_seats': random.randint(10, total_seats)
        }
        
        try:
            created = FlightRepository.create(flight)
            flights.append(created)
            if (i + 1) % 100 == 0:
                print(f"  Created {i + 1}/{count} flights")
        except Exception as e:
            print(f"  Error creating flight {i + 1}: {e}")
    
    print(f"Successfully created {len(flights)} flights")
    return flights

def generate_hotels(count=4000):
    """Generate hotel data"""
    print(f"Generating {count} hotels...")
    hotels = []
    
    for i in range(count):
        city, state = random.choice(CITIES_STATES)
        
        num_amenities = random.randint(3, 8)
        selected_amenities = random.sample(AMENITIES_LIST, num_amenities)
        amenities_str = ', '.join(selected_amenities)
        
        star_rating = random.randint(1, 5)
        base_price = random.uniform(50, 500)
        if star_rating >= 4:
            base_price *= 1.5
        if star_rating == 5:
            base_price *= 2
        
        total_rooms = random.randint(20, 500)
        
        hotel = {
            'hotel_name': f"{random.choice(['Grand', 'Royal', 'Plaza', 'Park', 'Regency', 'Inn', 'Lodge', 'Resort'])} {random.choice(['Hotel', 'Suites', 'Resort', 'Inn'])}",
            'address': f"{random.randint(100, 9999)} {random.choice(['Main', 'Park', 'Oak', 'Maple', 'Elm', 'First', 'Second', 'Broadway'])} Street",
            'city': city,
            'state': state,
            'zip_code': f"{random.randint(10000, 99999)}",
            'star_rating': star_rating,
            'number_of_rooms': total_rooms,
            'current_available_rooms': random.randint(5, total_rooms),
            'room_type': random.choice(['Standard', 'Deluxe', 'Suite', 'Executive', 'Presidential']),
            'price_per_night': round(base_price, 2),
            'amenities': amenities_str,
            'latitude': round(random.uniform(25.0, 49.0), 6),
            'longitude': round(random.uniform(-125.0, -66.0), 6)
        }
        
        try:
            created = HotelRepository.create(hotel)
            hotels.append(created)
            if (i + 1) % 100 == 0:
                print(f"  Created {i + 1}/{count} hotels")
        except Exception as e:
            print(f"  Error creating hotel {i + 1}: {e}")
    
    print(f"Successfully created {len(hotels)} hotels")
    return hotels

def generate_cars(count=3000):
    """Generate car data"""
    print(f"Generating {count} cars...")
    cars = []
    
    for i in range(count):
        city, state = random.choice(CITIES_STATES)
        
        car_type = random.choice(CAR_TYPES)
        base_price = random.uniform(30, 200)
        if car_type == 'Luxury':
            base_price *= 2.5
        elif car_type == 'SUV':
            base_price *= 1.3
        elif car_type == 'Compact':
            base_price *= 0.8
        
        car = {
            'car_type': car_type,
            'company_provider_name': random.choice(CAR_PROVIDERS),
            'model_and_year': random.choice(CAR_MODELS),
            'transmission_type': random.choice(['Automatic', 'Manual']),
            'number_of_seats': random.choice([4, 5, 6, 7, 8]),
            'daily_rental_price': round(base_price, 2),
            'availability_status': random.choice(['Available', 'Available', 'Available', 'Reserved']),
            'location_city': city,
            'location_state': state,
            'location_address': f"{random.randint(100, 9999)} {random.choice(['Rental', 'Car', 'Auto', 'Drive'])} Avenue"
        }
        
        try:
            created = CarRepository.create(car)
            cars.append(created)
            if (i + 1) % 100 == 0:
                print(f"  Created {i + 1}/{count} cars")
        except Exception as e:
            print(f"  Error creating car {i + 1}: {e}")
    
    print(f"Successfully created {len(cars)} cars")
    return cars

def main():
    """Main seeding function"""
    print("=" * 50)
    print("Starting data seeding for Team 2 - Listing Services")
    print("=" * 50)
    
    flights = generate_flights(3000)
    hotels = generate_hotels(4000)
    cars = generate_cars(3000)
    
    total = len(flights) + len(hotels) + len(cars)
    print("\n" + "=" * 50)
    print(f"Seeding completed!")
    print(f"Total listings created: {total}")
    print(f"  - Flights: {len(flights)}")
    print(f"  - Hotels: {len(hotels)}")
    print(f"  - Cars: {len(cars)}")
    print("=" * 50)

if __name__ == "__main__":
    main()
