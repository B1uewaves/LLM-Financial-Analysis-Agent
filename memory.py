from langchain.memory.chat_message_histories import RedisChatMessageHistory
from langchain.memory import ConversationBufferMemory
import os

def get_memory(session_id: str = "default-session", redis_url: str = "redis://redis:6379"):
    """
    Initializes a Redis-backed conversation memory.

    Args:
        session_id (str): Unique identifier for the conversation.
        redis_url (str): Redis server URL.

    Returns:
        ConversationBufferMemory: Configured memory object.
    """
    redis_url = redis_url or os.getenv("REDIS_URL", "redis://redis:6379")
    message_history = RedisChatMessageHistory(
        session_id = session_id,
        url = redis_url
    )


    return ConversationBufferMemory(
        chat_memory=message_history,
        return_messages=True
    )