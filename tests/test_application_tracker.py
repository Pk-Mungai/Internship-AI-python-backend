
import json
import pytest

from src.application_tracker import ApplicationTracker


@pytest.fixture
def tracker(tmp_path):
    storage = tmp_path / "applications.json"
    return ApplicationTracker(storage)


def test_creates_storage_file(tracker):
    assert tracker.storage_path.exists()


def test_adds_application(tracker):
    application = tracker.add_application("INT001")

    assert application["internship_id"] == "INT001"
    assert application["status"] == "saved"
    assert application["notes"] == ""


def test_adds_application_with_custom_status_and_notes(tracker):
    application = tracker.add_application(
        "INT002",
        status="applied",
        notes="Application submitted.",
    )

    assert application["status"] == "applied"
    assert application["notes"] == "Application submitted."


def test_rejects_duplicate_application(tracker):
    tracker.add_application("INT001")

    with pytest.raises(ValueError, match="already exists"):
        tracker.add_application("INT001")


def test_rejects_invalid_status(tracker):
    with pytest.raises(ValueError, match="Invalid status"):
        tracker.add_application("INT001", status="pending")


def test_retrieves_application(tracker):
    tracker.add_application("INT001")

    application = tracker.get_application("INT001")

    assert application is not None
    assert application["internship_id"] == "INT001"


def test_returns_none_for_unknown_application(tracker):
    assert tracker.get_application("UNKNOWN") is None


def test_updates_application_status(tracker):
    tracker.add_application("INT001")

    updated = tracker.update_status("INT001", "shortlisted")

    assert updated["status"] == "shortlisted"


def test_filters_applications_by_status(tracker):
    tracker.add_application("INT001", status="saved")
    tracker.add_application("INT002", status="applied")
    tracker.add_application("INT003", status="saved")

    saved = tracker.list_applications(status="saved")

    assert len(saved) == 2
    assert all(item["status"] == "saved" for item in saved)


def test_updates_application_notes(tracker):
    tracker.add_application("INT001")

    updated = tracker.update_notes(
        "INT001",
        "Interview scheduled for next week.",
    )

    assert updated["notes"] == "Interview scheduled for next week."


def test_deletes_application(tracker):
    tracker.add_application("INT001")

    assert tracker.delete_application("INT001") is True
    assert tracker.get_application("INT001") is None


def test_returns_false_when_deleting_unknown_application(tracker):
    assert tracker.delete_application("UNKNOWN") is False


def test_rejects_empty_internship_id(tracker):
    with pytest.raises(ValueError, match="cannot be empty"):
        tracker.add_application(" ")


def test_rejects_non_string_notes(tracker):
    with pytest.raises(TypeError, match="notes must be a string"):
        tracker.add_application("INT001", notes=123)


def test_persists_applications_between_instances(tracker):
    tracker.add_application("INT001", status="applied")

    another_tracker = ApplicationTracker(tracker.storage_path)

    application = another_tracker.get_application("INT001")

    assert application is not None
    assert application["status"] == "applied"


def test_detects_corrupted_storage(tmp_path):
    storage = tmp_path / "applications.json"
    storage.write_text("{invalid json", encoding="utf-8")

    tracker = ApplicationTracker(storage)

    with pytest.raises(ValueError, match="invalid JSON"):
        tracker.list_applications()
