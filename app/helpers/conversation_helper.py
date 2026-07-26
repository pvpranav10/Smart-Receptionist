import uuid

def generate_conversation_id(phone_number: str) -> str:
    """
    Generates a unique conversation ID using the phone number
    and a random UUID.

    Example:
    conv_7f8a2c1d_9b2d6e1f
    """
    random_part = uuid.uuid4().hex[:8]

    return f"{phone_number}_{random_part}"


# def get_most_recent_conversation_state