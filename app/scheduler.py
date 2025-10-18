from re import error
from time import strftime
from datetime import datetime, timedelta
import random
import time

"""
to handle the schedule of sending email like splitting the 24h into chuncks
"""

"""
the purpose of this file is to create a scheduler
    this scheduler will act on a certain window of time and these laps of time some opereation will be executed
    what do i need to do first : 
        1- keep track of the exact time and the time zone ==== done 
        2- define the time to perfom operations ==== done
        3- create a function that will add time randomly ==== done
        4- manipulate the time where the program has to stop ==== done
"""

# python representation of the 24h accepted :
# the_hour_of_the_day = "23:59:59.999999"
# to add time i need to use timedelta() only works on returned object of datetime


def retrieve_current_time():
    try:
        current_time = datetime.now()
        return current_time
    except Exception as e:
        raise error(f"could not proccede with the retreival operation : {e}")


def retrieve_local_timezone():
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
        raise RuntimeError(
            f"error could not retreive the current local time zone : {e}"
        )


def add_time_randomly() -> timedelta:
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
        now = retrieve_current_time()
        random_time_morning = random.choice(interval_of_times["morning"])
        random_time_evening = random.choice(interval_of_times["evening"])
        if now.hour < 12:
            return random_time_morning
        elif now.hour > 12:
            return random_time_evening
        elif now.hour == 12:
            return timedelta(days=0, hours=1, minutes=0, seconds=0)
    except Exception as e:
        raise RuntimeError(
            f"error happened during the random adding of an arbitrary time of action : {e}"
        )


def time_manipulation() -> None:
    # retreived the current time plus the timezone
    try:
        timenow = retrieve_current_time()
        if timenow is None:
            raise RuntimeError("error could not retreive the current time")
        local_time_zone = retrieve_local_timezone()
        print(
            "retreiving the current time with the time zone : ",
            timenow.strftime("%H:%M:%S %p"),
            local_time_zone,
        )  # this comes from the function above
        random_choice = add_time_randomly()
        print(f"randomly adding {random_choice}")
        cumulated_time = timenow + random_choice  # the time to stop the program
        formated_cumulated_time = cumulated_time.strftime("%H:%M:%S %p")
        print("the cumulated time becomes : ", cumulated_time.strftime("%H:%M:%S %p"))
        print(
            f"please keep in mind the program will stop executing once the : {formated_cumulated_time} is reached"
        )
        increment_time_value_in_second = timedelta(
            days=0, hours=0, minutes=0, seconds=1
        )
        increment_time_value_in_seconds = timedelta(
            days=0, hours=0, minutes=0, seconds=10
        )

        while timenow < cumulated_time:
            time.sleep(1)
            if random_choice > timedelta(days=0, hours=1, minutes=0, seconds=0):
                timenow += increment_time_value_in_seconds
            else:
                timenow += increment_time_value_in_second
            print(timenow.strftime("%H:%M:%S"))
            if timenow == cumulated_time:
                print("the program has reached it end")
                break
    except Exception as e:
        raise RuntimeError(
            f"error while procceding with the time manipulation and : {e}"
        )


time_manipulation()
