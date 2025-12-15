#!/bin/bash
# Test script to verify real-time analyzer with polling fallback

echo "========================================="
echo "Real-Time Analyzer Polling Test"
echo "========================================="
echo ""

# Create a test log file
TEST_LOG="logs/test_polling.jsonl"
rm -f "$TEST_LOG"

echo "1. Starting real-time analyzer..."
python realtime_drift_analyzer.py --log-file "$TEST_LOG" --window-size 10 &
ANALYZER_PID=$!

echo "   Analyzer PID: $ANALYZER_PID"
echo "   Waiting 3 seconds for analyzer to start..."
sleep 3

echo ""
echo "2. Writing test predictions..."

# Write 50 predictions (5 windows)
for i in {1..50}; do
  TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S.%6NZ" 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%SZ")

  # Baseline (low prediction values)
  if [ $i -le 30 ]; then
    PRED=$(python3 -c "import random; print(round(random.uniform(0.05, 0.15), 6))")
  else
    # Drift (high prediction values)
    PRED=$(python3 -c "import random; print(round(random.uniform(0.5, 0.9), 6))")
  fi

  echo "{\"timestamp\": \"$TIMESTAMP\", \"input_features\": {\"feature1\": 5.0, \"feature2\": 2.0, \"feature3\": 1.0}, \"prediction\": $PRED, \"model_version\": \"v1.0\", \"drift_phase\": 1}" >> "$TEST_LOG"

  if [ $((i % 10)) -eq 0 ]; then
    echo "   Written $i/50 predictions..."
    sleep 3  # Give polling time to process
  else
    sleep 0.2
  fi
done

echo ""
echo "3. Waiting 5 seconds for processing..."
sleep 5

echo ""
echo "4. Stopping analyzer..."
kill $ANALYZER_PID 2>/dev/null

echo ""
echo "5. Checking results..."
PRED_COUNT=$(wc -l < "$TEST_LOG" | tr -d ' ')
echo "   Total predictions written: $PRED_COUNT"

echo ""
echo "Test complete!"
echo "You should have seen:"
echo "  - 3 baseline windows (STABLE)"
echo "  - 2 drift windows (DRIFT DETECTED)"
echo ""
echo "Check the output above to verify drift was detected."
