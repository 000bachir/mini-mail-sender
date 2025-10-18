import pytest
import builtins
import time
import random
from datetime import datetime, timedelta
import types

# import your functions (assuming they’re in scheduler.py)
import scheduler

# ---- Fixtures and Mocks ----


class DummyDateTime(datetime):
    """Allows overriding datetime.now() for deterministic testing."""

    @classmethod
    def now(cls, tz=None):
        # pretend it's 10:00 AM for morning tests
        return cls(2025, 10, 18, 10, 0, 0)


@pytest.fixture(autouse=True)
def patch_datetime(monkeypatch):
    monkeypatch.setattr(scheduler, "datetime", DummyDateTime)
    yield


@pytest.fixture
def mock_sleep(monkeypatch):
    """Avoid real sleeping."""
    monkeypatch.setattr(time, "sleep", lambda s: None)


@pytest.fixture
def mock_random(monkeypatch):
    """Force predictable random.choice."""
    monkeypatch.setattr(random, "choice", lambda x: x[0])  # always pick first


# ---- Tests ----


def test_retrieve_current_time_returns_datetime():
    result = scheduler.retreaving_the_current_time()
    assert isinstance(result, datetime)


def test_retrieve_local_timezone_is_string():
    tz = scheduler.retreiving_the_local_time_zone()
    assert isinstance(tz, str)
    assert len(tz) > 0


def test_add_time_randomly_morning(mock_random):
    td = scheduler.adding_time_randomely()
    assert isinstance(td, timedelta)
    assert td.total_seconds() > 0


def test_add_time_randomly_evening(monkeypatch, mock_random):
    class Evening(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2025, 10, 18, 18, 0, 0)

    monkeypatch.setattr(scheduler, "datetime", Evening)
    td = scheduler.adding_time_randomely()
    assert isinstance(td, timedelta)
    assert td.total_seconds() > 0


def test_time_manipulation_runs_fast(monkeypatch, mock_sleep, mock_random, capsys):
    """Test that the function runs to completion and prints expected output."""
    # Shorten the time window by forcing random_choice to 1 second
    monkeypatch.setattr(
        scheduler, "adding_time_randomely", lambda: timedelta(seconds=1)
    )
    scheduler.time_manipulation()
    output = capsys.readouterr().out
    assert "the program has reached it end" in output
    assert "please keep in mind" in output
