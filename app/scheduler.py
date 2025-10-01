"""
to handle the schedule of sending email like splitting the 24h into chuncks
"""

"""
the purpose of this file is to create a scheduler
    this scheduler will act on a certain window of time and these laps of time some opereation will be executed
    what do i need to do first : 
        1- keep track of the exact time and the time zone ==== done 
        2- define the time to perfom operations ==== done
        3- create a function that will add time randomly
"""


# python representation of the 24h accepted :
# the_hour_of_the_day = "23:59:59.999999"
# to add time i need to use timedelta() only works on returned object of datetime
#
#
#


from re import error
from time import gmtime, strftime
from datetime import date, datetime, timedelta
from typing_extensions import NoExtraItems
import random

# this function will determine the time must run


def retreaving_the_current_time():
    try:
        current_time = datetime.now()
        return current_time
    except Exception as e:
        raise error(f"could not proccede with the retreival operation : {e}")


def retreiving_the_local_time_zone():
    try:
        local_tz = datetime.now().astimezone().tzinfo
        now = datetime.now()
        local_now = now.astimezone()
        local_tz = local_now.tzname()
        if local_tz is None:
            raise RuntimeError(
                "error could not retreive the local time zone please check again"
            )
        return local_tz
    except Exception as e:
        raise error(f"error : {e}")


def adding_time_randomely() -> timedelta:
    interval_of_times = {
        "morning": [
            timedelta(hours=2, minutes=0, seconds=20),
            timedelta(hours=1, minutes=20),
            timedelta(hours=1, minutes=40),
            timedelta(hours=1),
        ],
        "evening": [
            timedelta(hours=1, minutes=0, seconds=35),
            timedelta(hours=1, minutes=15),
            timedelta(minutes=33),
            timedelta(minutes=47, seconds=56),
        ],
    }
    try:
        now = retreaving_the_current_time()
        random_time_morning = random.choice(interval_of_times["morning"])
        random_time_evening = random.choice(interval_of_times["evening"])
        if now.hour < 12:
            return random_time_morning
        elif now.hour > 12:
            return random_time_evening
    except Exception as e:
        raise RuntimeError(
            f"error happened during the random adding of an arbitrary time of action : {e}"
        )


def time_manipulation() -> None:
    # retreived the current time plus the timezone
    try:
        timenow = retreaving_the_current_time()
        if timenow is None:
            raise RuntimeError("error could not retreive the current time")
        local_time_zone = retreiving_the_local_time_zone()
        print(
            "this comes from a function above : ",
            timenow.strftime("%H:%M:%S %p"),
            local_time_zone,
        )
        added_time = timenow + timedelta(hours=10)
        new_time = added_time.strftime("%H:%M:%S %p")
        print("the added time becomes like this : ", new_time)
        random_choice = adding_time_randomely()
        print("test : ", random_choice)
        another_time = timenow + random_choice
        print("another time : ", another_time.strftime("%H:%M:%S %p"))
    except Exception as e:
        raise error(e)


time_manipulation()
