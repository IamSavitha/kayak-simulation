# ⚡ QUICK REFERENCE GUIDE - KAYAK PROJECT

One-page cheat sheet for instant answers during your presentation.

---

## 🗄️ DATABASES AT A GLANCE

### **MySQL** (Port 3306)
**What:** Relational database for structured, transactional data  
**Where:** `backend/common/database.py`, all services  
**Why:** ACID compliance, foreign keys, JOINs  

**Tables:**
- `users` (10K+) - SSN IDs, auth, profiles
- `flights` (10K+) - IATA codes, schedules, prices
- `hotels` (5K+) - locations, ratings, amenities
- `rooms` (15K+) - FK to hotels, availability
- `cars` (10K+) - rental inventory
- `bookings` (100K+) - transactions
- `billing` - payments, transaction IDs

**Example:**
```sql
SELECT b.*, u.email FROM bookings b 
JOIN users u ON b.user_id = u.user_id 
WHERE status = 'confirmed';
```

---

### **MongoDB** (Port 27017)
**What:** Document database for unstructured, flexible data  
**Where:** `ai_service`, `admin_service`, Kafka consumers  
**Why:** Flexible schemas, fast writes, nested JSON  

**Collections:**
- `chat_sessions` - AI conversations with context
- `search_logs` - User search behavior
- `booking_logs` - Kafka events stored
- `analytics` - Aggregated metrics
- `reviews` - User-generated content
- `user_journeys` - Behavior tracking

**Example:**
```javascript
db.chat_sessions.find({user_id: "123-45-6789"})
  .sort({created_at: -1}).limit(10);
```

---

### **Redis** (Port 6379)
**What:** In-memory cache for sub-millisecond performance  
**Where:** All search services, user sessions  
**Why:** 291x faster than MySQL, 99.97% hit ratio  

**Cached Data:**
- Flight searches: `kayak:flight_search:{route}:{date}`
- Hotel searches: `kayak:hotel_search:city:{city}`
- User sessions: `kayak:session:user:{user_id}`
- Availability: `kayak:availability:{type}:{id}`

**Performance:**
- Without: 163 req/s, 583ms
- With: 3,010 req/s, 31ms
- **18.4x improvement**

**Commands:**
```bash
docker exec redis redis-cli
KEYS kayak:*
INFO stats
GET kayak:flight_search:SFO:LAX:2024-12-15
```

---

### **Kafka** (Port 29092)
**What:** Event streaming for async processing  
**Where:** `backend/kafka/`, all services publish/consume  
**Why:** Decouple services, 7x faster user response  

**Topics:**
- `booking-events` - Created/cancelled bookings
- `search-events` - Search tracking
- `user-events` - Registration/login
- `analytics-events` - Page views, clicks
- `notification-events` - Email queue

**Flow:**
```
Booking Service → Kafka → [Billing, Analytics, Notification]
Async, parallel, no blocking
```

**Commands:**
```bash
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092
docker exec kafka kafka-console-consumer --topic booking-events
```

---

## 🤖 AI CHATBOT

**File:** `ai_service/agents/concierge_agent.py`  
**Tech:** LangChain, OpenAI GPT-4, NLP  
**Storage:** MongoDB `chat_sessions`  

**Pipeline:**
1. **Intent Classification** - Flight? Hotel? Booking?
2. **Entity Extraction** - Cities, dates, prices
3. **API Integration** - Call microservices
4. **Response Generation** - Natural language
5. **Context Storage** - MongoDB for memory

**Example:**
```python
# User: "Hotels in SF under $200"
intent = "hotel_query"
constraints = {city: "SF", price_max: 200}
results = hotel_service.search(constraints)
response = format_results(results)
save_to_mongodb(conversation)
```

**Features:**
- Multi-turn conversations
- Context tracking across messages
- Regex + keyword matching
- LLM for natural responses

---

## 📊 ADMIN DASHBOARD

**Files:** `frontend/src/pages/Admin*.tsx`  
**Backend:** `admin_service/main.py`  

**Metrics:**
- Total users, bookings, revenue
- Conversion rates (searches → bookings)
- Popular routes/destinations
- Real-time system health

**Data Sources:**
- MySQL: Bookings count, revenue
- MongoDB: Search analytics
- Redis: Real-time stats
- Kafka: Event processing lag

**Query Example:**
```sql
SELECT booking_type, SUM(total_price) 
FROM bookings WHERE status = 'confirmed' 
GROUP BY booking_type;
```

---

## 🏗️ MICROSERVICES

**9 Independent Services:**

| Service | Port | Database | Purpose |
|---------|------|----------|---------|
| User | 8001 | MySQL | Auth, profiles |
| Flight | 8002 | MySQL + Redis | Flight search |
| Hotel | 8003 | MySQL + Redis | Hotel search |
| Car | 8004 | MySQL + Redis | Car rentals |
| Billing | 8005 | MySQL | Payments |
| Admin | 8006 | MySQL + MongoDB | Analytics |
| Search | 8007 | All | Unified search |
| AI | 8008 | MongoDB | Chatbot |
| Booking | 8009 | MySQL + Kafka | Orchestration |

**Each Service:**
- FastAPI Python backend
- Docker container
- Independent scaling
- REST API + Kafka events

---

## 📈 PERFORMANCE TESTING

**Setup:**
- Tool: Apache JMeter
- Users: 100 concurrent
- Duration: 5 min per config
- Scenarios: Search, book, admin ops

**Results:**

| Config | Req/s | Avg Time | Error % |
|--------|-------|----------|---------|
| Base | 163 | 583ms | 0.00% |
| +Redis | 3,010 | 31ms | 0.00% |
| +Kafka | 3,009 | 31ms | 0.00% |
| All Opts | 2,821 | 33ms | 0.00% |

**Total:** 2.8M+ requests, 0 errors

**Cache Stats:**
- Hits: 412,084
- Misses: 1
- Hit Ratio: 99.97%

---

## 🔑 KEY CODE LOCATIONS

**Redis Caching:**
```
backend/common/cache.py - RedisCache class
backend/services/flight_service/main.py - Usage
```

**Kafka:**
```
backend/kafka/producer.py - Publishing
backend/kafka/consumer.py - Consuming
```

**AI Chatbot:**
```
ai_service/agents/concierge_agent.py - Main logic
ai_service/api/routes.py - Endpoints
```

**Database:**
```
backend/common/database.py - MySQL connection
backend/common/config.py - All settings
```

**Docker:**
```
docker-compose.yml - All services
```

---

## 💬 QUICK ANSWERS

**Q: Why microservices?**  
A: Independent scaling, fault isolation, tech flexibility

**Q: Why MySQL AND MongoDB?**  
A: Polyglot persistence - right tool for job

**Q: How does Redis help?**  
A: 18x faster, 99.97% cache hit ratio

**Q: What does Kafka do?**  
A: Async events, decoupling, 7x faster responses

**Q: How does AI work?**  
A: NLP pipeline: intent → entities → API → response

**Q: Data consistency?**  
A: MySQL transactions (strong), Kafka (eventual)

**Q: Security?**  
A: JWT auth, bcrypt, SQL injection prevention, rate limiting

**Q: Scaling?**  
A: Horizontal scaling, sharding, Redis cluster, Kafka partitions

---

## 📊 DEMO COMMANDS

**Check All Services:**
```bash
docker-compose ps
```

**Redis Cache:**
```bash
docker exec redis redis-cli
> KEYS kayak:*
> INFO stats
> GET kayak:flight_search:SFO:LAX:2024-12-15
```

**MongoDB:**
```bash
docker exec -it mongodb mongosh -u admin -p kayak_mongo_pass
> use kayak_db
> db.chat_sessions.find().limit(3).pretty()
> db.search_logs.countDocuments()
```

**MySQL:**
```bash
docker exec -it mysql mysql -u kayak_user -pkayak_pass
> USE kayak_db;
> SELECT COUNT(*) FROM bookings;
> SELECT * FROM users LIMIT 3;
```

**Kafka:**
```bash
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092
docker exec kafka kafka-console-consumer --topic booking-events --from-beginning --max-messages 5
```

**JMeter Reports:**
```bash
open jmeter/results/base_s_k_x_report/index.html
```

---

## 🎯 PROJECT STATS

**Scale:**
- 45,000+ database records
- 10,000+ users, flights, hotels, cars
- 9 microservices
- 4 database technologies

**Performance:**
- 2.8M+ requests tested
- 0% error rate
- 18x throughput improvement
- <100ms response time

**Tech Stack:**
- React + TypeScript
- Python FastAPI
- Docker + docker-compose
- MySQL, MongoDB, Redis, Kafka

---

## 🚀 START SYSTEM

```bash
cd /Users/sujithdugyala/Desktop/DSGP\ 2
docker-compose up -d
docker-compose ps  # Verify all running
```

**Access:**
- Frontend: http://localhost:3000
- Admin: http://localhost:3000/admin
- Services: http://localhost:800X

---

**YOU'RE READY! 🎉**
