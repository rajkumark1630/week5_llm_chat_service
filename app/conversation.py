
import json
import os
from datetime import datetime, timezone


CONVERSATION_FILE = "conversations.json"


def load_conversations():
    """Load saved conversations."""

    if not os.path.exists(CONVERSATION_FILE):
        return {}

    try:
        with open(
            CONVERSATION_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return {}


def save_conversations(conversations):
    """Save conversations to JSON file."""

    with open(
        CONVERSATION_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            conversations,
            file,
            indent=4,
            ensure_ascii=False
        )


def create_conversation(conversation_id):
    """Create a new conversation."""

    conversations = load_conversations()

    if conversation_id in conversations:
        return conversations[conversation_id]

    conversations[conversation_id] = {
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "messages": []
    }

    save_conversations(conversations)

    return conversations[conversation_id]


def add_message(conversation_id, role, content):
    """Add user or assistant message."""

    if role not in ("user", "assistant"):
        raise ValueError("Invalid message role")

    conversations = load_conversations()

    if conversation_id not in conversations:
        create_conversation(conversation_id)
        conversations = load_conversations()

    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat()
    }

    conversations[conversation_id]["messages"].append(
        message
    )

    save_conversations(conversations)

    return message


def get_conversation(conversation_id):
    """Get complete conversation history."""

    conversations = load_conversations()

    return conversations.get(conversation_id)


def get_messages(conversation_id):
    """Get messages for LLM context."""

    conversation = get_conversation(conversation_id)

    if not conversation:
        return []

    return [
        {
            "role": message["role"],
            "content": message["content"]
        }
        for message in conversation["messages"]
    ]


def delete_conversation(conversation_id):
    """Delete a conversation."""

    conversations = load_conversations()

    if conversation_id not in conversations:
        return False

    del conversations[conversation_id]

    save_conversations(conversations)

    return True


def clear_conversations():
    """Delete all conversations."""

    save_conversations({})

    return True
