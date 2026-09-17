# backend/memory.py

# --------------------------------------------------
# In-memory conversation storage
# --------------------------------------------------

conversations = {}


# --------------------------------------------------
# Create / get conversation
# --------------------------------------------------

def get_conversation(session_id):

    if session_id not in conversations:

        conversations[session_id] = {
            "environment": {},
            "messages": []
        }

    return conversations[session_id]


# --------------------------------------------------
# Merge dictionaries
# --------------------------------------------------

def merge_dicts(old, new):

    result = old.copy()

    for key, value in new.items():

        if isinstance(value, dict):

            if key not in result:
                result[key] = {}

            result[key] = merge_dicts(
                result[key],
                value
            )

        elif value is not None:

            result[key] = value

    return result


# --------------------------------------------------
# Update environmental information
# --------------------------------------------------

def update_environment(
    session_id,
    environment
):

    conversation = get_conversation(
        session_id
    )

    conversation["environment"] = merge_dicts(
        conversation["environment"],
        environment
    )

    return conversation["environment"]


# --------------------------------------------------
# Add message
# --------------------------------------------------

def add_message(
    session_id,
    role,
    content
):

    conversation = get_conversation(
        session_id
    )

    conversation["messages"].append(
        {
            "role": role,
            "content": content
        }
    )


# --------------------------------------------------
# Get messages
# --------------------------------------------------

def get_messages(session_id):

    conversation = get_conversation(
        session_id
    )

    return conversation["messages"]


# --------------------------------------------------
# Get conversation context
# --------------------------------------------------

def get_context(session_id):

    conversation = get_conversation(
        session_id
    )

    return {
        "environment": conversation["environment"],
        "messages": conversation["messages"]
    }


# --------------------------------------------------
# Format history for Gemini
# --------------------------------------------------

def format_chat_history(session_id, max_messages=10):

    messages = get_messages(
        session_id
    )

    # Only keep recent messages
    messages = messages[-max_messages:]

    if not messages:
        return "No previous conversation."

    history = []

    for message in messages:

        role = message.get(
            "role",
            "user"
        )

        content = message.get(
            "content",
            ""
        )

        if role == "user":
            label = "USER"

        else:
            label = "ASSISTANT"

        history.append(
            f"{label}: {content}"
        )

    return "\n".join(history)