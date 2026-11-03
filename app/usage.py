
import json
import os


USAGE_FILE = "usage.jsonl"


def get_usage():
    """Read all API usage records."""

    records = []

    if not os.path.exists(USAGE_FILE):
        return records

    with open(USAGE_FILE, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                records.append(json.loads(line))

    return records


def get_usage_summary():
    """Calculate total token usage and cost."""

    records = get_usage()

    total_requests = len(records)
    total_input_tokens = sum(
        item.get("input_tokens", 0) for item in records
    )
    total_output_tokens = sum(
        item.get("output_tokens", 0) for item in records
    )
    total_cost = sum(
        item.get("cost_usd", 0) for item in records
    )

    return {
        "total_requests": total_requests,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "total_tokens": total_input_tokens + total_output_tokens,
        "total_cost_usd": round(total_cost, 8)
    }


def print_usage():
    """Display usage summary."""

    summary = get_usage_summary()

    print("\n========== API USAGE SUMMARY ==========")

    print("Total Requests:", summary["total_requests"])
    print("Input Tokens:", summary["total_input_tokens"])
    print("Output Tokens:", summary["total_output_tokens"])
    print("Total Tokens:", summary["total_tokens"])
    print("Total Cost (USD):", summary["total_cost_usd"])

    print("=======================================\n")


if __name__ == "__main__":
    print_usage()
