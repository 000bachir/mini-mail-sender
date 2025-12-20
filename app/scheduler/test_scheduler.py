from __future__ import annotations
import pytest
import logging
import random
from datetime import date, datetime as dt_time
from datetime import timedelta
import datetime
from datetime import time

# import your functions (assuming they’re in scheduler.py)
from app.scheduler.scheduler import EmailScheduler

# ---- Fixtures and Mocks ----
from unittest.mock import patch


class DummyDateTime(datetime.datetime):
    def __new__(cls, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    """Allows overriding datetime.now() for deterministic testing."""

    @classmethod
    def now(cls, tz=None):
        # pretend it's 10:00 AM for morning tests
        return cls(2025, 10, 18, 10, 0, 0, tzinfo=tz)


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
        scheduler = EmailScheduler()
        assert scheduler.max_email_an_hour == 30
        assert scheduler.email_sent_during_a_day == 0
        assert scheduler.email_sent_during_an_hour == 0
        assert scheduler.buisness_hours_starting == time(9, 0)
        assert scheduler.buisness_hours_ending == time(17, 0)

    def test_custom_init(self):
        scheduler = EmailScheduler(
            daily_batch_emails=150,
            max_email_an_hour=50,
            buisness_hours_starting=time(9, 0),
            buisness_hours_ending=time(17, 0),
            enable_loggin_info=False,
        )
        assert scheduler.buisness_hours_starting == time(9, 0)
        assert scheduler.buisness_hours_ending == time(17, 0)
        assert scheduler.max_email_an_hour == 50

    def test_interval_init(self):
        scheduler = EmailScheduler()
        assert len(scheduler.morning_intervals) == 4
        assert len(scheduler.evening_intervals) == 4
        assert isinstance(scheduler.noon_interval, timedelta)


class TestCheckingBusinessHours:
    def test_weekend_within_buisness_hours(self):
        scheduler = EmailScheduler(enable_loggin_info=False)
        test_time = datetime.datetime(2025, 1, 9, 10, 0)
        assert scheduler.checking_buisness_hours(test_time)

    def test_weekday_before_business_hours(self):
        scheduler = EmailScheduler(enable_loggin_info=False)
        # Monday at 8 AM
        test_time = datetime.datetime(2025, 1, 8, 8, 0)
        assert not scheduler.checking_buisness_hours(test_time)

    def test_weekday_after_business_hours(self):
        scheduler = EmailScheduler(enable_loggin_info=False)
        # Monday at 6 PM
        test_time = datetime.datetime(2025, 1, 8, 18, 0)
        assert not scheduler.checking_buisness_hours(test_time)

    def test_weekend_saturday(self):
        scheduler = EmailScheduler(enable_loggin_info=False)
        # Saturday at 10 AM
        test_time = datetime.datetime(2025, 1, 11, 10, 0)
        assert not scheduler.checking_buisness_hours(test_time)

    def test_weekend_sunday(self):
        scheduler = EmailScheduler(enable_loggin_info=False)
        # Sunday at 10 AM
        test_time = datetime.datetime(2025, 1, 12, 10, 0)
        assert not scheduler.checking_buisness_hours(test_time)

    def test_edge_of_business_hours_start(self):
        scheduler = EmailScheduler(enable_loggin_info=False)
        # Monday at 9 AM exactly
        test_time = datetime.datetime(2025, 1, 8, 9, 0)
        assert scheduler.checking_buisness_hours(test_time)

    def test_edge_of_business_hours_end(self):
        scheduler = EmailScheduler(enable_loggin_info=False)
        # Monday at 5 PM exactly
        test_time = datetime.datetime(2025, 1, 8, 17, 0)
        assert scheduler.checking_buisness_hours(test_time)

    def test_default_current_time(self):
        scheduler = EmailScheduler(enable_loggin_info=False)
        # Should use current time if no time provided
        result = scheduler.checking_buisness_hours()
        assert isinstance(result, bool)


class TestAddRandomDelayAfterInit:
    @patch("app.scheduler.scheduler.EmailScheduler.get_current_time")
    def test_morning_delay(self, mock_time):
        scheduler = EmailScheduler(enable_loggin_info=False)
        mock_time.return_value = datetime.datetime(2025, 1, 8, 10, 0)
        delay = scheduler.add_random_delay_after_init()
        assert isinstance(delay, timedelta)
        assert delay.total_seconds() > 0

    @patch("app.scheduler.scheduler.EmailScheduler.get_current_time")
    def test_evening_delay(self, mock_time):
        scheduler = EmailScheduler(enable_loggin_info=False)
        mock_time.return_value = datetime.datetime(2025, 1, 8, 15, 0)  # 3 PM
        delay = scheduler.add_random_delay_after_init()
        assert isinstance(delay, timedelta)
        assert delay.total_seconds() > 0

    @patch("app.scheduler.scheduler.EmailScheduler.get_current_time")
    def test_noon_delay(self, mock_time):
        scheduler = EmailScheduler(enable_loggin_info=False)
        mock_time.return_value = datetime.datetime(2025, 1, 8, 12, 0)  # 12 PM
        delay = scheduler.add_random_delay_after_init()
        assert isinstance(delay, timedelta)
        assert 4185 <= delay.total_seconds() <= 4365


class TestRandomEmailIntervalBetweenDelivery:
    @patch("time.sleep")
    def test_default_interval(self, mock_sleep):
        scheduler = EmailScheduler(enable_loggin_info=False)
        scheduler.random_email_interval_between_delivery()

        mock_sleep.assert_called_once()
        call_args = mock_sleep.call_args[0][0]
        assert 15 <= call_args <= 90

    @patch("time.sleep")
    def test_custom_interval(self, mock_sleep):
        scheduler = EmailScheduler(enable_loggin_info=False)
        scheduler.random_email_interval_between_delivery(
            max_seconds=120, min_seconds=30
        )
        mock_sleep.assert_called_once()
        call_args = mock_sleep.call_args[0][0]
        assert 30 <= call_args <= 120


class TestCheckHourlyEmailRateLimit:
    def test_under_hourly_limit(self):
        scheduler = EmailScheduler(enable_loggin_info=True, max_email_an_hour=30)
        scheduler.email_sent_during_an_hour = 10
        result, message = scheduler.check_hourly_email_rate_limit()
        assert result
        assert "still good to go" in message

    def test_over_hourly_limit(self):
        scheduler = EmailScheduler(max_email_an_hour=30, enable_loggin_info=False)
        scheduler.email_sent_during_an_hour = 35
        result, message = scheduler.check_hourly_email_rate_limit()
        assert result == False
        assert "WARNING" in message


class TestLogging:
    """Test logging functionality"""

    def test_logging_enabled(self):
        with patch("logging.basicConfig") as mock_config:
            scheduler = EmailScheduler(enable_loggin_info=True)
            mock_config.assert_called_once()

    def test_logging_disabled(self):
        with patch("logging.basicConfig") as mock_config:
            scheduler = EmailScheduler(enable_loggin_info=False)
            mock_config.assert_not_called()
