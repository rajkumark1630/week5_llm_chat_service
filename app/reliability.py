
import json
import os
import time
from datetime import datetime, timezone


RELIABILITY_FILE = "reliability.jsonl"


def log_request(status, response_time, error=None):
    """Log API request reliability metrics."""

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "response_time": round(response_time, 4),
        "error": str(error) if error else None
    }

    with open(RELIABILITY_FILE, "a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")


def get_reliability_records():
    """Read reliability records."""

    records = []

    if not os.path.exists(RELIABILITY_FILE):
        return records

    with open(RELIABILITY_FILE, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                records.append(json.loads(line))

    return records


def get_reliability_summary():
    """Calculate reliability metrics."""

    records = get_reliability_records()

    total_requests = len(records)

    successful = sum(
        1 for item in records
        if item["status"] == "success"
    )

    failed = sum(
        1 for item in records
        if item["status"] == "failed"
    )

    response_times = [
        item["response_time"] for item in records
    ]

    avg_response_time = (
        sum(response_times) / len(response_times)
        if response_times else 0
    )

    success_rate = (
        successful / total_requests * 100
        if total_requests else 0
    )

    failure_rate = (
        failed / total_requests * 100
        if total_requests else 0
    )

    return {
        "total_requests": total_requests,
        "successful_requests": successful,
        "failed_requests": failed,
        "success_rate": round(success_rate, 2),
        "failure_rate": round(failure_rate, 2),
        "average_response_time": round(avg_response_time, 4)
    }


def print_reliability():
    """Display reliability report."""

    summary = get_reliability_summary()

    print("\n========== RELIABILITY REPORT ==========")

    print("Total Requests:", summary["total_requests"])
    print("Successful Requests:", summary["successful_requests"])
    print("Failed Requests:", summary["failed_requests"])
    print("Success Rate:", str(summary["success_rate"]) + "%")
    print("Failure Rate:", str(summary["failure_rate"]) + "%")
    print(
        "Average Response Time:",
        str(summary["average_response_time"]) + " seconds"
    )

    print("========================================\n")


if __name__ == "__main__":
    print_reliability()
