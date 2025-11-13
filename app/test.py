import random
from enum import Enum
from typing import Optional, List, Callable, Tuple, dataclass_transform
from datetime import date, datetime, timedelta, time as dt_time


buisness_hours_starting: dt_time = dt_time(9, 0)
buisness_hours_ending: dt_time = dt_time(17, 0)
rate_limit_email_per_hour: int = 15
rate_limit_email_per_day: int = 50


def cheking_buisness_hours():
    # buisness_hours = buisness_hours_starting
    current_time = datetime.now().strftime("%H:%M:%S")
    print(current_time)
    if current_time == buisness_hours_starting:
        print("the time is good to start the program")
    elif current_time == buisness_hours_ending:
        print("time to end the program life cycle")
    else:
        print("outside of working scope")


print("helll ")


def check_time():
    check_time = datetime.now()
    print(check_time)
    if check_time.weekday() >= 5:
        print("the weekdays have been hits no more email to be sent")
    current_time = check_time.time()
    print(current_time)
    if buisness_hours_ending <= current_time <= buisness_hours_ending:
        print("the window of action is good")
        return True
    else:
        return False


check_time()
