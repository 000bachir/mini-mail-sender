import time as time_module
import random
import datetime
from datetime import datetime, timedelta, time
from typing import Any, Optional, Callable, Union, Tuple
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
        # rule of thumb use "time" when for comparing or checking the time and timedelta for operation like adding
        buisness_hours_starting=time(9, 0),
        buisness_hours_ending=time(17, 0),
        daily_batch_emails=100,
        variation=random.randint(-10, 25),
        # max_email_a_day=70,
        max_email_an_hour=30,
        enable_loggin_info: bool = True,
    ):
        # when the program will fire it will a time interval until it starts sending depending on the time
        self.morning_intervals = [
            timedelta(hours=0, minutes=10, seconds=20),
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
        self.noon_interval = timedelta(hours=1, minutes=10, seconds=45)

        # buisness hours set up

        self.buisness_hours_starting = buisness_hours_starting
        self.buisness_hours_ending = buisness_hours_ending

        # rate limit of sending emails
        self.max_email_an_hour = max_email_an_hour
        self.max_email_a_day = daily_batch_emails + variation

        # emails quotas a day and an hour
        self.max_email_an_hour = max_email_an_hour
        self.max_email_a_day = daily_batch_emails + variation

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
        # enable loggins
        self.logger.info("Email scheduler class is being initiated\n")

    def get_current_time(self) -> datetime:
        try:
            return datetime.now()
        except Exception as e:
            self.logger.error(
                f"the get_current_time method crashed please check error : {e}\n"
            )
            raise

    def checking_buisness_hours(self, check_time: Optional[datetime] = None) -> bool:
        if check_time is None:
            check_time = self.get_current_time()
        # chekc if it is the weekend :
        if check_time is not None:
            if check_time.weekday() >= 5:
                self.logger.warning(
                    "please reconsider your choice and avoid using this tool on weekend to not be flaged by google bots \n"
                )
                return False
        current_time = check_time.time()
        if self.buisness_hours_starting <= current_time <= self.buisness_hours_ending:
            self.logger.info("THE WINDOW OF ACTION IS GOOD TO GO \n")
            return True
        else:
            return False

    def add_random_delay_after_init(self):
        try:
            current_time = self.get_current_time()
            current_hour = current_time.hour

            if current_hour < 12:
                base_delay = random.choice(self.morning_intervals)
                jitter = timedelta(seconds=random.randint(-60, 120))
                final_delay = base_delay + jitter
            elif current_hour == 12:
                base_delay = self.noon_interval
                jitter = timedelta(seconds=random.randint(-60, 120))
                final_delay = base_delay + jitter

            else:
                base_delay = random.choice(self.evening_intervals)
                jitter = timedelta(seconds=random.randint(-30, 90))
                final_delay = base_delay + jitter
            return final_delay
        except Exception as e:
            self.logger.error(
                f"error could not lunch the function add_random_delay_after_init : {e}\n"
            )
            raise

    def random_email_interval_between_delivery(
        self, max_seconds: int = 90, min_seconds: int = 15
    ):
        wait_time = random.randint(min_seconds, max_seconds)
        self.logger.warning(
            f"to not being flagged by robots we need to simulate some type of sleep between each email sent {wait_time}\n"
        )
        time_module.sleep(wait_time)

    def check_hourly_email_rate_limit(self) -> tuple[bool, str]:
        try:
            if self.email_sent_during_an_hour >= self.max_email_an_hour:
                return (
                    False,
                    f"WARNING max email an hour has been reached {self.max_email_an_hour}\n",
                )
            elif self.email_sent_during_an_hour < self.max_email_a_day:
                return (
                    True,
                    f"still good to go for the hour the limit is {self.max_email_a_day}\n",
                )
            else:
                return False, "Unexpected condition occured\n"
        except Exception as e:
            self.logger.error(
                f"the function check_hourly_email_rate_limit has crashed see error : {e}\n"
            )
            raise

    def check_daily_email_rate_limit(self) -> tuple[bool, str]:
        try:
            if self.email_sent_during_a_day >= self.max_email_a_day:
                return (
                    False,
                    f"WARNING max email an a day has been reached {self.max_email_a_day}\n",
                )
            elif self.email_sent_during_a_day < self.max_email_a_day:
                return (
                    True,
                    f"still good to go for the hour the limit is {self.max_email_a_day}\n",
                )
            else:
                return False, "Unexpected condition occured\n"
        except Exception as e:
            self.logger.error(
                f"the function check_hourly_email_rate_limit has crashed see error : {e}\n"
            )
            raise
