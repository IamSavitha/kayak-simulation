#!/bin/bash

# Kayak Performance Testing Automation Script
# Runs all 4 configurations and generates reports

set -e

echo "=========================================="
echo "KAYAK PERFORMANCE TESTING"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
JMETER_HOME=${JMETER_HOME:-"/usr/local/bin"}
JMETER_DIR="/Users/sujithdugyala/Desktop/DSGP 2/jmeter"
TEST_PLAN="${JMETER_DIR}/kayak_performance_test.jmx"
RESULTS_DIR="${JMETER_DIR}/results"
PROJECT_DIR="/Users/sujithdugyala/Desktop/DSGP 2"

# Check if JMeter is installed
if ! command -v jmeter &> /dev/null; then
    echo -e "${RED}❌ JMeter not found!${NC}"
    echo "Install with: brew install jmeter"
    exit 1
fi

echo -e "${GREEN}✅ JMeter found${NC}"
echo ""

# Create results directory
mkdir -p $RESULTS_DIR

# Function to run a test configuration
run_test() {
    local config_name=$1
    local config_desc=$2
    local prep_commands=$3
    
    echo "=========================================="
    echo "Testing Configuration: $config_desc"
    echo "=========================================="
    echo ""
    
    # Execute preparation commands
    if [ -n "$prep_commands" ]; then
        echo "Preparing configuration..."
        eval "$prep_commands"
        echo "Waiting 10 seconds for services to stabilize..."
        sleep 10
    fi
    
    # Create results directory if it doesn't exist
    mkdir -p "${RESULTS_DIR}"
    
    # Clear results
    rm -f "${RESULTS_DIR}/${config_name}_results.jtl"
    rm -rf "${RESULTS_DIR}/${config_name}_report"
    
    echo "Running JMeter test..."
    echo "Test file: $TEST_PLAN"
    echo "Results: ${RESULTS_DIR}/${config_name}_results.jtl"
    echo ""
    
    # Run JMeter in CLI mode
    jmeter -n -t "$TEST_PLAN" \
        -l "${RESULTS_DIR}/${config_name}_results.jtl" \
        -e -o "${RESULTS_DIR}/${config_name}_report" \
        -Jconfig_name="$config_desc" \
        -Jthreads=100 \
        -Jrampup=30 \
        -Jduration=300
    
    echo ""
    echo -e "${GREEN}✅ Test completed: $config_desc${NC}"
    echo "Report: ${RESULTS_DIR}/${config_name}_report/index.html"
    echo ""
    
    # Extract key metrics
    echo "Key Metrics:"
    if [ -f "${RESULTS_DIR}/${config_name}_report/statistics.json" ]; then
        python3 -c "
import json
with open('${RESULTS_DIR}/${config_name}_report/statistics.json') as f:
    data = json.load(f)
    overall = data.get('Total', {})
    print(f\"  Total Requests: {overall.get('sampleCount', 0)}\")
    print(f\"  Error Rate: {overall.get('errorPct', 0)}%\")
    print(f\"  Avg Response Time: {overall.get('meanResTime', 0)} ms\")
    print(f\"  95th Percentile: {overall.get('pct3ResTime', 0)} ms\")
    print(f\"  Throughput: {overall.get('throughput', 0)} req/s\")
"
    fi
    echo ""
    
    # Wait before next test
    echo "Waiting 30 seconds before next test..."
    sleep 30
}

# ========================================
# TEST 1: Base Configuration (B)
# ========================================
run_test "base" "B (Base - No Optimizations)" "
cd '$PROJECT_DIR'
echo 'Stopping Redis and Kafka...'
docker-compose stop redis kafka zookeeper
docker-compose restart user-service flight-service hotel-service car-service booking-service
"

# ========================================
# TEST 2: Base + SQL Caching (B+S)
# ========================================
run_test "base_s" "B+S (Base + Redis Caching)" "
cd '$PROJECT_DIR'
echo 'Starting Redis, stopping Kafka...'
docker-compose start redis
docker-compose stop kafka zookeeper
docker-compose exec -T redis redis-cli FLUSHDB
docker-compose restart user-service flight-service hotel-service car-service booking-service
"

# ========================================
# TEST 3: Base + SQL + Kafka (B+S+K)
# ========================================
run_test "base_s_k" "B+S+K (Base + Redis + Kafka)" "
cd '$PROJECT_DIR'
echo 'Starting all services...'
docker-compose up -d
docker-compose exec -T redis redis-cli FLUSHDB
sleep 15
docker-compose restart user-service flight-service hotel-service car-service booking-service
"

# ========================================
# TEST 4: All Optimizations (B+S+K+X)
# ========================================
run_test "base_s_k_x" "B+S+K+X (All Optimizations)" "
cd '$PROJECT_DIR'
echo 'All services with optimizations...'
docker-compose up -d
docker-compose exec -T redis redis-cli FLUSHDB
sleep 15
"

# ========================================
# Generate Comparison Report
# ========================================
echo "=========================================="
echo "GENERATING COMPARISON REPORT"
echo "=========================================="
echo ""

python3 << 'PYTHON_SCRIPT'
import json
import os
from datetime import datetime

results_dir = "results"
configurations = [
    ("base", "B (Base)"),
    ("base_s", "B+S (+ Redis)"),
    ("base_s_k", "B+S+K (+ Kafka)"),
    ("base_s_k_x", "B+S+K+X (All)")
]

print("=" * 80)
print(" " * 20 + "PERFORMANCE TEST SUMMARY")
print("=" * 80)
print()

comparison_data = []

for config_id, config_name in configurations:
    stats_file = f"{results_dir}/{config_id}_report/statistics.json"
    
    if os.path.exists(stats_file):
        with open(stats_file) as f:
            data = json.load(f)
            overall = data.get('Total', {})
            
            total_requests = overall.get('sampleCount', 0)
            error_pct = overall.get('errorPct', 0.0)
            avg_time = overall.get('meanResTime', 0)
            pct95_time = overall.get('pct3ResTime', 0)
            throughput = overall.get('throughput', 0.0)
            
            status = "✅" if error_pct < 5.0 else "❌"
            
            print(f"Configuration: {config_name}")
            print(f"  Total Requests:     {total_requests:,}")
            print(f"  Error Rate:         {error_pct:.2f}% {status}")
            print(f"  Avg Response Time:  {avg_time:.0f} ms")
            print(f"  95th Percentile:    {pct95_time:.0f} ms")
            print(f"  Throughput:         {throughput:.2f} req/s")
            print()
            
            comparison_data.append({
                'config': config_name,
                'total_requests': total_requests,
                'error_rate': error_pct,
                'avg_time': avg_time,
                'pct95_time': pct95_time,
                'throughput': throughput
            })

# Save comparison data as CSV
csv_file = f"{results_dir}/performance_comparison.csv"
with open(csv_file, 'w') as f:
    f.write("Configuration,Total Requests,Error Rate (%),Avg Response Time (ms),95th Percentile (ms),Throughput (req/s)\n")
    for row in comparison_data:
        f.write(f"{row['config']},{row['total_requests']},{row['error_rate']:.2f},{row['avg_time']:.0f},{row['pct95_time']:.0f},{row['throughput']:.2f}\n")

print("=" * 80)
print(f"Comparison data saved to: {csv_file}")
print("=" * 80)
print()

# Check if all tests passed
all_passed = all(row['error_rate'] < 5.0 for row in comparison_data)
if all_passed:
    print("✅ ALL TESTS PASSED! Error rates below 5%")
else:
    print("❌ SOME TESTS FAILED! Error rates above 5%")
    print("   Review the configurations and optimize further.")

PYTHON_SCRIPT

echo ""
echo "=========================================="
echo "TESTING COMPLETE!"
echo "=========================================="
echo ""
echo "View detailed reports:"
echo "  Base:          open results/base_report/index.html"
echo "  Base + Redis:  open results/base_s_report/index.html"
echo "  Base + Kafka:  open results/base_s_k_report/index.html"
echo "  All Opts:      open results/base_s_k_x_report/index.html"
echo ""
echo "Comparison CSV: results/performance_comparison.csv"
echo ""
