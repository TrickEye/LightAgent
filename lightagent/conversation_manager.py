from storage.sqlite import SQLiteStorage
from models import *
from typing import List
import json

class ConversationManager:
    def __init__(self, storage: SQLiteStorage):
        if storage is None:
            self.storage = SQLiteStorage("lightagent.db")
        else:
            self.storage = storage
        storage.create_table("users", "id TEXT PRIMARY KEY, name TEXT, conversation_id_list TEXT")
        storage.create_table("conversations", "id TEXT PRIMARY KEY, user_id TEXT, message_id_list TEXT")
        storage.create_table("messages", "id TEXT PRIMARY KEY, content TEXT, last_modified_datetime TEXT, location TEXT, conversation_id TEXT, enabled_plugins TEXT, inner_tool_invokation_results TEXT, response TEXT")
    
    def __serialize_json(self, obj: dict):
        return json.dumps(obj)
    
    def __deserialize_json(self, str: str):
        return json.loads(str)
    
    def get_message_context(self, message: Message):
        conversation_data = self.storage.get("conversations", f"id = '{message.conversation_id}'")
        conversation = Conversation(
            id=message.conversation_id,
            user_id=conversation_data[1],
            message_id_list=self.__deserialize_json(conversation_data[2])) 
        
        user_data = self.storage.get("users", f"id = '{conversation.user_id}'")
        user = UserProfile(
            id=user_data[0],
            name=user_data[1],
            datetime=message.last_modified_datetime,
            location=message.location
        )

        return Context(
            conversation_id=message.conversation_id,
            conversation_history=[Message(*(self.storage.get("messages", f"id = '{message_id}'"))) for message_id in conversation.message_id_list],
            user_profile=user,
            inner_tool_invokation_results=[]
        )


    def save_message(self, message: Message, context: Context, response: str):
        self.storage.insert("messages", {
            "id": message.id,
            "content": message.content,
            "last_modified_datetime": message.last_modified_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "location": message.location,
            "conversation_id": message.conversation_id,
            "enabled_plugins": self.__serialize_json(message.enabled_plugins),
            "inner_tool_invokation_results": self.__serialize_json(context.inner_tool_invokation_results),
            "response": response
        })

        message_id_list = [msg.id for msg in context.conversation_history]
        message_id_list.append(message.id)
        self.storage.update("conversations", {"message_id_list": self.__serialize_json(message_id_list)}, f"id = '{message.conversation_id}'")

        user_data = self.storage.get("users", f"id = '{context.user_profile.id}'")
        conversation_id_list = self.__deserialize_json(user_data[2])
        conversation_id_list.append(message.conversation_id)
        self.storage.update("users", {"name": context.user_profile.name, "conversation_id_list": self.__serialize_json(conversation_id_list)}, f"id = '{context.user_profile.id}'")
