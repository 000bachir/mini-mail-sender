from typing import Union
from dotenv import load_dotenv
from fastapi import FastAPI
from app.supabase.supabaseClient import DatabaseOperation
# TODO : instead of using asyncio i could uvloop it faster and handle connections better

app = FastAPI()


@app.get("/")
def load_emails():
    try:
        loading_emails = DatabaseOperation()
        connection = loading_emails.load_and_check_connection()
        if connection is None:
            return {"message": "could not check the database"}
        return connection
    except Exception as e:
        print("error: ", e)
