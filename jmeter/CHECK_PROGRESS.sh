#!/bin/bash

# Check JMeter Test Progress

echo "════════════════════════════════════════════════════════════"
echo "  JMETER PERFORMANCE TEST - PROGRESS CHECKER"
echo "════════════════════════════════════════════════════════════"
echo ""

# Check if test is running
if ps aux | grep -q "[r]un_all_performance_tests"; then
    echo "✅ Test is RUNNING"
    echo ""
    
    # Show current stage
    echo "📊 Current Activity (last 30 lines):"
    echo "────────────────────────────────────────────────────────────"
    tail -30 /Users/sujithdugyala/Desktop/DSGP\ 2/jmeter/full_test_output.log
    echo "────────────────────────────────────────────────────────────"
    echo ""
    
    # Check which config is running
    if grep -q "Testing Configuration: B (Base" /Users/sujithdugyala/Desktop/DSGP\ 2/jmeter/full_test_output.log 2>/dev/null; then
        echo "🔹 Stage: Configuration 1/4 - Base (B)"
    fi
    if grep -q "Testing Configuration: B+S" /Users/sujithdugyala/Desktop/DSGP\ 2/jmeter/full_test_output.log 2>/dev/null; then
        echo "🔹 Stage: Configuration 2/4 - Base + Redis (B+S)"
    fi
    if grep -q "Testing Configuration: B+S+K (" /Users/sujithdugyala/Desktop/DSGP\ 2/jmeter/full_test_output.log 2>/dev/null; then
        echo "🔹 Stage: Configuration 3/4 - Base + Redis + Kafka (B+S+K)"
    fi
    if grep -q "Testing Configuration: B+S+K+X" /Users/sujithdugyala/Desktop/DSGP\ 2/jmeter/full_test_output.log 2>/dev/null; then
        echo "🔹 Stage: Configuration 4/4 - All Optimizations (B+S+K+X)"
    fi
    
    echo ""
    echo "⏱️  Estimated time per config: ~6 minutes"
    echo "⏱️  Total time: ~30 minutes"
    echo ""
    echo "💡 To watch live progress:"
    echo "   tail -f /Users/sujithdugyala/Desktop/DSGP\\ 2/jmeter/full_test_output.log"
    
else
    echo "❌ Test is NOT running"
    echo ""
    
    # Check if test completed
    if [ -f "/Users/sujithdugyala/Desktop/DSGP 2/jmeter/results/performance_comparison.csv" ]; then
        echo "✅ TEST COMPLETED!"
        echo ""
        echo "📊 Results Summary:"
        echo "────────────────────────────────────────────────────────────"
        cat /Users/sujithdugyala/Desktop/DSGP\ 2/jmeter/results/performance_comparison.csv
        echo "────────────────────────────────────────────────────────────"
        echo ""
        echo "📁 View Reports:"
        echo "   open /Users/sujithdugyala/Desktop/DSGP\\ 2/jmeter/results/base_report/index.html"
        echo "   open /Users/sujithdugyala/Desktop/DSGP\\ 2/jmeter/results/base_s_report/index.html"
        echo "   open /Users/sujithdugyala/Desktop/DSGP\\ 2/jmeter/results/base_s_k_report/index.html"
        echo "   open /Users/sujithdugyala/Desktop/DSGP\\ 2/jmeter/results/base_s_k_x_report/index.html"
        echo ""
        echo "📊 Generate Charts:"
        echo "   cd /Users/sujithdugyala/Desktop/DSGP\\ 2/jmeter"
        echo "   python3 generate_comparison_charts.py"
    else
        echo "💡 Start the test with:"
        echo "   cd /Users/sujithdugyala/Desktop/DSGP\\ 2/jmeter"
        echo "   ./run_all_performance_tests.sh"
    fi
fi

echo ""
echo "════════════════════════════════════════════════════════════"
