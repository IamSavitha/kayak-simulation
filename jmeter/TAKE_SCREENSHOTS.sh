#!/bin/bash

# Automated Screenshot Data Generator
# Run this to get all the output you need to screenshot

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║        DATABASE DEMO - SCREENSHOT HELPER                     ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "This script will show you all the data you need to screenshot"
echo "for your presentation. Take screenshots as you go!"
echo ""
read -p "Press ENTER to start..."

# ============================================================
# PART 1: ALL SERVICES RUNNING
# ============================================================
clear
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📸 SCREENSHOT 1: All Services Running"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
docker-compose ps
echo ""
read -p "✅ Screenshot taken? Press ENTER for next..."

# ============================================================
# PART 2: MYSQL
# ============================================================
clear
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📸 SCREENSHOT 2: MySQL - Show Tables"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
docker-compose exec -T mysql mysql -ukayak_user -pkayak_pass kayak_db -e "SHOW TABLES;"
echo ""
read -p "✅ Screenshot taken? Press ENTER for next..."

clear
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📸 SCREENSHOT 3: MySQL - Row Counts (Scalability Proof)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
docker-compose exec -T mysql mysql -ukayak_user -pkayak_pass kayak_db << 'EOF'
SELECT 'users' as table_name, COUNT(*) as row_count FROM users
UNION ALL
SELECT 'flights', COUNT(*) FROM flights
UNION ALL
SELECT 'hotels', COUNT(*) FROM hotels
UNION ALL
SELECT 'hotel_rooms', COUNT(*) FROM hotel_rooms
UNION ALL
SELECT 'cars', COUNT(*) FROM cars
UNION ALL
SELECT 'bookings', COUNT(*) FROM bookings;
EOF
echo ""
read -p "✅ Screenshot taken? Press ENTER for next..."

clear
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📸 SCREENSHOT 4: MySQL - Users Table Schema"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
docker-compose exec -T mysql mysql -ukayak_user -pkayak_pass kayak_db -e "DESCRIBE users;"
echo ""
read -p "✅ Screenshot taken? Press ENTER for next..."

clear
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📸 SCREENSHOT 5: MySQL - Sample Data with Join"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
docker-compose exec -T mysql mysql -ukayak_user -pkayak_pass kayak_db << 'EOF'
SELECT 
    b.booking_id,
    u.email as user_email,
    b.booking_type,
    b.total_price,
    b.status,
    b.created_at
FROM bookings b
JOIN users u ON b.user_id = u.user_id
LIMIT 5;
EOF
echo ""
read -p "✅ Screenshot taken? Press ENTER for next..."

clear
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📸 SCREENSHOT 6: MySQL - Indexes (Performance)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
docker-compose exec -T mysql mysql -ukayak_user -pkayak_pass kayak_db -e "SHOW INDEX FROM flights;"
echo ""
read -p "✅ Screenshot taken? Press ENTER for next..."

# ============================================================
# PART 3: MONGODB
# ============================================================
clear
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📸 SCREENSHOT 7: MongoDB - Collections"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
docker-compose exec -T mongodb mongosh -u kayak_user -p kayak_pass --authenticationDatabase admin kayak_db --quiet --eval "show collections"
echo ""
read -p "✅ Screenshot taken? Press ENTER for next..."

clear
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📸 SCREENSHOT 8: MongoDB - Document Counts"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
docker-compose exec -T mongodb mongosh -u kayak_user -p kayak_pass --authenticationDatabase admin kayak_db --quiet --eval "
db.getCollectionNames().forEach(function(collection) {
    print(collection + ': ' + db[collection].countDocuments());
});
"
echo ""
read -p "✅ Screenshot taken? Press ENTER for next..."

clear
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📸 SCREENSHOT 9: MongoDB - Sample Review Document"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
docker-compose exec -T mongodb mongosh -u kayak_user -p kayak_pass --authenticationDatabase admin kayak_db --quiet --eval "
db.reviews.findOne()
"
echo ""
read -p "✅ Screenshot taken? Press ENTER for next..."

clear
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📸 SCREENSHOT 10: MongoDB - Email Logs (Kafka Integration)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
docker-compose exec -T mongodb mongosh -u kayak_user -p kayak_pass --authenticationDatabase admin kayak_db --quiet --eval "
db.email_logs.find().sort({sent_at: -1}).limit(3).pretty()
"
echo ""
read -p "✅ Screenshot taken? Press ENTER for next..."

# ============================================================
# PART 4: REDIS
# ============================================================
clear
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📸 SCREENSHOT 11: Redis - Cache Keys & Size"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Total cache keys:"
docker-compose exec -T redis redis-cli DBSIZE
echo ""
echo "Sample cache keys:"
docker-compose exec -T redis redis-cli KEYS '*' | head -20
echo ""
read -p "✅ Screenshot taken? Press ENTER for next..."

clear
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📸 SCREENSHOT 12: Redis - Cache Hit Rate"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
docker-compose exec -T redis redis-cli INFO stats | grep -E "keyspace_hits|keyspace_misses"
echo ""
echo "Calculating hit rate..."
HITS=$(docker-compose exec -T redis redis-cli INFO stats | grep keyspace_hits | cut -d: -f2 | tr -d '\r')
MISSES=$(docker-compose exec -T redis redis-cli INFO stats | grep keyspace_misses | cut -d: -f2 | tr -d '\r')
TOTAL=$((HITS + MISSES))
if [ $TOTAL -gt 0 ]; then
    HIT_RATE=$(echo "scale=2; $HITS * 100 / $TOTAL" | bc)
    echo "Cache Hit Rate: ${HIT_RATE}%"
fi
echo ""
read -p "✅ Screenshot taken? Press ENTER for next..."

clear
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📸 SCREENSHOT 13: Redis - Memory Usage"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
docker-compose exec -T redis redis-cli INFO memory | grep -E "used_memory_human|used_memory_peak_human|maxmemory_human"
echo ""
read -p "✅ Screenshot taken? Press ENTER for next..."

# ============================================================
# PART 5: KAFKA
# ============================================================
clear
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📸 SCREENSHOT 14: Kafka - Topics List"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
docker-compose exec -T kafka kafka-topics --list --bootstrap-server localhost:9092 2>/dev/null || echo "Kafka not running"
echo ""
read -p "✅ Screenshot taken? Press ENTER for next..."

# ============================================================
# SUMMARY
# ============================================================
clear
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║              ✅ ALL SCREENSHOTS COMPLETE! ✅                 ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📸 Screenshots Taken:"
echo "   1. All services running (docker-compose ps)"
echo "   2. MySQL - Tables list"
echo "   3. MySQL - Row counts (scalability)"
echo "   4. MySQL - Users schema"
echo "   5. MySQL - Sample data with joins"
echo "   6. MySQL - Indexes"
echo "   7. MongoDB - Collections"
echo "   8. MongoDB - Document counts"
echo "   9. MongoDB - Sample review"
echo "  10. MongoDB - Email logs (Kafka)"
echo "  11. Redis - Cache keys"
echo "  12. Redis - Hit rate"
echo "  13. Redis - Memory usage"
echo "  14. Kafka - Topics list"
echo ""
echo "📊 Don't forget to screenshot:"
echo "   • JMeter performance graphs"
echo "   • Performance comparison charts"
echo ""
echo "📁 Location of charts:"
echo "   /Users/sujithdugyala/Desktop/DSGP\ 2/jmeter/results/charts/"
echo ""
echo "🎉 You're ready for your demo!"
echo ""
