from langchain.memory.chat_message_histories import RedisChatMessageHistory
from langchain.memory import ConversationBufferMemory

def get_memory(session_id: str = "default-session", redis_url: str = "redis://localhost:6379"):
    """
    Initializes a Redis-backed conversation memory.

    Args:
        session_id (str): Unique identifier for the conversation.
        redis_url (str): Redis server URL.

    Returns:
        ConversationBufferMemory: Configured memory object.
    """
    message_hostory = RedisChatMessageHistory(
        session_id = session_id,
        url = redis_url
    )

    memory = ConversationBufferMemory(
        chat_memory = message_history,
        return_messages = True
    )

    return memory