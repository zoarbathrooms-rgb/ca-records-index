#!/bin/bash
# collect.sh <run_id> -- download all shard artifacts, merge, report, place.
set -e
RUN_ID="$1"
REPO=ApTwoTone/ca-records-index
WORK=/tmp/ca-records-index
LOCAL_OUT="/Users/carlosescobar/Documents/Real-Estate 2/canary_run/priority_jun16_18/jun16_18_index_harvest.csv"
SPARK_DIR="/home/kai/Real-Estate-Work/analysis/netr_event_history_20260622/exports"

rm -rf "$WORK/artifacts" && mkdir -p "$WORK/artifacts"
gh run download "$RUN_ID" -R "$REPO" -D "$WORK/artifacts"
# flatten: all shard CSVs into one dir
mkdir -p "$WORK/shards_all"
find "$WORK/artifacts" -name '*.csv' -exec cp {} "$WORK/shards_all/" \;
echo "shard files: $(ls "$WORK/shards_all" | wc -l)"

python3 "$WORK/merge_and_report.py" "$WORK/shards_all" "$LOCAL_OUT"
echo "=== scp to spark ==="
scp -q "$LOCAL_OUT" "spark:$SPARK_DIR/jun16_18_index_harvest.csv" && echo "scp OK -> spark:$SPARK_DIR/"
