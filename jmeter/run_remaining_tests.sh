#!/bin/bash

echo "=========================================="
echo "CONTINUING JMETER TESTS FROM CONFIG 2"
echo "=========================================="
echo ""

cd /Users/sujithdugyala/Desktop/DSGP\ 2/jmeter

# Configuration 2: Base + Redis
echo "=========================================="
echo "Testing Configuration: B+S (Base + Redis)"
echo "=========================================="
cd /Users/sujithdugyala/Desktop/DSGP\ 2
docker-compose start redis
docker-compose stop kafka zookeeper
sleep 10

cd /Users/sujithdugyala/Desktop/DSGP\ 2/jmeter
jmeter -n -t kayak_performance_test.jmx \
  -l results/base_s_results.jtl \
  -e -o results/base_s_report \
  -Jthreads=100 -Jrampup=30 -Jduration=300

echo "✅ Test 2 complete!"
sleep 10

# Configuration 3: Base + Redis + Kafka  
echo "=========================================="
echo "Testing Configuration: B+S+K (Base + Redis + Kafka)"
echo "=========================================="
cd /Users/sujithdugyala/Desktop/DSGP\ 2
docker-compose start redis kafka zookeeper
sleep 15

cd /Users/sujithdugyala/Desktop/DSGP\ 2/jmeter
jmeter -n -t kayak_performance_test.jmx \
  -l results/base_s_k_results.jtl \
  -e -o results/base_s_k_report \
  -Jthreads=100 -Jrampup=30 -Jduration=300

echo "✅ Test 3 complete!"
sleep 10

# Configuration 4: All optimizations
echo "=========================================="
echo "Testing Configuration: B+S+K+X (All Optimizations)"
echo "=========================================="
cd /Users/sujithdugyala/Desktop/DSGP\ 2/jmeter
jmeter -n -t kayak_performance_test.jmx \
  -l results/base_s_k_x_results.jtl \
  -e -o results/base_s_k_x_report \
  -Jthreads=100 -Jrampup=30 -Jduration=300

echo "✅ Test 4 complete!"

echo ""
echo "=========================================="
echo "ALL TESTS COMPLETE!"
echo "=========================================="
echo ""
echo "Generate comparison charts:"
echo "  cd /Users/sujithdugyala/Desktop/DSGP\\ 2/jmeter"
echo "  python3 generate_comparison_charts.py"
echo ""
