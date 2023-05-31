from pymongo import MongoClient
import os

CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")


def get_database():
    """ Return the database """
    client = MongoClient(CONNECTION_STRING)
    return client['tool_kit_with_gpt']
