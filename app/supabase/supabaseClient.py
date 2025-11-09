"""
supabase integration
"""

import datetime
import re
from realtime import dataclass
from supabase import Client, create_client
from config import loading_env_variables
from typing import Union

"""
    what do i need to do to make the script works just like i intend to : 

        2- check if the email is a valid email ==== done
        3- test the database with email ==== done
        4-  a function that will count how many rows i have ==== done
        5- a function that will print only the email that i have with no count 
        
"""


#! env var keys
url = loading_env_variables("PROJECT_URL") or ""
key = loading_env_variables("ANON_PUBLIC_KEY") or ""

#! init the supabase client
supabase_client: Client = create_client(url, key)

# global timestamp
timestamp = datetime.datetime.now(datetime.UTC).isoformat()


# email record
@dataclass
class EmailRecord:
    email: str
    added_at: Union[datetime.datetime, str]
    last_contacted_at: Union[datetime.datetime, str]
    status: str = ""  # en attente , en cours d'envoie , operation fini
    full_name: str = ""
    category: str = ""
    language: str = ""
    source: str = ""
    notes: str = ""


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


def checking_for_dupalicates(record: EmailRecord):
    try:
        duplicate = (
            supabase_client.table("email")
            .select("email")
            .eq("email", record.email)
            .execute()
        )
        if duplicate.data:
            print(
                f"the email provided already exist in the database : {record.email} skipping"
            )
    except Exception as e:
        raise RuntimeError(
            f"failed checking for duplicate in the database please check the error above : {e}"
        )


def valid_record_needed(record: EmailRecord):
    required_fields = {
        "email": record.email,
        "language": record.language,
        "source": record.source,
        "status": record.status,
    }
    for field_name, value in required_fields.items():
        if not value:
            raise ValueError(f"error the field {field_name} is required")
    return True


# seeding the database with test emails :
def seeding_the_database(record: EmailRecord):
    seeding = None
    valid_email_pattern(record.email)
    valid_record_needed(record)
    # time of seeding :
    try:
        # normalizing timestamp
        if isinstance(record.added_at, str):
            record.added_at = datetime.datetime.now().isoformat()
        elif isinstance(record.last_contacted_at, str):
            record.last_contacted_at = record.added_at = (
                datetime.datetime.now().isoformat()
            )
        else:
            seeding = (
                supabase_client.table("emails")
                .insert(
                    {
                        "email": record.email,
                        "full_name": record.full_name,
                        "category": record.category,
                        "language": record.language,
                        "source": record.source,
                        "added_at": record.added_at,
                        "status": record.status,
                        "notes": record.notes,
                        "last_contacted_at": record.last_contacted_at,
                    }
                )
                .execute()
            )
        if seeding and seeding.data is not None:
            print("the seeding of the database has been successful")

    except Exception as e:
        raise RuntimeError(
            f"failed to seed the database with data please check the error : {e}"
        )


seeding_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
record = EmailRecord(
    email=mock_email,
    added_at=seeding_time,
    last_contacted_at=seeding_time,
    status="pending",
    language="english",
    notes="no note",
    category="teaching",
    full_name="bachir",
    source="linkedin",
)
seeding_the_database(record)


def countRows():
    try:
        rows = supabase_client.table("emails").select("*", count="exact").execute()
        print(f"the number of rows in the database are : {rows.count}")
        if rows.count == 0:
            print("the database has no rows inside of it")
    except Exception as e:
        raise RuntimeError(
            f"error could not retreive how many rows are in the database for more info please check the error : {e}"
        )


def FetchEmails():
    try:
        fetch = supabase_client.table("emails").select("email").execute()
        if fetch and fetch.data is None:
            print("failed to fetch all of the email from the database")
        else:
            print(f"email fetched : {fetch.data}")
    except Exception as e:
        raise RuntimeError(
            f"error operating the fetch request onto the database please check the error : {e}"
        )


FetchEmails()


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
