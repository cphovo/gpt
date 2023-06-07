from bson import ObjectId
from pydantic import BaseModel, Field, validator
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")


def get_database():
    """ Return the database """
    client = MongoClient(CONNECTION_STRING)
    return client['tool_kit_with_gpt']


class ChatGPTConversationBase(BaseModel):
    id: str | ObjectId | None = Field(None, alias="_id")
    conversation_id: str | None = None
    parent_id: str | None = None
    title: str
    plus: bool = False

    @validator('id')
    def parse_object_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        arbitrary_types_allowed = True


class ChatGPTConversation(ChatGPTConversationBase):
    question: str
    content: str
    plus: bool = False


def save_chat_gpt_conversation(conversation: ChatGPTConversation):
    dbname = get_database()
    collection_name = dbname["chatgpt"]
    collection_name.insert_one(conversation.dict())


def list_chat_gpt_conversations(skip: int = 0, limit: int = 10) -> list[ChatGPTConversationBase]:
    dbname = get_database()
    collection_name = dbname["chatgpt"]
    return [ChatGPTConversationBase(**doc)
            for doc in collection_name.find().sort([("_id", -1)]).skip(skip).limit(limit)]


def get_chat_gpt_conversation_by_id(id: str):
    dbname = get_database()
    collection_name = dbname["chatgpt"]
    conversation = collection_name.find_one({"_id": ObjectId(id)})
    return ChatGPTConversation(**conversation) if conversation else None


def get_chat_gpt_conversations(conversation_id: str):
    dbname = get_database()
    collection_name = dbname["chatgpt"]
    return [ChatGPTConversation(**doc) for doc in collection_name.find({"conversation_id": conversation_id})]


if __name__ == "__main__":
    print(list_chat_gpt_conversations())
