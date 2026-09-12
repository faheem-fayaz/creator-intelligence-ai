conversation_memory = {}

# Stores session -> video URL
session_video_context = {}

# Stores session -> AI-generated video context summary
session_context_map = {}


def save_message(session_id, role, content):

    if session_id not in conversation_memory:
        conversation_memory[session_id] = []

    conversation_memory[session_id].append({
        "role": role,
        "content": content
    })


def get_conversation(session_id):

    return conversation_memory.get(session_id, [])


# Save FULL video URL
def set_session_video(session_id, video_url):

    session_video_context[session_id] = video_url


# Get FULL video URL
def get_session_video(session_id):

    return session_video_context.get(session_id)


# Save AI-generated video context summary
def set_session_context(session_id, context):

    session_context_map[session_id] = context


# Retrieve AI-generated context summary
def get_session_context(session_id):

    return session_context_map.get(session_id)