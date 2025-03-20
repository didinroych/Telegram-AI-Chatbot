import json
import os
import logging
from config.config import SESSION_FILE

logger = logging.getLogger(__name__)

# Global sessions dictionary
user_sessions = {}

def init_sessions():
    """Initialize sessions from file or create an empty sessions dict."""
    global user_sessions
    user_sessions = load_sessions()
    logger.info(f"Initialized {len(user_sessions)} user sessions")

def load_sessions():
    """Load sessions from JSON file."""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
        
        # Try to load existing sessions
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, "r") as file:
                return json.load(file)
        return {}
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning(f"Could not load sessions: {e}")
        return {}

def save_sessions():
    """Save current sessions to file."""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
        
        with open(SESSION_FILE, "w") as file:
            json.dump(user_sessions, file, indent=4)
        return True
    except Exception as e:
        logger.error(f"Failed to save sessions: {e}")
        return False

def add_session(user_id, data):
    """Add or update a user session."""
    user_sessions[str(user_id)] = data
    return save_sessions()

def get_session(user_id):
    """Get a user session by ID."""
    return user_sessions.get(str(user_id), {})

def remove_session(user_id):
    """Remove a user session."""
    if str(user_id) in user_sessions:
        del user_sessions[str(user_id)]
        return save_sessions()
    return False