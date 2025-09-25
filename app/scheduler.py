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
from datetime import datetime, timedelta
import threading


def retreiving_the_current_time():
    try:
        current_time = datetime.now()
        current_time_formated = current_time.strftime("%H:%M:%S")
        time_zone_location = current_time.astimezone().tzinfo
        localtime = time.localtime()
        if current_time == "" and time_zone_location == "":
            raise error(
                "error couldn't retreive the current time nor the exact time zone"
            )
        else:
            print(
                f"the current time is : {current_time.strftime('%H:%M:%S')} and the timezone is {time_zone_location}"
            )
            if localtime.tm_hour < 12:
                print(f"and it's {current_time_formated} am in the morning")
            else:
                if localtime.tm_hour > 12:
                    print(f"and it's {current_time_formated} pm in the evening")
    except Exception as e:
        print(
            f"ERROR could not retreive time infos please check the console for errors : {e}"
        )


def target_time_for_operation():
    timenow = retreiving_the_current_time()
    print("this the current time", timenow)

    timer = threading.Timer(10)
    timer.start()
    try:
        user_input = input(
            "please enter the amount of time you want the program to run : "
        )
        added_time = retreiving_the_current_time() + timedelta(hours=10)
        print(
            f"you entered {user_input} and based on the current time {timenow} the program will end his task at "
        )
    except Exception as e:
        print("error", e)


target_time_for_operation()
