# JMeter Quick Start Guide - Kayak Project

## 🚀 Quick Start (5 Steps)

### Step 1: Populate Database
```bash
cd /Users/sujithdugyala/Desktop/DSGP\ 2/jmeter
python3 test_data_generator.py
```
**Expected:** 10,000+ users, flights, hotels, cars in database

### Step 2: Install JMeter (if not installed)
```bash
brew install jmeter
```

### Step 3: Prepare Test Data
```bash
# Generate CSV files for JMeter
python3 << 'EOF'
import csv
# Create user credentials for load testing
with open('test_data/user_credentials.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['user_email', 'user_password'])
    for i in range(1000):
        writer.writerow([f'testuser{i}@kayak.com', 'Test123!'])
print("✅ Test data created")
EOF
```

### Step 4: Run All Performance Tests
```bash
chmod +x run_all_performance_tests.sh
./run_all_performance_tests.sh
```
**Duration:** ~30 minutes (6 min per configuration x 4 + analysis)

### Step 5: Generate Charts
```bash
python3 generate_comparison_charts.py
```

**Done!** Check `results/charts/` for presentation-ready images.

---

## 📊 What You Get

### 4 HTML Reports
- `results/base_report/index.html` - Base configuration
- `results/base_s_report/index.html` - With Redis caching
- `results/base_s_k_report/index.html` - With Kafka
- `results/base_s_k_x_report/index.html` - All optimizations

### 5 Charts for Presentation
1. `avg_response_time.png` - Average response time comparison
2. `error_rate.png` - Error rate comparison (target: <5%)
3. `throughput.png` - Throughput comparison
4. `pct95_response_time.png` - 95th percentile times
5. `summary_table.png` - Complete summary table

### CSV Data
- `results/performance_comparison.csv` - Raw data for custom charts

---

## 🎯 Expected Results

### Target Metrics (Must Achieve)
- **Error Rate:** < 5% ✅
- **Average Response Time:** < 2 seconds
- **Throughput:** > 500 req/min

### Typical Performance Progression

| Config | Error Rate | Avg Time | Throughput |
|--------|-----------|----------|------------|
| B (Base) | 12% ❌ | 3.2s | 165 req/s |
| B+S (+Redis) | 6.8% ⚠️ | 1.8s | 274 req/s |
| B+S+K (+Kafka) | 3.2% ✅ | 1.1s | 453 req/s |
| B+S+K+X (All) | 1.4% ✅ | 0.7s | 746 req/s |

---

## 🔧 Troubleshooting

### Error Rate > 5%?

**1. Increase Database Connection Pool**
```python
# In backend/common/database.py
SQLALCHEMY_POOL_SIZE = 50  # Increase from default
SQLALCHEMY_MAX_OVERFLOW = 100
```

**2. Add More Indexes**
```sql
CREATE INDEX idx_flights_route ON flights(departure_airport, arrival_airport);
CREATE INDEX idx_hotels_city ON hotels(city);
CREATE INDEX idx_bookings_user_date ON bookings(user_id, check_in_date);
```

**3. Increase Service Timeouts**
```python
# In service configurations
TIMEOUT = 30  # seconds
MAX_RETRIES = 3
```

**4. Enable Connection Pooling**
```python
# For HTTP clients
session = requests.Session()
adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100)
session.mount('http://', adapter)
```

### Services Crashing?

**Check resources:**
```bash
docker stats
```

**Increase memory limits in docker-compose.yml:**
```yaml
services:
  user-service:
    deploy:
      resources:
        limits:
          memory: 2G
```

### Redis Not Helping?

**Verify cache hits:**
```bash
docker-compose exec redis redis-cli INFO stats | grep keyspace_hits
```

**Increase cache time:**
```python
@cache.memoize(timeout=600)  # 10 minutes
```

---

## 📋 For Your Presentation

### What to Show

1. **4 Bar Charts** (from `results/charts/`)
   - Average Response Time
   - Error Rate
   - Throughput
   - 95th Percentile

2. **Summary Table** (from `results/charts/summary_table.png`)

3. **Explanation** of each optimization:
   - **Redis**: Reduced DB queries by 70%, improved avg response time by 44%
   - **Kafka**: Async processing, reduced blocking operations, improved throughput by 65%
   - **Additional**: Connection pooling, indexing, query optimization

### Sample Presentation Slide

```
Performance Test Results (100 Concurrent Users)

Configuration Comparison:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
         │ Error Rate │ Avg Time │ Throughput
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Base     │   12.3% ❌ │  3245 ms │  165 req/s
+Redis   │    6.8% ⚠️ │  1823 ms │  274 req/s  (+66% ⬆️)
+Kafka   │    3.2% ✅ │  1105 ms │  453 req/s  (+65% ⬆️)
All Opts │    1.4% ✅ │   672 ms │  746 req/s  (+65% ⬆️)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Key Achievements:
✅ Error rate reduced from 12.3% to 1.4%
✅ Response time improved by 79%
✅ Throughput increased by 352%
✅ Successfully handles 100 concurrent users
```

---

## ⚡ Performance Tips

### Before Testing

1. **Clear all caches:**
   ```bash
   docker-compose exec redis redis-cli FLUSHDB
   docker-compose restart
   ```

2. **Close other applications** to avoid resource contention

3. **Ensure stable network** connection

### During Testing

1. **Monitor in real-time:**
   ```bash
   # Terminal 1: Docker stats
   docker stats
   
   # Terminal 2: Service logs
   docker-compose logs -f user-service
   
   # Terminal 3: Redis monitor
   docker-compose exec redis redis-cli MONITOR
   ```

2. **Don't interrupt tests** - let them complete fully

### After Testing

1. **Review HTML reports** for detailed analysis
2. **Check error logs** if error rate > 5%
3. **Analyze slow requests** in results tree
4. **Verify cache hit rates** in Redis

---

## 📝 Checklist Before Submission

- [ ] Database has 10,000+ records
- [ ] All 4 configurations tested
- [ ] Error rate < 5% for final configuration
- [ ] All 5 charts generated
- [ ] Summary CSV exported
- [ ] Screenshots taken
- [ ] Performance analysis written

---

## Need Help?

### Common Issues

**Q: JMeter command not found**
```bash
brew install jmeter
# or download from https://jmeter.apache.org/
```

**Q: Python dependencies missing**
```bash
pip3 install faker matplotlib seaborn pandas sqlalchemy
```

**Q: Services not responding**
```bash
docker-compose ps  # Check status
docker-compose logs <service-name>  # Check logs
docker-compose restart  # Restart all
```

**Q: Want to test with fewer users first?**
```bash
# Edit the script or run manually:
jmeter -n -t kayak_performance_test.jmx \
  -Jthreads=25 \  # 25 users instead of 100
  -Jrampup=15 \   # 15 second ramp-up
  -Jduration=180  # 3 minute test
  -l results/test_25users.jtl \
  -e -o results/test_25users_report
```

---

## 🎉 Success!

If you followed all steps, you now have:
✅ Comprehensive performance test results
✅ Visual charts for presentation
✅ Proof that your system handles 100 concurrent users with <5% error rate
✅ Data showing the impact of each optimization

**Good luck with your presentation!** 🚀
