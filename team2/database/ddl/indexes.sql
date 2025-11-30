-- Additional Indexes for Performance Optimization
USE kayak_listings;

-- Composite indexes for common search queries
CREATE INDEX IF NOT EXISTS idx_flight_search ON flights(departure_airport, arrival_airport, departure_date_time, ticket_price);
CREATE INDEX IF NOT EXISTS idx_hotel_search ON hotels(city, state, star_rating, price_per_night);
CREATE INDEX IF NOT EXISTS idx_car_search ON cars(location_city, location_state, car_type, daily_rental_price);

-- Indexes for availability checks
CREATE INDEX IF NOT EXISTS idx_flight_availability ON flights(current_available_seats, departure_date_time);
CREATE INDEX IF NOT EXISTS idx_hotel_availability ON hotels(current_available_rooms, city);

