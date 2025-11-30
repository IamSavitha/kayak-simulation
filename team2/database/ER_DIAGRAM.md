# Database ER Diagram Documentation

## MySQL Schema - Listings Database

### Flights Table
```
┌─────────────────────────────────────────────────────────────┐
│                         FLIGHTS                              │
├─────────────────────────────────────────────────────────────┤
│ PK  flight_id                    VARCHAR(50)                 │
│     airline                      VARCHAR(100)                │
│     departure_airport           VARCHAR(10)                 │
│     arrival_airport              VARCHAR(10)                 │
│     departure_date_time          DATETIME                    │
│     arrival_date_time            DATETIME                    │
│     duration_minutes             INT                         │
│     flight_class                 ENUM(Economy,Business,First)│
│     ticket_price                 DECIMAL(10,2)               │
│     total_available_seats        INT                         │
│     current_available_seats      INT                         │
│     flight_rating                DECIMAL(3,2)                │
│     total_reviews                INT                         │
│     created_at                   TIMESTAMP                   │
│     updated_at                   TIMESTAMP                   │
└─────────────────────────────────────────────────────────────┘
```

**Indexes:**
- `idx_departure_airport` on `departure_airport`
- `idx_arrival_airport` on `arrival_airport`
- `idx_departure_date` on `departure_date_time`
- `idx_price` on `ticket_price`
- `idx_class` on `flight_class`
- `idx_rating` on `flight_rating`
- `idx_airline` on `airline`
- `idx_flight_search` on `(departure_airport, arrival_airport, departure_date_time, ticket_price)`
- `idx_flight_availability` on `(current_available_seats, departure_date_time)`

---

### Hotels Table
```
┌─────────────────────────────────────────────────────────────┐
│                         HOTELS                               │
├─────────────────────────────────────────────────────────────┤
│ PK  hotel_id                    VARCHAR(50)                 │
│     hotel_name                  VARCHAR(200)                │
│     address                     VARCHAR(255)                │
│     city                        VARCHAR(100)                │
│     state                       VARCHAR(2)                   │
│     zip_code                    VARCHAR(10)                  │
│     star_rating                 INT (1-5)                    │
│     number_of_rooms              INT                         │
│     current_available_rooms     INT                         │
│     room_type                   VARCHAR(50)                  │
│     price_per_night             DECIMAL(10,2)                │
│     amenities                   TEXT                         │
│     hotel_rating                DECIMAL(3,2)                │
│     total_reviews               INT                          │
│     latitude                    DECIMAL(10,8)                │
│     longitude                   DECIMAL(11,8)                │
│     created_at                  TIMESTAMP                    │
│     updated_at                  TIMESTAMP                    │
└─────────────────────────────────────────────────────────────┘
```

**Indexes:**
- `idx_city` on `city`
- `idx_state` on `state`
- `idx_star_rating` on `star_rating`
- `idx_price` on `price_per_night`
- `idx_rating` on `hotel_rating`
- `idx_location` on `(city, state)`
- `idx_amenities` FULLTEXT on `amenities`
- `idx_hotel_search` on `(city, state, star_rating, price_per_night)`
- `idx_hotel_availability` on `(current_available_rooms, city)`

---

### Cars Table
```
┌─────────────────────────────────────────────────────────────┐
│                          CARS                                │
├─────────────────────────────────────────────────────────────┤
│ PK  car_id                      VARCHAR(50)                 │
│     car_type                    VARCHAR(50)                 │
│     company_provider_name       VARCHAR(100)                │
│     model_and_year              VARCHAR(100)                 │
│     transmission_type            ENUM(Automatic,Manual)      │
│     number_of_seats              INT                         │
│     daily_rental_price          DECIMAL(10,2)                │
│     car_rating                  DECIMAL(3,2)                 │
│     total_reviews                INT                         │
│     availability_status          ENUM(Available,Unavailable, │
│                                      Reserved)               │
│     location_city                VARCHAR(100)               │
│     location_state               VARCHAR(2)                  │
│     location_address             VARCHAR(255)               │
│     created_at                   TIMESTAMP                  │
│     updated_at                   TIMESTAMP                  │
└─────────────────────────────────────────────────────────────┘
```

**Indexes:**
- `idx_car_type` on `car_type`
- `idx_provider` on `company_provider_name`
- `idx_transmission` on `transmission_type`
- `idx_seats` on `number_of_seats`
- `idx_price` on `daily_rental_price`
- `idx_rating` on `car_rating`
- `idx_status` on `availability_status`
- `idx_location` on `(location_city, location_state)`
- `idx_car_search` on `(location_city, location_state, car_type, daily_rental_price)`

---

## MongoDB Schema - Images Collections

### hotel_images Collection
```json
{
  "_id": ObjectId,
  "hotel_id": "HTL-ABC123DEF456",
  "image_type": "hotel" | "room",
  "image_data": Binary,
  "metadata": {
    "filename": "hotel_image.jpg",
    "content_type": "image/jpeg",
    "size": 1024000
  },
  "created_at": ISODate
}
```

### car_images Collection
```json
{
  "_id": ObjectId,
  "car_id": "CAR-ABC123DEF456",
  "image_data": Binary,
  "metadata": {
    "filename": "car_image.jpg",
    "content_type": "image/jpeg",
    "size": 512000
  },
  "created_at": ISODate
}
```

---

## Relationships

### External Relationships (with other teams' databases)

1. **With Team 3 (Bookings):**
   - Bookings reference `flight_id`, `hotel_id`, or `car_id`
   - No foreign key constraint (microservices architecture)
   - Availability updated via API calls

2. **With Team 4 (Billing):**
   - Billing references listing IDs for pricing
   - No foreign key constraint
   - Pricing retrieved via API calls

3. **With Team 1 (Reviews):**
   - Reviews reference listing IDs
   - Rating aggregation updated via API calls

---

## Data Volume Estimates

- **Flights**: 3,000+ records
- **Hotels**: 4,000+ records
- **Cars**: 3,000+ records
- **Total**: 10,000+ listings

---

## Performance Considerations

1. **Indexes**: Optimized for common search patterns
2. **Composite Indexes**: For multi-field searches
3. **Full-Text Search**: For amenities search in hotels
4. **Caching**: Redis caching for frequently accessed listings
5. **Connection Pooling**: MySQL connection pool (10-20 connections)

---

## Notes

- All tables use `VARCHAR(50)` for IDs with prefix (FLT-, HTL-, CAR-)
- Ratings are stored as `DECIMAL(3,2)` (0.00 to 5.00)
- Timestamps use `TIMESTAMP` with auto-update on `updated_at`
- No foreign keys (microservices architecture)
- Images stored in MongoDB as Binary data

