from typing import Union
from fastapi import FastAPI

# TODO : instead of using asyncio i could uvloop it faster and handle connections better

app = FastAPI()


@app.get("/")
def root_server():
    return {"hello": "world from flask api"}
