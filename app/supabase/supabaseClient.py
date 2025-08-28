"""
    supabase integration
"""

from supabase import  create_client , Client
from supabase import Client
import datetime
from app.config import loading_env_variables


#! env var keys
url = loading_env_variables("PROJECT_URL")
key = loading_env_variables("ANON_PUBLIC_KEY")

#! init the supabase client 
supabase_client : Client = create_client(url , key)
timestamp = datetime.datetime.now(datetime.UTC).isoformat()


#! checking the health of the database 
def check_health(client : Client) :
    try :
        client.table('healthcheck').insert({
            "status" : "connection confirmed",
            "timestamp" : timestamp
        }).execute()
    except Exception as e : 
        client.table("healthcheck").insert({
            "status" : 'failed to check the database health of the connection',
            "timestamp" : timestamp
        }).execute()
        return False
#* checking the connection
def load_and_check_connection() :
    try : 
        response_check = supabase_client.table("healthcheck").select("*").order("timestamp", desc=True).limit(1).execute()
        if response_check.data : 
            latest = response_check.data[0]
            print(f"status: {latest['status']} at {latest['timestamp']}")
            return True
        return False
    except Exception as e : 
        raise(f"check failed please see the error above: {e}")
    

if __name__ == '__main__' :
    check_health(supabase_client)
    print("healthcheck : ", load_and_check_connection())

