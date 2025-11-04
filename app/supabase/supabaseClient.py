"""
supabase integration
"""

"""
    what do i need to do to make the script works just like i intend to : 
        1- create a supabase table that will store the emails that i wanna send my resume ==== done 
        2- test the database with my emails ====

"""


import datetime
import re

from realtime import dataclass
from supabase import Client, create_client

from config import loading_env_variables
import uuid
import json

#! env var keys
url = loading_env_variables("PROJECT_URL") or ""
key = loading_env_variables("ANON_PUBLIC_KEY") or ""

#! init the supabase client
supabase_client: Client = create_client(url, key)
timestamp = datetime.datetime.now(datetime.UTC).isoformat()


#! checking the health of the database
def check_health(client: Client):
    try:
        client.table("healthcheck").insert(
            {"status": "connection confirmed", "timestamp": timestamp}
        ).execute()
    except Exception as e:
        client.table("healthcheck").insert(
            {
                "status": f"failed to check the database health of the connection cause : {e} ",
                "timestamp": timestamp,
            }
        ).execute()
        return False


# * checking the connection
def load_and_check_connection():
    try:
        response_check = (
            supabase_client.table("healthcheck")
            .select("*")
            .order("timestamp", desc=True)
            .limit(1)
            .execute()
        )
        if response_check.data:
            latest = response_check.data[0]
            print(f"status: {latest['status']} at {latest['timestamp']}")
            return True
        return False
    except Exception as e:
        raise RuntimeError(f"check failed please see the error above: {e}")


def valid_email_pattern(email: str):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if re.fullmatch(pattern, email):
        print("the email provided is valid")
    else:
        print("error the email provided is of format invalid")


# seeding the database with test emails :
def seeding_the_database(
    added_at: datetime.datetime,
    last_contacted_at: datetime.datetime,
    email,
    status: str = "",
    full_name: str = "",
    last_name: str = "",
    category: str = "",
    language: str = "",
    source: str = "",
    note: str = "",
):
    try:
        seeding = (
            supabase_client.table("emails")
            .insert(
                {
                    "email": email,
                    "full_name": full_name,
                    "category": category,
                    "language": language,
                    "source": source,
                    "added_at": timestamp,
                    "status": status,
                    "note": note,
                }
            )
            .execute()
        )
        if seeding.data is not None:
            print("the seeding of the database has been started")
    except Exception as e:
        raise RuntimeError(
            f"failed to seed the database with data please , check the error : {e}"
        )


email = [
    "mobachir2@gmail.com",
]

if __name__ == "__main__":
    check_health(supabase_client)
    print("healthcheck : ", load_and_check_connection())
    print("seeding the database", seeding_the_database())
