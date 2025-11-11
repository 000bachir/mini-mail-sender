import re
import time
import random
from datetime import datetime, timedelta
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

    def __init__(self):
        self.morning_intervals = [
            timedelta(hours=1, minutes=10, seconds=20),
            timedelta(hours=1, minutes=20, seconds=45),
            timedelta(hours=1, minutes=30, seconds=35),
            timedelta(hours=1, minutes=0, seconds=59),
        ]
        self.evening_intervals = [
            timedelta(hours=1, minutes=0, seconds=35),
            timedelta(hours=1, minutes=15),
            timedelta(minutes=33),
            timedelta(minutes=47, seconds=56),
        ]
        self.noon_interval = timedelta(hours=1)

        # buisness hours set up
        self.buisness_hours_starting: dt_time = dt_time(9, 0)
        self.buisness_hours_ending: dt_time = dt_time(17, 0)
        self.rate_limit_email_per_hour: int = 15
        self.rate_limit_email_per_day: int = 50

        # rate limit of sending emails
        max_email_an_hour = 15
        max_email_a_day = 50
        # enable loggins 
        enable_loggin_info : bool = True
        # tracking metricks 
        self.email_sent_during_an_hour = 0 
        self.email_sent_during_a_day = 0 
        self.current_hour_start = datetime.now().replace(hour=0 , minute=0 , second=0 , microsecond=0)
        self.current_day_start =  datetime.now().replace(hour=0 , minute=0 , second=0 , microsecond=0)

        if enable_loggin_info : 
            logging.basicConfig(level=logging.INFO format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
            print(
                "avoid using the program during week ends to avoid being flagged by google bots"
            )
            return False
        current_time = check_time.time()
        # this will check if the time of action is between 9 and 17 normal hour rate of working
        if (
            self.buisness_hours_starting <= current_time
            and current_time <= self.buisness_hours_ending
        ):
            print("the window of action is acceptable by the program")
            return True
        else:
            return False

def get_random_delay_to_start_sending(self) -> timedelta:
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
                return random.choice(self.morning_intervals)
            elif hour == 12:
                return self.noon_interval
            else:
                return random.choice(self.evening_intervals)
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

            print(f"Current time: {current_time.strftime('%H:%M:%S %p')} {timezone}")
            print(f"Random delay: {delay}")
            print(f"Scheduled send time: {scheduled_time.strftime('%H:%M:%S %p')}")
            print(f"Waiting until {scheduled_time.strftime('%H:%M:%S %p')}...")

            # Wait until scheduled time
            while datetime.now() < scheduled_time:
                time.sleep(1)

            print(f"Scheduled time reached at {datetime.now().strftime('%H:%M:%S %p')}")

            # Execute callback if provided
            if callback:
                callback()

            return scheduled_time

        except Exception as e:
            raise RuntimeError(f"Error during scheduling: {e}")

    def wait_random_interval(self, min_seconds: int = 30, max_seconds: int = 180) -> None:
        """
        Waiting for a random interval between min and max seconds after each email is sent
        useful for adding variability
        """
        wait_time = random.randint(min_seconds, max_seconds)
        print(f"Waiting {wait_time} seconds before next action...")
        time.sleep(wait_time)
        
    def reset_daily_email_counter(self) -> None : 
        now = self.get_current_time()
        current_day = now.replace(hour=0 , minute=0 , second=0 , microsecond=0)
        if current_day > self.current_day_start : 
            self.email_sent_during_a_day = 0
            self.current_day_start = current_day
            


# Example usage
if __name__ == "__main__":
    scheduler = EmailScheduler()
    # Define what to do when scheduled time is reached
    def send_email():
        print("📧 Sending email now!")
        # Your email sending logic goes here

    # Schedule a single email
    scheduler.schedule_next_run(callback=send_email)

    # Or schedule multiple emails with random intervals
    # for i in range(3):
    #     print(f"\n--- Email {i+1} ---")
    #     scheduler.schedule_next_run(callback=send_email)
    #     if i < 2:  # Don't wait after the last email
    #         scheduler.wait_random_interval(min_seconds=60, max_seconds=300)
