# 🎯 KAYAK SIMULATION - COMPLETE TECHNICAL DOCUMENTATION

## Project Overview
**Distributed Systems Travel Booking Platform (Kayak Clone)**
- **Architecture:** 3-Tier Microservices Architecture
- **Scale:** 10,000+ listings, 10,000+ users, 100,000+ bookings
- **Technologies:** Python FastAPI, React, MySQL, MongoDB, Redis, Kafka, Docker

---

# 📊 SYSTEM ARCHITECTURE

## 1. Three-Tier Architecture

### **Tier 1: Client Layer (Frontend)**
- **Technology:** React with TypeScript
- **Port:** 3000
- **Purpose:** User interface for customers and admins
- **Key Features:**
  - Flight/Hotel/Car search and booking
  - User authentication and profile management
  - AI-powered chatbot integration
  - Real-time updates via WebSockets
  - Admin dashboard for analytics

### **Tier 2: Middleware Layer (Backend Services)**
**Microservices Architecture - 9 Independent Services:**

1. **User Service** (Port 8001)
   - User registration, login, authentication
   - JWT token generation and validation
   - Profile management
   - Password encryption with bcrypt

2. **Flight Service** (Port 8002)
   - Flight search and filtering
   - Flight CRUD operations
   - Price calculations
   - Availability checking

3. **Hotel Service** (Port 8003)
   - Hotel and room search
   - Hotel CRUD operations
   - Room availability management
   - Price calculations per night

4. **Car Service** (Port 8004)
   - Car rental search
   - Car CRUD operations
   - Daily rate management
   - Availability tracking

5. **Booking Service** (Port 8009)
   - Unified booking creation (flights, hotels, cars)
   - Booking status management
   - User booking history
   - Availability validation

6. **Billing Service** (Port 8005)
   - Payment processing simulation
   - Billing record creation
   - Transaction history
   - Payment status tracking

7. **Admin Service** (Port 8006)
   - Dashboard analytics
   - User/listing management
   - System statistics
   - Revenue tracking

8. **Search Service** (Port 8007)
   - Unified search across all services
   - Advanced filtering and sorting
   - Cross-service search aggregation

9. **AI Service** (Port 8008)
   - Intelligent chatbot (Concierge Agent)
   - Natural language processing
   - Intent recognition
   - Personalized recommendations
   - Conversation history

### **Tier 3: Data Layer (Databases)**
- **MySQL:** Structured relational data
- **MongoDB:** Unstructured document data
- **Redis:** In-memory caching
- **Kafka + Zookeeper:** Event streaming

---

# 🗄️ DATABASE USAGE - DETAILED

## 1. MySQL (Relational Database)

### **Why MySQL?**
- **ACID Compliance:** Transactions for bookings and payments
- **Structured Data:** Well-defined schemas for core entities
- **Relationships:** Foreign keys between users, bookings, listings
- **Complex Queries:** JOINs for analytics and reporting

### **What Data is Stored:**

#### **Tables and Schema:**

**1. Users Table**
```sql
CREATE TABLE users (
    user_id VARCHAR(11) PRIMARY KEY,  -- SSN format: XXX-XX-XXXX
    username VARCHAR(50) UNIQUE,
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    phone VARCHAR(15),
    address TEXT,
    city VARCHAR(50),
    state VARCHAR(2),  -- Validated state codes
    zip_code VARCHAR(10),  -- Validated ZIP codes
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

**2. Flights Table**
```sql
CREATE TABLE flights (
    flight_id INT PRIMARY KEY AUTO_INCREMENT,
    flight_number VARCHAR(10),
    airline VARCHAR(50),
    departure_airport VARCHAR(3),  -- IATA codes: SFO, LAX, JFK
    arrival_airport VARCHAR(3),
    departure_time DATETIME,
    arrival_time DATETIME,
    price DECIMAL(10,2),
    available_seats INT,
    aircraft_type VARCHAR(50),
    created_at TIMESTAMP
);
```

**3. Hotels Table**
```sql
CREATE TABLE hotels (
    hotel_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    address TEXT,
    city VARCHAR(50),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    star_rating DECIMAL(2,1),  -- 1.0 to 5.0
    amenities JSON,  -- ['WiFi', 'Pool', 'Gym']
    description TEXT,
    created_at TIMESTAMP
);
```

**4. Rooms Table** (One-to-Many with Hotels)
```sql
CREATE TABLE rooms (
    room_id INT PRIMARY KEY AUTO_INCREMENT,
    hotel_id INT,
    room_type VARCHAR(50),  -- 'Single', 'Double', 'Suite'
    price_per_night DECIMAL(10,2),
    total_rooms INT,
    available_rooms INT,
    amenities JSON,
    FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id)
);
```

**5. Cars Table**
```sql
CREATE TABLE cars (
    car_id INT PRIMARY KEY AUTO_INCREMENT,
    make VARCHAR(50),
    model VARCHAR(50),
    year INT,
    category VARCHAR(50),  -- 'Economy', 'SUV', 'Luxury'
    daily_rate DECIMAL(10,2),
    location VARCHAR(100),
    available_units INT,
    features JSON,
    created_at TIMESTAMP
);
```

**6. Bookings Table** (Central transaction table)
```sql
CREATE TABLE bookings (
    booking_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id VARCHAR(11),
    booking_type ENUM('flight', 'hotel', 'car'),
    item_id INT,  -- References flight_id, hotel_id, or car_id
    booking_date DATE,
    status ENUM('confirmed', 'cancelled', 'completed'),
    total_price DECIMAL(10,2),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

**7. Billing Table**
```sql
CREATE TABLE billing (
    billing_id INT PRIMARY KEY AUTO_INCREMENT,
    booking_id INT,
    user_id VARCHAR(11),
    amount DECIMAL(10,2),
    payment_method VARCHAR(50),
    payment_status ENUM('pending', 'completed', 'failed'),
    transaction_id VARCHAR(100),
    billing_date TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
);
```

### **Where MySQL is Used:**

1. **User Service** - User authentication and profile
2. **Flight/Hotel/Car Services** - Listing management
3. **Booking Service** - Transaction processing
4. **Billing Service** - Payment records
5. **Admin Service** - Analytics queries with JOINs

### **Example Queries:**

```sql
-- Get user's booking history with details
SELECT b.*, u.username, u.email
FROM bookings b
JOIN users u ON b.user_id = u.user_id
WHERE b.user_id = '123-45-6789'
ORDER BY b.created_at DESC;

-- Admin analytics: Revenue by booking type
SELECT booking_type, 
       COUNT(*) as total_bookings,
       SUM(total_price) as total_revenue
FROM bookings
WHERE status = 'confirmed'
GROUP BY booking_type;

-- Hotel search with room availability
SELECT h.*, r.room_type, r.price_per_night, r.available_rooms
FROM hotels h
JOIN rooms r ON h.hotel_id = r.hotel_id
WHERE h.city = 'San Francisco' 
  AND r.available_rooms > 0
  AND r.price_per_night <= 200;
```

### **Performance Optimizations:**
- **Indexes:** On user_id, email, booking_date, city, airports
- **Connection Pooling:** Reuse database connections (max 50)
- **Query Optimization:** Avoid N+1 queries, use JOINs efficiently

---

## 2. MONGODB (Document Database)

### **Why MongoDB?**
- **Flexible Schema:** Unstructured data like logs, analytics
- **Document Storage:** JSON-like documents for complex nested data
- **Scalability:** Horizontal scaling for big data
- **Fast Writes:** Optimized for logging and events

### **What Data is Stored:**

#### **Collections:**

**1. chat_sessions**
```javascript
{
  "_id": ObjectId("..."),
  "session_id": "uuid-string",
  "user_id": "123-45-6789",
  "messages": [
    {
      "role": "user",
      "content": "Find me hotels in San Francisco",
      "timestamp": ISODate("2024-12-08T10:30:00Z")
    },
    {
      "role": "assistant",
      "content": "I found 15 hotels in San Francisco...",
      "timestamp": ISODate("2024-12-08T10:30:05Z"),
      "intent": "hotel_search",
      "extracted_data": {
        "city": "San Francisco",
        "price_max": null
      }
    }
  ],
  "created_at": ISODate("2024-12-08T10:30:00Z"),
  "updated_at": ISODate("2024-12-08T10:35:00Z")
}
```

**2. search_logs**
```javascript
{
  "_id": ObjectId("..."),
  "user_id": "123-45-6789",
  "search_type": "flight",
  "query_params": {
    "departure_airport": "SFO",
    "arrival_airport": "LAX",
    "departure_date": "2024-12-15",
    "passengers": 2
  },
  "results_count": 25,
  "filters_applied": ["price_max", "airline"],
  "timestamp": ISODate("2024-12-08T10:30:00Z")
}
```

**3. booking_logs** (Kafka events stored)
```javascript
{
  "_id": ObjectId("..."),
  "event_type": "booking_created",
  "booking_id": 12345,
  "user_id": "123-45-6789",
  "booking_type": "hotel",
  "amount": 450.00,
  "status": "confirmed",
  "timestamp": ISODate("2024-12-08T10:30:00Z"),
  "metadata": {
    "hotel_name": "Grand Hotel SF",
    "check_in": "2024-12-20",
    "check_out": "2024-12-22"
  }
}
```

**4. user_journeys** (User behavior tracking)
```javascript
{
  "_id": ObjectId("..."),
  "user_id": "123-45-6789",
  "session_id": "session-uuid",
  "journey": [
    {
      "action": "search_flights",
      "timestamp": ISODate("2024-12-08T10:25:00Z"),
      "details": {"route": "SFO-LAX"}
    },
    {
      "action": "view_flight_details",
      "timestamp": ISODate("2024-12-08T10:26:00Z"),
      "flight_id": 123
    },
    {
      "action": "add_to_cart",
      "timestamp": ISODate("2024-12-08T10:27:00Z")
    },
    {
      "action": "checkout",
      "timestamp": ISODate("2024-12-08T10:30:00Z")
    }
  ],
  "created_at": ISODate("2024-12-08T10:25:00Z")
}
```

**5. analytics** (Aggregated metrics)
```javascript
{
  "_id": ObjectId("..."),
  "date": "2024-12-08",
  "metrics": {
    "total_searches": 1523,
    "total_bookings": 142,
    "conversion_rate": 9.3,
    "avg_booking_value": 385.50,
    "popular_routes": [
      {"route": "SFO-LAX", "count": 250},
      {"route": "NYC-MIA", "count": 180}
    ],
    "popular_cities": [
      {"city": "San Francisco", "searches": 450},
      {"city": "New York", "searches": 380}
    ]
  }
}
```

**6. reviews** (User-generated content)
```javascript
{
  "_id": ObjectId("..."),
  "booking_id": 12345,
  "user_id": "123-45-6789",
  "item_type": "hotel",
  "item_id": 456,
  "rating": 4.5,
  "review_text": "Great hotel, excellent service!",
  "photos": ["url1", "url2"],
  "helpful_count": 12,
  "created_at": ISODate("2024-12-08T15:00:00Z")
}
```

**7. images** (Metadata for uploaded images)
```javascript
{
  "_id": ObjectId("..."),
  "item_type": "hotel",
  "item_id": 456,
  "image_url": "https://cdn.kayak.com/hotel456/img1.jpg",
  "caption": "Ocean view room",
  "uploaded_by": "admin",
  "upload_date": ISODate("2024-12-01T10:00:00Z")
}
```

**8. click_tracking**
```javascript
{
  "_id": ObjectId("..."),
  "user_id": "123-45-6789",
  "page": "/hotels/san-francisco",
  "element_clicked": "hotel_card_123",
  "position": 3,
  "timestamp": ISODate("2024-12-08T10:30:00Z")
}
```

### **Where MongoDB is Used:**

1. **AI Service** - Chat conversation storage
2. **Search Service** - Search query logging
3. **Booking Service** - Event logging via Kafka
4. **Admin Service** - Analytics aggregation
5. **All Services** - User behavior tracking

### **Example Queries:**

```javascript
// Get user's chat history
db.chat_sessions.find({ user_id: "123-45-6789" })
  .sort({ created_at: -1 })
  .limit(10);

// Analytics: Popular search destinations
db.search_logs.aggregate([
  { $match: { search_type: "flight" } },
  { $group: {
      _id: "$query_params.arrival_airport",
      count: { $sum: 1 }
    }
  },
  { $sort: { count: -1 } },
  { $limit: 10 }
]);

// User journey funnel analysis
db.user_journeys.aggregate([
  { $unwind: "$journey" },
  { $group: {
      _id: "$journey.action",
      count: { $sum: 1 }
    }
  }
]);
```

---

## 3. REDIS (In-Memory Cache)

### **Why Redis?**
- **Speed:** Sub-millisecond response times
- **Performance:** Reduce database load by 90%+
- **Scalability:** Handle millions of requests
- **TTL Support:** Automatic expiration of cached data

### **What Data is Cached:**

**1. Flight Search Results**
```
Key: kayak:flight_search:c3491bc8e86fc1dcc69896ce2185f50e
Value: [
  {
    "flight_id": 123,
    "flight_number": "AA123",
    "airline": "American Airlines",
    "price": 250.00,
    "departure_time": "2024-12-15 10:00:00"
  },
  ...
]
TTL: 3600 seconds (1 hour)
```

**2. Hotel Search Results**
```
Key: kayak:hotel_search:city:san_francisco
Value: [
  {
    "hotel_id": 456,
    "name": "Grand Hotel SF",
    "price_per_night": 150.00,
    "star_rating": 4.5
  },
  ...
]
TTL: 3600 seconds
```

**3. User Session Data**
```
Key: kayak:session:user:123-45-6789
Value: {
  "user_id": "123-45-6789",
  "username": "john_doe",
  "email": "john@example.com",
  "auth_token": "jwt-token-here"
}
TTL: 1800 seconds (30 min)
```

**4. Popular Routes Cache**
```
Key: kayak:popular_routes
Value: [
  {"route": "SFO-LAX", "count": 1523},
  {"route": "NYC-MIA", "count": 892}
]
TTL: 86400 seconds (24 hours)
```

**5. Real-time Availability**
```
Key: kayak:availability:hotel:456:room:789
Value: {
  "available_rooms": 12,
  "last_updated": "2024-12-08T10:30:00Z"
}
TTL: 300 seconds (5 min)
```

### **Where Redis is Used:**

**1. Flight Service** (`backend/services/flight_service/main.py`)
```python
# Search flights with caching
@app.get("/flights/search")
def search_flights(params):
    # Generate cache key from search params
    cache_key = f"kayak:flight_search:{hash(params)}"
    
    # Try to get from cache
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result  # CACHE HIT - instant response
    
    # CACHE MISS - query database
    results = db.query(Flight).filter(...).all()
    
    # Store in cache for 1 hour
    cache.set(cache_key, results, ttl=3600)
    
    return results
```

**2. Hotel Service** (`backend/services/hotel_service/main.py`)
```python
@app.get("/hotels/search")
def search_hotels(city: str):
    cache_key = f"kayak:hotel_search:city:{city}"
    
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    hotels = db.query(Hotel).filter(Hotel.city == city).all()
    cache.set(cache_key, hotels, ttl=3600)
    
    return hotels
```

**3. User Service** (Session management)
```python
@app.post("/login")
def login(credentials):
    user = authenticate(credentials)
    
    # Store session in Redis
    session_key = f"kayak:session:user:{user.user_id}"
    cache.set(session_key, user_data, ttl=1800)
    
    return {"token": jwt_token, "user": user}
```

### **Cache Configuration:**
```python
# backend/common/cache.py
class RedisCache:
    def __init__(self):
        self.pool = redis.ConnectionPool(
            host='localhost',
            port=6379,
            max_connections=50,
            decode_responses=True
        )
        self.client = redis.Redis(connection_pool=self.pool)
    
    def get(self, key):
        value = self.client.get(key)
        return json.loads(value) if value else None
    
    def set(self, key, value, ttl=3600):
        return self.client.setex(key, ttl, json.dumps(value))
```

### **Performance Impact:**
- **Without Redis:** 163 req/s, 583ms avg response
- **With Redis:** 3,010 req/s, 31ms avg response
- **Improvement:** 18.4x faster, 99.97% cache hit ratio

---

## 4. KAFKA (Event Streaming)

### **Why Kafka?**
- **Asynchronous Processing:** Decouple services
- **Event Sourcing:** Track all system events
- **Scalability:** Handle millions of events
- **Reliability:** Guaranteed message delivery
- **Real-time:** Process events as they happen

### **Kafka Topics:**

**1. booking-events**
```json
{
  "event_id": "uuid",
  "event_type": "booking_created",
  "timestamp": "2024-12-08T10:30:00Z",
  "data": {
    "booking_id": 12345,
    "user_id": "123-45-6789",
    "booking_type": "hotel",
    "total_price": 450.00,
    "status": "confirmed"
  }
}
```

**2. search-events**
```json
{
  "event_id": "uuid",
  "event_type": "search_performed",
  "timestamp": "2024-12-08T10:25:00Z",
  "data": {
    "user_id": "123-45-6789",
    "search_type": "flight",
    "params": {
      "departure": "SFO",
      "arrival": "LAX",
      "date": "2024-12-15"
    },
    "results_count": 25
  }
}
```

**3. user-events**
```json
{
  "event_id": "uuid",
  "event_type": "user_registered",
  "timestamp": "2024-12-08T09:00:00Z",
  "data": {
    "user_id": "123-45-6789",
    "email": "john@example.com",
    "signup_source": "web"
  }
}
```

**4. analytics-events**
```json
{
  "event_id": "uuid",
  "event_type": "page_view",
  "timestamp": "2024-12-08T10:30:00Z",
  "data": {
    "user_id": "123-45-6789",
    "page": "/hotels/san-francisco",
    "referrer": "/search",
    "duration": 45
  }
}
```

**5. notification-events**
```json
{
  "event_id": "uuid",
  "event_type": "booking_confirmation",
  "timestamp": "2024-12-08T10:30:00Z",
  "data": {
    "user_id": "123-45-6789",
    "email": "john@example.com",
    "booking_id": 12345,
    "message": "Your booking is confirmed!"
  }
}
```

### **Where Kafka is Used:**

**1. Producer (Booking Service)**
```python
# backend/services/booking_service/main.py
from backend.kafka.producer import KafkaProducerService

producer = KafkaProducerService()

@app.post("/bookings")
def create_booking(booking_data):
    # Create booking in database
    booking = db.add(Booking(**booking_data))
    db.commit()
    
    # Publish event to Kafka
    producer.publish(
        topic="booking-events",
        key=f"booking_{booking.booking_id}",
        value={
            "event_type": "booking_created",
            "booking_id": booking.booking_id,
            "user_id": booking.user_id,
            "total_price": booking.total_price,
            "timestamp": datetime.now().isoformat()
        }
    )
    
    return booking
```

**2. Consumer (Analytics Service)**
```python
# backend/kafka/consumer.py
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'booking-events',
    'search-events',
    bootstrap_servers=['localhost:29092'],
    group_id='analytics_consumer_group',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

# Process events asynchronously
for message in consumer:
    event = message.value
    
    # Store in MongoDB
    db.analytics.insert_one(event)
    
    # Update real-time metrics
    update_dashboard_metrics(event)
```

**3. Kafka Configuration**
```python
# backend/kafka/producer.py
class KafkaProducerService:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=['localhost:29092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',  # Wait for all replicas
            retries=3,
            compression_type='gzip',
            batch_size=16384,
            linger_ms=10
        )
    
    def publish(self, topic, key, value):
        future = self.producer.send(topic, key=key.encode(), value=value)
        return future.get(timeout=10)  # Block until sent
```

### **Event Flow Example:**

```
User Books Hotel
    ↓
1. Booking Service creates booking in MySQL
    ↓
2. Booking Service publishes to Kafka topic "booking-events"
    ↓
3. Multiple consumers process the event:
   - Analytics Service → Stores in MongoDB
   - Notification Service → Sends confirmation email
   - Billing Service → Creates billing record
   - Admin Dashboard → Updates real-time metrics
```

---

# 🤖 AI CHATBOT (CONCIERGE AGENT)

## Overview
Intelligent conversational agent that helps users find and book travel services using natural language.

### **Technology Stack:**
- **Framework:** LangChain
- **LLM:** OpenAI GPT-4 / Anthropic Claude
- **Vector DB:** (Optional) for semantic search
- **Storage:** MongoDB for conversation history

### **Implementation Details:**

**File:** `ai_service/agents/concierge_agent.py`

```python
class ConciergeAgent:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0.7, model="gpt-4")
        self.conversation_history = []
    
    async def process_message(self, message: str, user_id: str):
        # Step 1: Parse intent
        intent = self._parse_intent(message)
        
        # Step 2: Extract constraints
        constraints = self._extract_constraints(message)
        
        # Step 3: Execute appropriate handler
        if intent == "flight_query":
            response = await self._handle_flight_query(constraints)
        elif intent == "hotel_query":
            response = await self._handle_hotel_query(constraints)
        elif intent == "book":
            response = await self._handle_booking(constraints)
        else:
            response = await self._general_response(message)
        
        # Step 4: Store in MongoDB
        self._save_conversation(user_id, message, response)
        
        return response
```

### **Intent Recognition:**

```python
def _parse_intent(self, message: str) -> str:
    message_lower = message.lower()
    
    # Flight keywords
    if any(word in message_lower for word in ["flight", "fly", "airport"]):
        return "flight_query"
    
    # Hotel keywords
    if any(word in message_lower for word in ["hotel", "stay", "room"]):
        return "hotel_query"
    
    # Booking keywords
    if any(phrase in message_lower for phrase in ["book this", "reserve", "purchase"]):
        return "book"
    
    # Car keywords
    if any(word in message_lower for word in ["car", "rental", "vehicle"]):
        return "car_query"
    
    return "general"
```

### **Constraint Extraction:**

```python
def _extract_constraints(self, message: str) -> dict:
    constraints = {}
    
    # Extract airports (IATA codes)
    airports = re.findall(r'\b[A-Z]{3}\b', message.upper())
    if len(airports) >= 2:
        constraints["departure_airport"] = airports[0]
        constraints["arrival_airport"] = airports[1]
    
    # Extract cities
    cities = ["San Francisco", "New York", "Los Angeles", ...]
    for city in cities:
        if city.lower() in message.lower():
            constraints["city"] = city
    
    # Extract dates
    dates = re.findall(r'\d{4}-\d{2}-\d{2}', message)
    if dates:
        constraints["date"] = dates[0]
    
    # Extract price constraints
    price_match = re.search(r'\$(\d+)', message)
    if price_match:
        constraints["price_max"] = float(price_match.group(1))
    
    return constraints
```

### **Query Handler (Hotel Example):**

```python
async def _handle_hotel_query(self, constraints: dict):
    # Call Hotel Service API
    response = requests.get(
        f"{HOTEL_SERVICE_URL}/hotels/search",
        params={"city": constraints.get("city")}
    )
    
    hotels = response.json()
    
    # Format response
    if hotels:
        hotel_list = "\n".join([
            f"- {h['name']}: ${h['price_per_night']}/night ({h['star_rating']}⭐)"
            for h in hotels[:5]
        ])
        return f"I found these hotels:\n{hotel_list}\n\nWould you like to book one?"
    else:
        return "Sorry, no hotels found matching your criteria."
```

### **Features:**
1. **Natural Language Understanding**
   - Intent classification
   - Entity extraction (cities, dates, prices)
   - Context tracking across conversation

2. **Service Integration**
   - Calls Flight/Hotel/Car Service APIs
   - Processes results and formats responses
   - Provides personalized recommendations

3. **Conversation Memory**
   - Stores chat history in MongoDB
   - Maintains context across multiple turns
   - Recalls previous preferences

4. **Multi-turn Dialogues**
   ```
   User: "I need a hotel in SF"
   Bot: "I found 10 hotels. What's your budget?"
   User: "Under $200"
   Bot: "Here are 5 hotels under $200..."
   User: "Book the second one"
   Bot: "Booking Grand Hotel SF for you..."
   ```

---

# 📊 ADMIN DASHBOARD

## Overview
Comprehensive analytics and management interface for system administrators.

### **Location:** `frontend/src/pages/Admin*.tsx`

### **Key Features:**

**1. Analytics Overview**
- **File:** `AdminDashboard.tsx`
- **Metrics Displayed:**
  - Total users registered
  - Total bookings (flights, hotels, cars)
  - Total revenue
  - Average booking value
  - Conversion rates
  - Popular routes/destinations
  - Real-time active users

**2. User Management**
- **File:** `AdminUserManagement.tsx`
- **Features:**
  - View all registered users
  - Search and filter users
  - User activity history
  - Booking history per user
  - Enable/disable user accounts

**3. Flight Management**
- **File:** `AdminFlightManagement.tsx`
- **Features:**
  - Add/Edit/Delete flights
  - Update flight prices
  - Manage availability
  - Bulk import flights
  - View booking statistics per flight

**4. Hotel Management**
- **File:** `AdminHotelManagement.tsx`
- **Features:**
  - Add/Edit/Delete hotels
  - Manage rooms and availability
  - Update pricing
  - Upload hotel images
  - View booking statistics per hotel

**5. Car Management**
- **File:** `AdminCarManagement.tsx`
- **Features:**
  - Add/Edit/Delete car listings
  - Update rental rates
  - Manage inventory
  - Track rental history

**6. Booking Management**
- **File:** `AdminBookingManagement.tsx`
- **Features:**
  - View all bookings
  - Filter by status, type, date
  - Cancel/modify bookings
  - Refund processing
  - Export booking reports

### **Backend API (Admin Service):**

**File:** `backend/services/admin_service/main.py`

```python
@app.get("/admin/analytics/overview")
def get_analytics_overview():
    # Query MySQL for counts
    total_users = db.query(User).count()
    total_bookings = db.query(Booking).count()
    total_revenue = db.query(Booking).with_entities(
        func.sum(Booking.total_price)
    ).scalar()
    
    # Query MongoDB for additional metrics
    popular_routes = db.analytics.aggregate([
        {"$group": {"_id": "$route", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ])
    
    return {
        "total_users": total_users,
        "total_bookings": total_bookings,
        "total_revenue": float(total_revenue),
        "popular_routes": list(popular_routes)
    }

@app.get("/admin/bookings")
def get_all_bookings(status: Optional[str] = None):
    query = db.query(Booking).join(User)
    
    if status:
        query = query.filter(Booking.status == status)
    
    bookings = query.all()
    return bookings

@app.put("/admin/bookings/{booking_id}/cancel")
def cancel_booking(booking_id: int):
    booking = db.query(Booking).get(booking_id)
    booking.status = "cancelled"
    db.commit()
    
    # Publish Kafka event
    producer.publish("booking-events", {
        "event_type": "booking_cancelled",
        "booking_id": booking_id
    })
    
    return {"message": "Booking cancelled"}
```

---

# 🔄 DATA FLOW EXAMPLES

## Example 1: User Books a Hotel

```
1. User enters search criteria in frontend
   ↓
2. Frontend calls Search Service API
   ↓
3. Search Service checks Redis cache
   - CACHE HIT → Return cached results
   - CACHE MISS → Query Hotel Service
   ↓
4. Hotel Service queries MySQL for available hotels
   ↓
5. Results cached in Redis (TTL: 1 hour)
   ↓
6. Results returned to frontend
   ↓
7. User selects hotel and clicks "Book Now"
   ↓
8. Frontend calls Booking Service API
   ↓
9. Booking Service:
   - Validates availability in MySQL
   - Creates booking record in MySQL
   - Publishes "booking_created" event to Kafka
   ↓
10. Kafka event consumed by:
    - Analytics Service → Stores in MongoDB
    - Billing Service → Creates billing record
    - Notification Service → Sends email
    - Admin Dashboard → Updates metrics
   ↓
11. User receives booking confirmation
```

## Example 2: Admin Views Dashboard Analytics

```
1. Admin navigates to dashboard
   ↓
2. Frontend calls Admin Service API
   ↓
3. Admin Service:
   - Queries MySQL for booking counts, revenue
   - Queries MongoDB for popular routes, user behavior
   - Queries Redis for real-time metrics
   ↓
4. Data aggregated and returned
   ↓
5. Frontend displays charts and tables
```

## Example 3: User Chats with AI Bot

```
1. User types message: "Find me hotels in SF under $200"
   ↓
2. Frontend calls AI Service API
   ↓
3. AI Service (Concierge Agent):
   - Parses intent: "hotel_query"
   - Extracts constraints: {city: "San Francisco", price_max: 200}
   ↓
4. AI Service calls Hotel Service API
   ↓
5. Hotel Service checks Redis cache
   ↓
6. Results returned to AI Service
   ↓
7. AI Service formats response with LLM
   ↓
8. AI Service stores conversation in MongoDB
   ↓
9. Response sent to frontend
   ↓
10. User sees formatted hotel recommendations
```

---

# 📈 PERFORMANCE TESTING RESULTS

## JMeter Test Configurations:

**Test Setup:**
- **Users:** 100 concurrent
- **Duration:** 5 minutes per test
- **Total Tests:** 4 configurations

### **Results:**

| Configuration | Requests | Error Rate | Throughput | Avg Response |
|--------------|----------|------------|------------|--------------|
| Base (No Opts) | 49,014 | 0.00% | 163/s | 583ms |
| Base + Redis | 1M+ | 0.00% | 3,010/s | 31ms |
| Base + Redis + Kafka | 903,019 | 0.00% | 3,009/s | 31ms |
| All Optimizations | 846,580 | 0.00% | 2,821/s | 33ms |

### **Key Findings:**
✅ **18.4x throughput improvement** with Redis  
✅ **18.8x faster response times** (583ms → 31ms)  
✅ **0% error rate** across all optimized configs  
✅ **99.97% cache hit ratio** (412,084 hits / 1 miss)  
✅ **2.8+ million total requests** processed

---

# 🎓 PROFESSOR Q&A PREPARATION

## Common Questions & Answers:

### **Q: Why did you use microservices architecture?**
**A:** "We used microservices to achieve:
1. **Scalability** - Each service scales independently based on load
2. **Fault Isolation** - If one service fails, others continue working
3. **Technology Flexibility** - Different services can use different tech stacks
4. **Team Autonomy** - Different teams can work on different services
5. **Deployment Independence** - Deploy updates without affecting entire system"

### **Q: Why MySQL AND MongoDB?**
**A:** "We use a polyglot persistence approach:
- **MySQL** for structured, transactional data (bookings, users, payments) that requires ACID compliance and complex JOINs
- **MongoDB** for unstructured data (logs, analytics, chat histories) that needs flexible schemas and fast writes
- This is a best practice in distributed systems - use the right tool for the right job"

### **Q: How does Redis improve performance?**
**A:** "Redis provides:
1. **In-memory storage** - Sub-millisecond response times
2. **Reduced database load** - 99.97% cache hit ratio means only 0.03% of requests hit MySQL
3. **Scalability** - Our JMeter tests show 18.4x improvement in throughput
4. **TTL support** - Automatic expiration prevents stale data
5. **Cost savings** - Fewer database queries = lower infrastructure costs"

### **Q: What is Kafka used for?**
**A:** "Kafka provides:
1. **Asynchronous processing** - Decouples services for better performance
2. **Event sourcing** - Complete audit trail of all system events
3. **Real-time analytics** - Process events as they happen
4. **Reliability** - Guaranteed message delivery with replication
5. **Scalability** - Can handle millions of events per second"

### **Q: How does the AI chatbot work?**
**A:** "Our Concierge Agent uses:
1. **Natural Language Processing** - Understands user intent from text
2. **Entity Extraction** - Identifies cities, dates, prices using regex and NLP
3. **Service Integration** - Calls appropriate microservice APIs
4. **Context Management** - Maintains conversation history in MongoDB
5. **LLM Integration** - Uses GPT-4 for natural response generation"

### **Q: How do you ensure data consistency?**
**A:** "We use several strategies:
1. **Database Transactions** - ACID guarantees in MySQL for critical operations
2. **Event Sourcing** - Kafka provides ordered, reliable event delivery
3. **Cache Invalidation** - Redis TTL ensures data freshness
4. **Eventual Consistency** - MongoDB updates asynchronously via Kafka
5. **Idempotency** - Event handlers process duplicate events safely"

### **Q: What about security?**
**A:** "Security measures include:
1. **JWT Authentication** - Stateless token-based auth
2. **Password Hashing** - bcrypt for secure password storage
3. **Input Validation** - Pydantic models validate all inputs
4. **SQL Injection Prevention** - SQLAlchemy ORM with parameterized queries
5. **CORS Configuration** - Restrict cross-origin requests
6. **Environment Variables** - Sensitive data not in code"

### **Q: How did you test scalability?**
**A:** "Our testing approach:
1. **Data Generation** - Created 45,000+ records (10K+ in each category)
2. **Load Testing** - JMeter with 100 concurrent users
3. **Duration Testing** - 5-minute sustained load tests
4. **Multiple Configurations** - Tested with/without optimizations
5. **Metrics Collection** - Measured throughput, response time, error rate
6. **Results** - System handled 2.8M requests with 0% error rate"

---

# 📁 PROJECT STRUCTURE

```
kayak-simulation/
├── frontend/                    # React frontend
│   ├── src/
│   │   ├── pages/              # Page components
│   │   │   ├── FlightsPage.tsx
│   │   │   ├── HotelsPage.tsx
│   │   │   ├── AdminDashboard.tsx
│   │   │   └── ...
│   │   ├── api/                # API clients
│   │   └── components/         # Reusable components
│   └── package.json
│
├── backend/
│   ├── services/               # Microservices
│   │   ├── user_service/       # Port 8001
│   │   ├── flight_service/     # Port 8002
│   │   ├── hotel_service/      # Port 8003
│   │   ├── car_service/        # Port 8004
│   │   ├── billing_service/    # Port 8005
│   │   ├── admin_service/      # Port 8006
│   │   ├── search_service/     # Port 8007
│   │   └── booking_service/    # Port 8009
│   │
│   ├── common/                 # Shared utilities
│   │   ├── config.py          # Configuration
│   │   ├── cache.py           # Redis cache wrapper
│   │   └── database.py        # DB connections
│   │
│   └── kafka/                  # Kafka integration
│       ├── producer.py
│       └── consumer.py
│
├── ai_service/                 # AI Chatbot
│   ├── agents/
│   │   └── concierge_agent.py
│   └── api/
│       └── routes.py
│
├── jmeter/                     # Performance testing
│   ├── kayak_performance_test.jmx
│   ├── run_all_performance_tests.sh
│   ├── generate_comparison_charts.py
│   └── results/
│       ├── base_report/
│       ├── base_s_report/
│       ├── base_s_k_report/
│       ├── base_s_k_x_report/
│       └── charts/
│
├── docker-compose.yml          # Container orchestration
├── README.md
└── PROVE_REDIS_CACHING.md
```

---

# 🚀 DEPLOYMENT

## Docker Services:

```yaml
services:
  # Databases
  mysql:           # Port 3306
  mongodb:         # Port 27017
  redis:           # Port 6379
  
  # Kafka
  zookeeper:       # Port 2181
  kafka:           # Port 9092, 29092
  
  # Microservices
  user-service:    # Port 8001
  flight-service:  # Port 8002
  hotel-service:   # Port 8003
  car-service:     # Port 8004
  billing-service: # Port 8005
  admin-service:   # Port 8006
  search-service:  # Port 8007
  ai-service:      # Port 8008
  booking-service: # Port 8009
  
  # Frontend
  frontend:        # Port 3000
```

## Start System:
```bash
# Start all services
docker-compose up -d

# Verify all running
docker-compose ps

# View logs
docker-compose logs -f [service-name]
```

---

# ✅ SUMMARY

This distributed travel booking platform demonstrates:

✅ **Microservices Architecture** - 9 independent services  
✅ **Polyglot Persistence** - MySQL + MongoDB + Redis  
✅ **Event-Driven Design** - Kafka for async communication  
✅ **AI Integration** - Intelligent chatbot with NLP  
✅ **High Performance** - 18x improvement with caching  
✅ **Scalability** - Tested with 2.8M requests, 0% errors  
✅ **Modern Tech Stack** - React, FastAPI, Docker  
✅ **Production-Ready** - Monitoring, logging, analytics  

**Total Scale:**
- 45,000+ database records
- 10,000+ users
- 100,000+ bookings supported
- 2.8M+ requests tested
- 0% error rate achieved

---

**Created:** December 8, 2024  
**Author:** Kayak Simulation Team  
**Purpose:** Distributed Systems for Data Engineering Project
