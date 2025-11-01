from typing import Union
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root_server():
    return {"hello": "world from flask api"}
