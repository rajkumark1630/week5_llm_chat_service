
import json
import pytest

from app import reliability


@pytest.fixture
def temp_reliability_file(tmp_path, monkeypatch):
    test_file = tmp_path / "test_reliability.jsonl"

    monkeypatch.setattr(
        reliability,
        "RELIABILITY_FILE",
        str(test_file)
    )

    return test_file


def test_log_success_request(temp_reliability_file):
    reliability.log_request(
        status="success",
        response_time=1.25
    )

    records = reliability.get_reliability_records()

    assert len(records) == 1
    assert records[0]["status"] == "success"
    assert records[0]["response_time"] == 1.25
    assert records[0]["error"] is None


def test_log_failed_request(temp_reliability_file):
    reliability.log_request(
        status="failed",
        response_time=2.5,
        error="API connection failed"
    )

    records = reliability.get_reliability_records()

    assert len(records) == 1
    assert records[0]["status"] == "failed"
    assert records[0]["error"] == "API connection failed"


def test_get_reliability_summary(temp_reliability_file):
    reliability.log_request("success", 1.0)
    reliability.log_request("success", 2.0)
    reliability.log_request("failed", 3.0, "API error")

    summary = reliability.get_reliability_summary()

    assert summary["total_requests"] == 3
    assert summary["successful_requests"] == 2
    assert summary["failed_requests"] == 1
    assert summary["success_rate"] == 66.67
    assert summary["failure_rate"] == 33.33
    assert summary["average_response_time"] == 2.0


def test_empty_reliability_summary(temp_reliability_file):
    summary = reliability.get_reliability_summary()

    assert summary["total_requests"] == 0
    assert summary["successful_requests"] == 0
    assert summary["failed_requests"] == 0
    assert summary["success_rate"] == 0
    assert summary["failure_rate"] == 0
    assert summary["average_response_time"] == 0


def test_multiple_requests(temp_reliability_file):
    reliability.log_request("success", 0.5)
    reliability.log_request("success", 1.5)

    records = reliability.get_reliability_records()

    assert len(records) == 2
    assert records[0]["status"] == "success"
    assert records[1]["status"] == "success"


def test_reliability_record_is_valid_json(temp_reliability_file):
    reliability.log_request("success", 1.2)

    with open(temp_reliability_file, "r", encoding="utf-8") as file:
        record = json.loads(file.readline())

    assert "timestamp" in record
    assert "status" in record
    assert "response_time" in record
    assert record["status"] == "success"
