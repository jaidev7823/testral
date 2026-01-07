from typing import Union
import os

from fastapi import FastAPI

from pymongo import MongoClient

app = FastAPI()


@app.on_event("startup")
def startup_event():
    mongo_url = os.getenv("MONGO_URL", "mongodb://mongo:27017")
    try:
        client = MongoClient(mongo_url)
        client.admin.command("ping")
        app.state.mongo_client = client
        print(f"Connected to MongoDB at {mongo_url}")
    except Exception as e:
        app.state.mongo_client = None
        print(f"Warning: could not connect to MongoDB: {e}")


@app.on_event("shutdown")
def shutdown_event():
    client = getattr(app.state, "mongo_client", None)
    if client:
        client.close()
        print("Closed MongoDB connection")


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}