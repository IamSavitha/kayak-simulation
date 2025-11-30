# Team 2 - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites Check
- [ ] Python 3.11+ installed
- [ ] MySQL 8.0+ running
- [ ] MongoDB 7.0+ running
- [ ] Redis 7+ running
- [ ] Kafka running (or use docker-compose)

### Step 1: Install Dependencies
```bash
cd team2
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
cp .env.example .env
# Edit .env with your database credentials
```

### Step 3: Setup Database
```bash
# Run all DDL scripts
mysql -u root -p < database/ddl/flights.sql
mysql -u root -p < database/ddl/hotels.sql
mysql -u root -p < database/ddl/cars.sql
mysql -u root -p < database/ddl/indexes.sql
```

### Step 4: Run Service

**Option A: Docker Compose (Recommended)**
```bash
docker-compose up -d
```

**Option B: Local Development**
```bash
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

### Step 5: Seed Data (Optional)
```bash
python scripts/seed_data.py
```

### Step 6: Test API
- Open browser: http://localhost:8002/docs
- Try creating a flight: `POST /flights`
- Try searching: `GET /flights/search?origin=JFK&destination=LAX`

---

## 📋 What You Need From Other Teams

### From Team 5 (Kafka & Redis) - ⚠️ REQUIRED
**Action:** Update `.env` file with:
```
KAFKA_BOOTSTRAP_SERVERS=<team5_kafka_address>:9092
REDIS_HOST=<team5_redis_host>
REDIS_PORT=<team5_redis_port>
```

### From Team 3 (Booking) - ⚠️ REQUIRED
**Action:** Coordinate on:
- Availability update flow when bookings are created/cancelled
- Error handling for failed availability updates

### From Team 1 (User/Admin) - 📝 IMPORTANT
**Action:** Share API documentation and coordinate on:
- Search request format (if different from ours)
- Admin listing management integration

---

## 🧪 Run Tests
```bash
pytest tests/
```

## 📚 Documentation
- **API Docs**: `API_DOCUMENTATION.md`
- **Dependencies**: `TEAM_DEPENDENCIES.md`
- **ER Diagram**: `database/ER_DIAGRAM.md`
- **Full README**: `README.md`

---

## ✅ Verification Checklist

After setup, verify:
- [ ] Service starts without errors
- [ ] Can access `/docs` endpoint
- [ ] Can create a flight via API
- [ ] Can search flights
- [ ] Redis connection works (check logs)
- [ ] Kafka connection works (check logs, if Team 5 is ready)

---

## 🆘 Troubleshooting

**Issue: Cannot connect to MySQL**
- Check MySQL is running: `mysql -u root -p`
- Verify credentials in `.env`
- Check MySQL port (default 3306)

**Issue: Cannot connect to MongoDB**
- Check MongoDB is running: `mongosh`
- Verify MongoDB port (default 27017)

**Issue: Cannot connect to Redis**
- Check Redis is running: `redis-cli ping`
- Should return `PONG`

**Issue: Kafka connection fails**
- This is expected if Team 5 hasn't set up Kafka yet
- Service will still work, but events won't be published
- Update `.env` once Team 5 provides Kafka address

---

## 📞 Need Help?

1. Check `TEAM_DEPENDENCIES.md` for integration requirements
2. Check `API_DOCUMENTATION.md` for API details
3. Check logs for error messages
4. Contact Team 5 for Kafka/Redis setup

