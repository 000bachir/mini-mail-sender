import time
import random
from datetime import date, datetime, timedelta
from typing import Optional, Callable
from typing import List, Optional, Callable, Tuple
from datetime import datetime, timedelta, time as dt_time
from enum import Enum
import logging


class PriorityState(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class EmailScheduler:
    """
    A scheduler that mimics human-like timing patterns for sending emails.
    Helps avoid detection by automated spam filters through randomized delays.
    """

    def __init__(
        self,
        max_email_a_day=70,
        max_email_an_hour=30,
        buisness_hours_starting: dt_time = dt_time(9, 0),
        buisness_hours_ending: dt_time = dt_time(17, 0),
        enable_loggin_info: bool = True,
    ):
        # when the program will fire it will a time interval until it starts sending depending on the time
        self.morning_intervals = [
            timedelta(hours=1, minutes=10, seconds=20),
            timedelta(hours=1, minutes=20, seconds=45),
            timedelta(hours=1, minutes=30, seconds=35),
            timedelta(hours=1, minutes=0, seconds=59),
        ]
        # when the program will fire it will a time interval until it starts sending depending on the time
        self.evening_intervals = [
            timedelta(hours=1, minutes=0, seconds=35),
            timedelta(hours=1, minutes=15),
            timedelta(minutes=33),
            timedelta(minutes=47, seconds=56),
        ]
        # if it is noon then am only gonna skip the lunch time
        self.noon_interval = timedelta(hours=1, minutes=5, seconds=45)

        # buisness hours set up
        self.buisness_hours_starting: dt_time = buisness_hours_starting
        self.buisness_hours_ending: dt_time = buisness_hours_ending

        # rate limit of sending emails
        self.max_email_an_hour = max_email_an_hour
        self.max_email_a_day = max_email_a_day
        # enable loggins
        self.enable_loggin_info = enable_loggin_info

        # emails quotas a day and an hour
        self.max_email_an_hour = max_email_an_hour
        self.max_email_a_day = max_email_a_day

        # tracking metricks
        self.email_sent_during_an_hour = 0
        self.email_sent_during_a_day = 0
        self.current_hour_start = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        self.current_day_start = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        if enable_loggin_info:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )
        self.logger = logging.getLogger(__name__)

    def get_current_time(self) -> datetime:
        """Retrieve the current system time."""
        try:
            return datetime.now()
        except Exception as e:
            raise RuntimeError(f"Could not retrieve current time: {e}")

    def get_local_timezone(self) -> str:
        """Retrieve the local timezone name."""
        try:
            local_now = datetime.now().astimezone()
            local_tz = local_now.tzname()

            if local_tz is None:
                raise RuntimeError("Could not retrieve local timezone")

            return local_tz
        except Exception as e:
            raise RuntimeError(f"Could not retrieve local timezone: {e}")

    # check if it is buisness hour
    def is_buisness_hours(self, check_time: Optional[datetime] = None) -> bool:
        # check if a time has been given
        if check_time is None:
            check_time = self.get_current_time()
        # check if it is the week end
        if check_time.weekday() >= 5:
            logging.info(
                "avoid using the program during week ends to avoid being flagged by google bots"
            )
            return False
        current_time = check_time.time()
        # this will check if the time of action is between 9 and 17 normal hour rate of working
        if (
            self.buisness_hours_starting <= current_time
            and current_time <= self.buisness_hours_ending
        ):
            logging.info("the window of action is acceptable by the program")
            return True
        else:
            return False

    def get_random_delay_to_start_sending(
        self, priority: PriorityState = PriorityState.NORMAL
    ):
        """
        Get a random delay based on current time of day.
        in a more dumb way this will select the time of action
        to be clear let say you start the program at 9 in the morning
        the program will add a random value of time before starting to send emails
        """
        try:
            now = self.get_current_time()
            hour = now.hour

            if hour < 12:
                base_delay = random.choice(self.morning_intervals)
            elif hour == 12:
                base_delay = self.noon_interval
            else:
                base_delay = random.choice(self.evening_intervals)

            # adjusting based on priority
            if priority == PriorityState.URGENT:
                base_delay = base_delay * 0.3
            elif priority == PriorityState.HIGH:
                base_delay = base_delay * 0.6
            elif priority == PriorityState.LOW:
                base_delay = base_delay * 1.2

        except Exception as e:
            raise RuntimeError(f"Error calculating random delay: {e}")

    def schedule_next_run(self, callback: Optional[Callable] = None) -> datetime:
        """
        Schedule the next email send with human-like randomization.
        Args:
            callback: Optional function to call when the scheduled time is reached
        Returns:
            The datetime when the next action will occur
        """
        try:
            current_time = self.get_current_time()
            timezone = self.get_local_timezone()
            delay = self.get_random_delay_to_start_sending()
            scheduled_time = current_time + delay

            logging.info(
                f"Current time: {current_time.strftime('%H:%M:%S %p')} {timezone}"
            )
            logging.info(f"Random delay: {delay}")
            logging.info(
                f"Scheduled send time: {scheduled_time.strftime('%H:%M:%S %p')}"
            )
            logging.info(f"Waiting until {scheduled_time.strftime('%H:%M:%S %p')}...")
            # Wait until scheduled time
            while datetime.now() < scheduled_time:
                time.sleep(1)
            logging.warning(
                f"Scheduled time reached at {datetime.now().strftime('%H:%M:%S %p')}"
            )
            # Execute callback if provided
            if callback:
                callback()

            return scheduled_time

        except Exception as e:
            raise RuntimeError(f"Error during scheduling: {e}")

    def wait_random_interval(
        self, min_seconds: int = 30, max_seconds: int = 180
    ) -> None:
        """
        Waiting for a random interval between min and max seconds after each email is sent
        """
        wait_time = random.randint(min_seconds, max_seconds)
        logging.info(f"Waiting {wait_time} seconds before next action...")
        time.sleep(wait_time)

    def reset_hourly_counter(self) -> None:
        """Reset the hourly email counter if an hour has passed."""
        now = self.get_current_time()
        current_hour = now.replace(minute=0, second=0, microsecond=0)
        if current_hour > self.current_hour_start:
            self.emails_sent_current_hour = 0
            self.current_hour_start = current_hour
            self.logger.info("Hourly counter reset")

    def reset_daily_counter(self) -> None:
        """Reset the daily email counter if a day has passed."""
        now = self.get_current_time()
        current_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if current_day > self.current_day_start:
            self.emails_sent_today = 0
            self.current_day_start = current_day
            self.logger.info("Daily counter reset")

    def check_email_max_rate(self) -> Tuple[bool, str]:
        self.reset_hourly_counter()
        self.reset_daily_counter()

        if self.emails_sent_current_hour >= self.max_email_an_hour:
            return (
                False,
                f"warning the hourly quotas of emails has been reached ({self.max_email_an_hour}/hour)",
            )

        if self.email_sent_during_a_day >= self.max_email_a_day:
            return False, "warning the daily quotas of emails in 24h has been reached"
        return True, "GOOD the quotas are respected"

    def reset_daily_email_counter(self) -> None:
        now = self.get_current_time()
        current_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if current_day > self.current_day_start:
            self.email_sent_during_a_day = 0
            self.current_day_start = current_day
            self.logger.info("daily email quotas a day has been reached")

    def get_next_buisness_hour(self):
        now = self.get_current_time()
        next_time = now

        if next_time.weekday() >= 5:
            self.logger.info(
                "this is the weekend the program will skip to the next day"
            )
            next_time += timedelta(days=1)

        next_time = next_time.replace(
            self.buisness_hours_starting.hour,
            self.buisness_hours_starting.minute,
            second=0,
            microsecond=0,
        )

        if now.time() >= self.buisness_hours_ending:
            next_time += timedelta(days=1)
            while next_time.weekday() >= 5:
                next_time += timedelta(days=1)
        return next_time

    # this function has been generated by claude :
    def calculate_next_send_time(
        self,
        suggested_time,
        priority: PriorityState = PriorityState.NORMAL,
        respected_buisness_hours: bool = True,
    ) -> datetime:
        now = self.get_current_time()
        delay = self.get_random_delay_to_start_sending(priority)
        if delay is not None and now is not None:
            suggested_time = now + delay
        if respected_buisness_hours:
            if not self.is_buisness_hours(suggested_time):
                next_buisness_hour = self.get_next_buisness_hour()
                random_start_delay = timedelta(minutes=random.randint(5, 30))
                suggested_time = next_buisness_hour + random_start_delay
                self.logger.info(
                    f"adjusted to the next buisness hour : {suggested_time}"
                )

        return suggested_time
