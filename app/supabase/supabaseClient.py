"""
supabase integration
"""

import datetime
from realtime import dataclass
from supabase import Client, create_client
from config import loading_env_variables
from typing import Union
import logging
from utils.valid_email_check import UserManager

"""
    what do i need to do to make the script works just like i intend to : 

        2- check if the email is a valid email ==== done
        3- test the database with email ==== done
        4-  a function that will count how many rows i have ==== done
        5- a function that will print only the email that i have with no count ==== done
        
"""
#! env var keys
url = loading_env_variables("PROJECT_URL") or ""
key = loading_env_variables("ANON_PUBLIC_KEY") or ""

#! init the supabase client
supabase_client: Client = create_client(url, key)

# global timestamp
# timestamp = datetime.datetime.now(datetime.UTC).isoformat()
seeding_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

# logging global variabele
is_loggin: bool = True


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


class DatabaseOperation:
    def __init__(self, enable_loggin: bool = True):
        self.client = supabase_client

        # logging setup
        if enable_loggin:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )
        self.logger = logging.getLogger(__name__)

    """
        checking the health of the database
    """

    def check_health(self):
        seeding_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        try:
            self.client.table("healthcheck").insert(
                {"status": "connection confirmed", "timestamp": seeding_time}
            ).execute()
        except Exception as e:
            self.client.table("healthcheck").insert(
                {
                    "status": f"failed to check the database health of the connection cause : {e} ",
                    "timestamp": seeding_time,
                }
            ).execute()
            return False

    """

    checking the connection

    """

    def load_and_check_connection(self):
        try:
            response_check = (
                self.client.table("healthcheck")
                .select("*")
                .order("timestamp", desc=True)
                .limit(1)
                .execute()
            )
            if response_check.data:
                latest = response_check.data[0]
                logging.info(f"status: {latest['status']} at {latest['timestamp']}")
                return latest
            return False
        except Exception as e:
            raise RuntimeError(f"check failed please see the error above: {e}")

    """
        valid email patterns
    """

    # def valid_email_pattern(self, email: str):
    #     pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    #     if re.fullmatch(pattern, email):
    #         logging.info("the email provided is valid")
    #     else:
    #         logging.warning("the email provided doesn't have a valid structure")
    #
    def checking_for_dupalicates(self, record: EmailRecord):
        try:
            duplicate = (
                self.client.table("emails")
                .select("email")
                .eq("email", record.email)
                .execute()
            )
            if duplicate.data:
                self.logger.warning(
                    f"the email provided already exist in the database : {record.email} skipping"
                )
                return True
            return False
        except Exception as e:
            self.logger.error(
                f"failed checking for duplicate in the database please check the error above : {e}"
            )
            raise

    """
        valid email record
    """

    def valid_record_needed(self, record: EmailRecord):
        required_fields = {
            "email": record.email,
            "language": record.language,
            "source": record.source,
            "status": record.status,
        }
        for field_name, value in required_fields.items():
            if not value:
                self.logger.error(f"error the field {field_name} is required")
                raise ValueError
        return True

    """
        seeding the database with test emails 
    """

    def seeding_the_database(self, record: EmailRecord):
        seeding = None
        valid_pattern = UserManager.valid_email_pattern(
            record.email
        )  # check for valid email pattern
        if not valid_pattern:
            self.logger.error("error the email is not in a correct format")
        # check if the required fields are available
        self.valid_record_needed(record)
        duplicates = self.checking_for_dupalicates(record)
        if duplicates:
            self.logger.info(f"email already in the database {record.email}")
            return False
        # time of seeding :
        try:
            logging.warning("the process of seeding the database is being initiated")
            # normalizing timestamp
            if isinstance(record.added_at, str):
                record.added_at = datetime.datetime.now().isoformat()
            if isinstance(record.last_contacted_at, str):
                record.last_contacted_at = record.added_at = (
                    datetime.datetime.now().isoformat()
                )
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
                self.logger.info("the seeding of the database has been successful")

        except Exception as e:
            self.logger.error(
                f"failed to seed the database with data please check the error : {e}"
            )
            raise RuntimeError

    """
        function that will count the number of rows in a database
    """

    def countRows(self):
        try:
            rows = self.client.table("emails").select("*", count="exact").execute()
            logging.info(f"the number of rows in the database are : {rows.count}")
            if rows.count == 0:
                self.logger.info("the database has no rows inside of it")
        except Exception as e:
            self.logger.error(
                f"error could not retreive how many rows are in the database for more info please check the error : {e}"
            )
            raise RuntimeError

    """
        to fetch the emails stored in the database 
    """

    def FetchEmails(self):
        try:
            fetch = self.client.table("emails").select("email").execute()
            if not fetch.data:
                return self.logger.error(
                    "failed to fetch all of the email from the database"
                )
            else:
                self.logger.info(f"email fetched : {fetch.data}")
        except Exception as e:
            self.logger.error(
                f"error operating the fetch request onto the database please check the error : {e}"
            )
            raise RuntimeError
