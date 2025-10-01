"""
to handle the schedule of sending email like splitting the 24h into chuncks
"""

"""
the purpose of this file is to create a scheduler
    this scheduler will act on a certain window of time and these laps of time some opereation will be executed
    what do i need to do first : 
        1- keep track of the exact time and the time zone ==== done 
        2- define the time to perfom operations 
"""


# python representation of the 24h accepted :
# the_hour_of_the_day = "23:59:59.999999"
from re import error
import time, sched
from time import gmtime, strftime
from datetime import date, datetime, timedelta
import threading


def retreaving_the_current_time():
    try:
        current_time = datetime.now()
        if not current_time:
            print("error could not retreive the current time please check again")
            return False
        else:
            return current_time

    except Exception as e:
        raise error(f"could not proccede with the retreival operation : {e}")


def retreiving_the_local_time_zone() -> datetime:
    try:
        local_tz = datetime.now().astimezone().tzinfo
        now = datetime.now()
        local_now = now.astimezone()
        local_tz = local_now.tzinfo
        if local_tz is None:
            raise RuntimeError(
                "error could not retreive the local time zone please check again"
            )
        return local_tz
    except Exception as e:
        raise error(f"error : {e}")


def time_manipulation() -> None:
    timenow = retreaving_the_current_time()
    local_time_zone = retreiving_the_local_time_zone()
    print(
        "this comes from a function above : ",
        timenow.strftime("%H:%M:%S"),
        local_time_zone,
    )
    added_time = timenow + timedelta(hours=10)
    new_time = added_time.strftime("%H:%M:%S")
    print("the added time becomes like this : ", new_time)


time_manipulation()
