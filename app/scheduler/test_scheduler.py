from __future__ import annotations
import pytest
import time
import random
from datetime import datetime as dt_time
import datetime

# import your functions (assuming they’re in scheduler.py)
from app.scheduler.scheduler import EmailScheduler, PriorityState

# ---- Fixtures and Mocks ----
from unittest.mock import Mock, patch, MagicMock


class DummyDateTime(datetime.datetime):
    def __new__(cls, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    """Allows overriding datetime.now() for deterministic testing."""

    @classmethod
    def now(cls, tz=None):
        # pretend it's 10:00 AM for morning tests
        return cls(2025, 10, 18, 10, 0, 0, tzinfo=tz)


"""
Automatically replace datetime.datetime with DummyDateTime in *your code*.
This ensures that whenever your application calls datetime.datetime.now(),
it gets the fixed time defined above, making tests deterministic.
"""


@pytest.fixture(autouse=True)
def patch_datetime(monkeypatch):
    monkeypatch.setattr(datetime, "date", DummyDateTime)
    yield  # the test will run and then restore normal behavior


@pytest.fixture
def mock_sleep(monkeypatch):
    """Avoid real sleeping."""
    monkeypatch.setattr(time, "sleep", lambda s: None)


@pytest.fixture
def mock_random(monkeypatch):
    """Force predictable random.choice."""
    monkeypatch.setattr(random, "choice", lambda x: x[0])  # always pick first


# ---- Tests ----


class TestEmailSchedulerInitialization:
    def test_default_init(self):
        scheduler = EmailScheduler(enable_loggin_info=False)
        assert scheduler.max_email_a_day == 70
        assert scheduler.max_email_an_hour == 30
        assert scheduler.buisness_hours_starting == dt_time(9, 0)
        assert scheduler.buisness_hours_ending == dt_time(17, 0)
