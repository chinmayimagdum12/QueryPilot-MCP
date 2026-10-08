"""Analyze audit.jsonl and generate a summary report of tool calls, statuses, and latency metrics."""

import json
import statistics
import sys
from pathlib import Path


def main():
    audit_file = Path("audit.jsonl")
    if not audit_file.exists():
        print("No audit.jsonl file found.")
        sys.exit(0)

    tool_counts = {}
    status_counts = {}
    latencies = []

    with open(audit_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            tool = entry.get("tool", "unknown")
            status = entry.get("status", "unknown")
            elapsed = entry.get("elapsed_ms", 0.0)

            tool_counts[tool] = tool_counts.get(tool, 0) + 1
            status_counts[status] = status_counts.get(status, 0) + 1
            if elapsed > 0:
                latencies.append(elapsed)

    print("=" * 45)
    print(" QueryPilot MCP - Audit Log Summary Report")
    print("=" * 45)
    print(f"\nTotal queries logged: {sum(status_counts.values())}")

    print("\n--- Calls by Tool ---")
    for tool, count in sorted(tool_counts.items(), key=lambda x: -x[1]):
        print(f"  {tool:<25}: {count}")

    print("\n--- Calls by Status ---")
    for status, count in sorted(status_counts.items(), key=lambda x: -x[1]):
        print(f"  {status:<25}: {count}")

    if latencies:
        latencies.sort()
        p50 = statistics.median(latencies)
        p95 = latencies[int(len(latencies) * 0.95)] if len(latencies) > 1 else latencies[0]
        print("\n--- Latency Performance (ms) ---")
        print(f"  Min : {min(latencies):.1f} ms")
        print(f"  p50 : {p50:.1f} ms")
        print(f"  p95 : {p95:.1f} ms")
        print(f"  Max : {max(latencies):.1f} ms")
    else:
        print("\nNo latency data recorded yet.")

    print("=" * 45)


if __name__ == "__main__":
    main()
