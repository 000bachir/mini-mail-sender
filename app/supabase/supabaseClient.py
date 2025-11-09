"""
supabase integration
"""

import datetime
import re
from supabase import Client, create_client
from config import loading_env_variables
from typing import Union

"""
    what do i need to do to make the script works just like i intend to : 

        2- check if the email is a valid email
        3- test the database with email ==== done
        4-  a function that will gather all my email that i registred

"""


#! env var keys
url = loading_env_variables("PROJECT_URL") or ""
key = loading_env_variables("ANON_PUBLIC_KEY") or ""

#! init the supabase client
supabase_client: Client = create_client(url, key)

# global timestamp
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
        print("the email provided doesn't have a valid structure")


mock_email = "ykami892@gmail.com"


# seeding the database with test emails :
def seeding_the_database(
    added_at: Union[datetime.datetime, str],
    last_contacted_at: Union[datetime.datetime, str],
    email,
    status: str = "",
    full_name: str = "",
    category: str = "",
    language: str = "",
    source: str = "",
    notes: str = "",
):
    if isinstance(added_at, str):
        added_at = datetime.datetime.now().isoformat()
    if isinstance(last_contacted_at, str):
        last_contacted_at = added_at = datetime.datetime.now().isoformat()
    valid_email_pattern(email)
    # time of seeding :
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
                    "added_at": added_at,
                    "status": status,
                    "notes": notes,
                    "last_contacted_at": last_contacted_at,
                }
            )
            .execute()
        )
        if seeding.data is not None:
            print("the seeding of the database has been successful")
    except Exception as e:
        raise RuntimeError(
            f"failed to seed the database with data please , check the error : {e}"
        )


seeding_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
# seeding_the_database(
#     email=mock_email,
#     added_at=seeding_time,
#     last_contacted_at=seeding_time,
#     language="french",
#     full_name="fadi",
#     status="pending",
#     notes="no note",
#     category="tech",
# )


def gather_all_the_email():
    try:
        response = supabase_client.table("emails").select("*", count="exact").execute()
        print(response.count)
    except Exception as e:
        print(e)


gather_all_the_email()

# if __name__ == "__main__":
#     check_health(supabase_client)
#     print("healthcheck : ", load_and_check_connection())
#     print(
#         "seeding the database",
#         seeding_the_database(
#             added_at=timestamp,
#             last_contacted_at=timestamp,
#             email=email_to_test,
#             category="french",
#             status="pending",
#             source="facebook",
#             notes="testing",
#         ),
#     )
