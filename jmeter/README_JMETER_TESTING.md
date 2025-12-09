# JMeter Performance Testing - Kayak Project

## Overview
This guide will help you perform load testing with 100 concurrent users across 4 configurations:
- **B**: Base (No optimizations)
- **B+S**: Base + SQL Caching (Redis)
- **B+S+K**: Base + SQL Caching + Kafka
- **B+S+K+X**: All optimizations + Additional techniques

Target: **Less than 5% error rate** with 100 simultaneous users

---

## Prerequisites

### 1. Install JMeter
```bash
# macOS
brew install jmeter

# Or download from: https://jmeter.apache.org/download_jmeter.cgi
```

### 2. Verify Installation
```bash
jmeter --version
# Should show: Apache JMeter 5.x
```

### 3. Populate Database
Ensure you have **at least 10,000 records** in your database:
- 10,000+ users
- 10,000+ flights
- 10,000+ hotels
- 10,000+ cars
- Sample bookings and billing records

---

## Test Configurations

### Configuration 1: Base (B)
**What to disable:**
- Turn OFF Redis caching
- Turn OFF Kafka (use direct REST calls)
- Disable any other optimizations

**docker-compose changes:**
```yaml
# Comment out or remove:
# - redis
# - kafka
# - zookeeper

# Update services to NOT use Redis/Kafka
```

### Configuration 2: Base + SQL Caching (B+S)
**What to enable:**
- Turn ON Redis caching
- Keep Kafka OFF

**Verify Redis is working:**
```bash
docker-compose exec redis redis-cli
> KEYS *
> INFO stats
```

### Configuration 3: Base + SQL + Kafka (B+S+K)
**What to enable:**
- Redis caching ON
- Kafka ON
- All services using Kafka for async operations

**Verify Kafka:**
```bash
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092
```

### Configuration 4: All Optimizations (B+S+K+X)
**Enable everything:**
- Redis caching
- Kafka
- Connection pooling
- Database indexing
- Query optimization
- Async processing
- Load balancing (if implemented)

---

## JMeter Test Plan Structure

### Test Scenarios (100 concurrent users)

#### Scenario 1: User Operations (20% load)
- Sign up new users
- Login
- Update profile
- View profile

#### Scenario 2: Search Operations (40% load)
- Search flights
- Search hotels
- Search cars
- Filter results

#### Scenario 3: Booking Operations (30% load)
- Create flight booking
- Create hotel booking
- Create car booking
- View bookings

#### Scenario 4: Admin Operations (10% load)
- View dashboard
- Manage listings
- View analytics

---

## Running Tests

### Step 1: Prepare for Each Configuration

#### For Base (B):
```bash
# Stop Redis and Kafka
docker-compose stop redis kafka zookeeper

# Restart services
docker-compose restart user-service flight-service hotel-service car-service booking-service
```

#### For B+S:
```bash
# Start Redis, keep Kafka off
docker-compose start redis
docker-compose stop kafka zookeeper

# Flush Redis cache
docker-compose exec redis redis-cli FLUSHDB

# Restart services
docker-compose restart user-service flight-service hotel-service car-service booking-service
```

#### For B+S+K:
```bash
# Start everything
docker-compose up -d

# Flush Redis
docker-compose exec redis redis-cli FLUSHDB

# Restart all services
docker-compose restart
```

#### For B+S+K+X:
```bash
# Ensure all optimizations are enabled in code
# Start everything
docker-compose up -d
```

### Step 2: Run JMeter Test
```bash
# GUI Mode (for setup/debugging)
jmeter -t kayak_performance_test.jmx

# CLI Mode (for actual testing)
jmeter -n -t kayak_performance_test.jmx -l results/base_results.jtl -e -o results/base_report

# For each configuration:
jmeter -n -t kayak_performance_test.jmx -l results/base_s_results.jtl -e -o results/base_s_report
jmeter -n -t kayak_performance_test.jmx -l results/base_s_k_results.jtl -e -o results/base_s_k_report
jmeter -n -t kayak_performance_test.jmx -l results/base_s_k_x_results.jtl -e -o results/base_s_k_x_report
```

### Step 3: Wait and Collect Results
Each test will take approximately:
- Ramp-up: 30 seconds (100 users)
- Test duration: 5 minutes
- Ramp-down: 10 seconds
- Total: ~6 minutes per configuration

---

## Success Criteria

### Target Metrics

| Metric | Target | Notes |
|--------|--------|-------|
| **Error Rate** | < 5% | MUST be below 5% |
| **Response Time (Avg)** | < 2 seconds | For 90% of requests |
| **Response Time (95th)** | < 5 seconds | 95th percentile |
| **Throughput** | > 500 req/min | Minimum |
| **CPU Usage** | < 80% | Server-side |
| **Memory Usage** | < 4GB | Per service |

### Expected Improvements

| Configuration | Expected Error Rate | Expected Avg Response Time |
|---------------|-------------------|---------------------------|
| B (Base) | 10-15% | 3-5 seconds |
| B+S (+ Redis) | 5-8% | 1.5-3 seconds |
| B+S+K (+ Kafka) | 2-5% | 1-2 seconds |
| B+S+K+X (All) | < 2% | < 1 second |

---

## Analyzing Results

### Key Metrics to Extract

1. **Total Requests**
2. **Error %**
3. **Average Response Time**
4. **95th Percentile Response Time**
5. **Throughput (requests/second)**
6. **Min/Max Response Times**

### Generate Comparison Graphs

JMeter automatically generates HTML reports. Key graphs:
- Response Time Over Time
- Throughput Over Time
- Error Rate Over Time
- Response Time Percentiles

### Create Bar Charts

Extract data for your presentation:

```
Configuration | Avg Response Time (ms) | Error Rate (%) | Throughput (req/s)
-------------|------------------------|----------------|-------------------
B            | XXXX                   | XX.XX          | XXX.XX
B+S          | XXXX                   | XX.XX          | XXX.XX
B+S+K        | XXXX                   | XX.XX          | XXX.XX
B+S+K+X      | XXXX                   | XX.XX          | XXX.XX
```

---

## Troubleshooting

### Error Rate > 5%

**Common Causes:**
1. **Database connection pool exhausted**
   - Increase pool size in services
   - Add connection timeouts

2. **Service timeouts**
   - Increase request timeout values
   - Add retry logic

3. **Resource exhaustion (CPU/Memory)**
   - Scale services horizontally
   - Add caching

4. **Database locks/deadlocks**
   - Review transaction isolation levels
   - Add proper indexing

### How to Fix

#### Increase Database Connections
```python
# In database config
SQLALCHEMY_POOL_SIZE = 50
SQLALCHEMY_MAX_OVERFLOW = 100
SQLALCHEMY_POOL_TIMEOUT = 30
```

#### Add Redis Caching
```python
# Cache frequently accessed data
@cache.memoize(timeout=300)
def get_flight(flight_id):
    return db.query(Flight).filter_by(flight_id=flight_id).first()
```

#### Use Kafka for Async Operations
```python
# For non-critical operations
await kafka_producer.send('email-notifications', email_data)
# Don't wait for response
```

---

## Tips for Success

### 1. Gradual Load Testing
Start with fewer users and increase:
- 10 users
- 25 users
- 50 users
- 100 users

### 2. Monitor Resources
```bash
# Watch Docker stats
docker stats

# Watch individual service logs
docker-compose logs -f user-service
```

### 3. Database Optimization
```sql
-- Add indexes on frequently queried columns
CREATE INDEX idx_flights_route ON flights(departure_airport, arrival_airport);
CREATE INDEX idx_bookings_user ON bookings(user_id);
CREATE INDEX idx_hotels_city ON hotels(city);
```

### 4. Clear Cache Between Tests
```bash
# Flush Redis
docker-compose exec redis redis-cli FLUSHDB

# Restart services
docker-compose restart
```

---

## Deliverables for Presentation

1. **4 Bar Charts** showing:
   - Average Response Time comparison
   - Error Rate comparison
   - Throughput comparison
   - 95th Percentile Response Time

2. **Performance Analysis**:
   - Explain why each optimization improved performance
   - Show specific bottlenecks identified
   - Demonstrate cache hit rates from Redis

3. **Screenshots**:
   - JMeter test configuration
   - JMeter results summary
   - Generated HTML reports

---

## Quick Start Commands

```bash
# 1. Setup
cd /Users/sujithdugyala/Desktop/DSGP\ 2/jmeter

# 2. Run all tests (this will take ~30 minutes total)
./run_all_performance_tests.sh

# 3. View results
open results/base_report/index.html
open results/base_s_report/index.html
open results/base_s_k_report/index.html
open results/base_s_k_x_report/index.html

# 4. Generate comparison CSV
python generate_comparison_charts.py
```

---

## Sample Output

```
=== Performance Test Results ===

Configuration: B (Base)
- Total Requests: 50,000
- Error Rate: 12.3%  ❌ (Target: <5%)
- Avg Response Time: 3,245 ms
- Throughput: 165 req/s

Configuration: B+S (+ Redis)
- Total Requests: 50,000
- Error Rate: 6.8%  ⚠️ (Close to target)
- Avg Response Time: 1,823 ms
- Throughput: 274 req/s

Configuration: B+S+K (+ Kafka)
- Total Requests: 50,000
- Error Rate: 3.2%  ✅ (Below target!)
- Avg Response Time: 1,105 ms
- Throughput: 453 req/s

Configuration: B+S+K+X (All Optimizations)
- Total Requests: 50,000
- Error Rate: 1.4%  ✅✅ (Excellent!)
- Avg Response Time: 672 ms
- Throughput: 746 req/s
```

---

## Next Steps

See the following files:
1. `kayak_performance_test.jmx` - Main JMeter test plan
2. `run_all_performance_tests.sh` - Automated test runner
3. `generate_comparison_charts.py` - Create presentation charts
4. `test_data_generator.py` - Populate 10,000 records
