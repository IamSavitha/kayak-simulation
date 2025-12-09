#!/bin/bash

# Quick Performance Test Runner for Kayak Project
# This runs a DEMO test (faster) - use full script for complete testing

echo "=============================================="
echo "KAYAK PERFORMANCE TEST - DEMO MODE"
echo "=============================================="
echo ""
echo "Running with:"
echo "  - 25 concurrent users (vs 100 for full test)"
echo "  - 2 minute duration (vs 5 minutes)"
echo "  - Single configuration"
echo ""
echo "For FULL testing (100 users, all 4 configs, ~30 min):"
echo "  ./run_all_performance_tests.sh"
echo ""
echo "=============================================="
echo ""

cd /Users/sujithdugyala/Desktop/DSGP\ 2/jmeter

# Clean old results
rm -rf results/demo_report results/demo_test.jtl

echo "Starting demo test..."
echo ""

# Run JMeter test
jmeter -n -t kayak_performance_test.jmx \
  -Jthreads=25 \
  -Jrampup=10 \
  -Jduration=120 \
  -Jloops=5 \
  -l results/demo_test.jtl \
  -e -o results/demo_report

echo ""
echo "=============================================="
echo "DEMO TEST COMPLETE!"
echo "=============================================="
echo ""

# Extract metrics
if [ -f "results/demo_report/statistics.json" ]; then
    echo "📊 Results:"
    python3 << 'PYTHON'
import json
with open('results/demo_report/statistics.json') as f:
    data = json.load(f)
    overall = data.get('Total', {})
    total = overall.get('sampleCount', 0)
    error = overall.get('errorPct', 0.0)
    avg_time = overall.get('meanResTime', 0)
    throughput = overall.get('throughput', 0.0)
    
    status = "✅ PASS" if error < 5.0 else "❌ FAIL"
    
    print(f"  Total Requests:     {total:,}")
    print(f"  Error Rate:         {error:.2f}% {status}")
    print(f"  Avg Response Time:  {avg_time:.0f} ms")
    print(f"  Throughput:         {throughput:.2f} req/s")
PYTHON
fi

echo ""
echo "📁 View detailed report:"
echo "  open results/demo_report/index.html"
echo ""
echo "🚀 Ready for full test? Run:"
echo "  ./run_all_performance_tests.sh"
echo ""
