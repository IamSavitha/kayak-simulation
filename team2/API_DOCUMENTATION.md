# Team 2 - Listing Services API Documentation

## Base URL
```
http://localhost:8002
```

## Authentication
Currently, no authentication is required. In production, this should be integrated with Team 1's authentication service.

---

## Flight Service API

### Create Flight
**POST** `/flights`

Creates a new flight listing.

**Request Body:**
```json
{
  "airline": "American Airlines",
  "departure_airport": "JFK",
  "arrival_airport": "LAX",
  "departure_date_time": "2024-06-01T10:00:00",
  "arrival_date_time": "2024-06-01T13:30:00",
  "duration_minutes": 330,
  "flight_class": "Economy",
  "ticket_price": 299.99,
  "total_available_seats": 150,
  "current_available_seats": 150
}
```

**Response:** `201 Created`
```json
{
  "flight_id": "FLT-ABC123DEF456",
  "airline": "American Airlines",
  "departure_airport": "JFK",
  "arrival_airport": "LAX",
  "departure_date_time": "2024-06-01T10:00:00",
  "arrival_date_time": "2024-06-01T13:30:00",
  "duration_minutes": 330,
  "flight_class": "Economy",
  "ticket_price": 299.99,
  "total_available_seats": 150,
  "current_available_seats": 150,
  "flight_rating": 0.0,
  "total_reviews": 0,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### Get Flight by ID
**GET** `/flights/{flight_id}`

**Response:** `200 OK`
```json
{
  "flight_id": "FLT-ABC123DEF456",
  ...
}
```

### Update Flight
**PUT** `/flights/{flight_id}`

**Request Body:** (all fields optional)
```json
{
  "ticket_price": 349.99,
  "current_available_seats": 140
}
```

**Response:** `200 OK`

### Delete Flight
**DELETE** `/flights/{flight_id}`

**Response:** `204 No Content`

### Search Flights
**GET** `/flights/search`

**Query Parameters:**
- `origin` (string, optional): Departure airport code
- `destination` (string, optional): Arrival airport code
- `departure_date` (datetime, optional): Departure date
- `min_price` (float, optional): Minimum price
- `max_price` (float, optional): Maximum price
- `flight_class` (string, optional): Economy, Business, or First
- `departure_time_start` (string, optional): HH:MM format
- `departure_time_end` (string, optional): HH:MM format
- `arrival_time_start` (string, optional): HH:MM format
- `arrival_time_end` (string, optional): HH:MM format
- `page` (int, default=1): Page number
- `page_size` (int, default=20, max=100): Results per page

**Example:**
```
GET /flights/search?origin=JFK&destination=LAX&departure_date=2024-06-01&min_price=200&max_price=500&page=1&page_size=20
```

**Response:** `200 OK`
```json
{
  "flights": [...],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8
}
```

### Update Flight Availability
**PUT** `/flights/{flight_id}/availability?seats_change=-5`

Used by booking service to update seat availability.

**Response:** `200 OK`
```json
{
  "message": "Availability updated successfully"
}
```

### Update Flight Rating
**PUT** `/flights/{flight_id}/rating?new_rating=4.5&total_reviews=100`

Used by review service to update aggregated rating.

**Response:** `200 OK`

---

## Hotel Service API

### Create Hotel
**POST** `/hotels`

**Request Body:**
```json
{
  "hotel_name": "Grand Hotel",
  "address": "123 Main Street",
  "city": "New York",
  "state": "NY",
  "zip_code": "10001",
  "star_rating": 4,
  "number_of_rooms": 100,
  "current_available_rooms": 50,
  "room_type": "Deluxe",
  "price_per_night": 199.99,
  "amenities": "Wi-Fi, Breakfast, Parking, Pool",
  "latitude": 40.7128,
  "longitude": -74.0060
}
```

**Response:** `201 Created`

### Get Hotel by ID
**GET** `/hotels/{hotel_id}`

**Response:** `200 OK`

### Update Hotel
**PUT** `/hotels/{hotel_id}`

**Request Body:** (all fields optional)

### Delete Hotel
**DELETE** `/hotels/{hotel_id}`

**Response:** `204 No Content`

### Search Hotels
**GET** `/hotels/search`

**Query Parameters:**
- `location` (string, optional): City or state
- `city` (string, optional): City name
- `state` (string, optional): State abbreviation
- `check_in_date` (datetime, optional)
- `check_out_date` (datetime, optional)
- `min_price` (float, optional)
- `max_price` (float, optional)
- `min_stars` (int, optional): 1-5
- `max_stars` (int, optional): 1-5
- `amenities` (string, optional): Comma-separated list
- `page` (int, default=1)
- `page_size` (int, default=20, max=100)

**Example:**
```
GET /hotels/search?city=New York&min_stars=4&max_price=300&amenities=Wi-Fi,Pool&page=1&page_size=20
```

**Response:** `200 OK`
```json
{
  "hotels": [...],
  "total": 250,
  "page": 1,
  "page_size": 20,
  "total_pages": 13
}
```

### Upload Hotel Image
**POST** `/hotels/{hotel_id}/images`

**Form Data:**
- `image` (file): Image file
- `image_type` (string): "hotel" or "room"

**Response:** `201 Created`
```json
{
  "image_id": "...",
  "message": "Image uploaded successfully"
}
```

### Get Hotel Images
**GET** `/hotels/{hotel_id}/images?image_type=hotel`

**Response:** `200 OK`
```json
{
  "images": [...]
}
```

### Update Hotel Availability
**PUT** `/hotels/{hotel_id}/availability?rooms_change=-2`

**Response:** `200 OK`

### Update Hotel Rating
**PUT** `/hotels/{hotel_id}/rating?new_rating=4.5&total_reviews=100`

**Response:** `200 OK`

---

## Car Service API

### Create Car
**POST** `/cars`

**Request Body:**
```json
{
  "car_type": "SUV",
  "company_provider_name": "Hertz",
  "model_and_year": "Toyota RAV4 2023",
  "transmission_type": "Automatic",
  "number_of_seats": 5,
  "daily_rental_price": 89.99,
  "availability_status": "Available",
  "location_city": "New York",
  "location_state": "NY",
  "location_address": "123 Car Rental St"
}
```

**Response:** `201 Created`

### Get Car by ID
**GET** `/cars/{car_id}`

**Response:** `200 OK`

### Update Car
**PUT** `/cars/{car_id}`

**Request Body:** (all fields optional)

### Delete Car
**DELETE** `/cars/{car_id}`

**Response:** `204 No Content`

### Search Cars
**GET** `/cars/search`

**Query Parameters:**
- `location` (string, optional): City or state
- `city` (string, optional)
- `state` (string, optional)
- `car_type` (string, optional): SUV, Sedan, Compact, etc.
- `min_price` (float, optional)
- `max_price` (float, optional)
- `transmission_type` (string, optional): Automatic or Manual
- `min_seats` (int, optional): 2-8
- `max_seats` (int, optional): 2-8
- `page` (int, default=1)
- `page_size` (int, default=20, max=100)

**Example:**
```
GET /cars/search?city=New York&car_type=SUV&min_seats=5&max_price=150&page=1&page_size=20
```

**Response:** `200 OK`
```json
{
  "cars": [...],
  "total": 80,
  "page": 1,
  "page_size": 20,
  "total_pages": 4
}
```

### Upload Car Image
**POST** `/cars/{car_id}/images`

**Form Data:**
- `image` (file): Image file

**Response:** `201 Created`

### Get Car Images
**GET** `/cars/{car_id}/images`

**Response:** `200 OK`

### Update Car Availability
**PUT** `/cars/{car_id}/availability?status=Reserved`

**Status values:** Available, Unavailable, Reserved

**Response:** `200 OK`

### Update Car Rating
**PUT** `/cars/{car_id}/rating?new_rating=4.5&total_reviews=100`

**Response:** `200 OK`

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 404 Not Found
```json
{
  "detail": "Flight not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error message"
}
```

---

## Integration Notes

### For Team 1 (User & Admin Services)
- Admin can use all CRUD endpoints to manage listings
- Search endpoints are available for user search interface
- Listing data format is documented above

### For Team 3 (Booking Service)
- Use availability update endpoints when creating/canceling bookings:
  - `PUT /flights/{flight_id}/availability?seats_change=-1`
  - `PUT /hotels/{hotel_id}/availability?rooms_change=-1`
  - `PUT /cars/{car_id}/availability?status=Reserved`
- Use rating update endpoints when reviews are submitted

### For Team 4 (Billing Service)
- Use `GET /flights/{flight_id}`, `GET /hotels/{hotel_id}`, `GET /cars/{car_id}` to get pricing information

### For Team 5 (Kafka Integration)
- Service publishes events to `listing_updates` topic:
  - `listing_created`
  - `listing_updated`
  - `listing_deleted`
- Event schema:
```json
{
  "event_type": "listing_created|listing_updated|listing_deleted",
  "listing_type": "flight|hotel|car",
  "listing_id": "...",
  "timestamp": "2024-01-01T00:00:00",
  "data": {...}
}
```

