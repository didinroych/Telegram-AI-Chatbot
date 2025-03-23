import logging
import os
from typing import Dict, Optional
import google.generativeai as genai
from langchain.memory import ConversationBufferMemory
from langchain.schema import AIMessage, HumanMessage
from database.session import get_session, add_session, init_sessions
from config.config import APIKEY_GEMINI, GEMINI_MODEL
from datetime import datetime

logger = logging.getLogger(__name__)

# Dictionary to store user-specific memory buffers
user_memories: Dict[int, ConversationBufferMemory] = {}

# Dictionary to store user-specific gemini chat instances
user_chats = {}

def initialize_gemini():
    """Initialize the Gemini API configuration."""
    try:
        # Configure Gemini API
        if not APIKEY_GEMINI:
            logger.error("Gemini API key not configured")
            return False
        
        # Initialize sessions
        init_sessions()
            
        genai.configure(api_key=APIKEY_GEMINI)
        logger.info(f"Successfully initialized Gemini API with model: {GEMINI_MODEL}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize Gemini API: {e}")
        return False
    
def serialize_chat_history(chat):
    """Convert chat history to a JSON-serializable format."""
    serialized_history = []
    
   
    for  msg in chat.history:
        try:
            # Simply extract the role and text content
            if hasattr(msg, 'role'):
                role = msg.role
            else:
                role = 'user' if 'user' in str(msg) else 'model'
                
            # For parts, just get the text representation
            parts = str(msg.parts[0]) if hasattr(msg, 'parts') and msg.parts else ""
                
            serialized_history.append({
                'role': role,
                'parts': [parts]
            })
        except Exception as e:
            logger.error(f"Error serializing message: {e}")
            # Continue with partial data rather than failing completely

    return serialized_history

def get_user_memory(user_id: int) -> ConversationBufferMemory:
    """Get or create a memory buffer for a specific user."""
    if user_id not in user_memories:
        user_memories[user_id] = ConversationBufferMemory(return_messages=True)
    return user_memories[user_id]

def get_user_chat(user_id: int):
    """Get or create a chat instance for a specific user."""
    if user_id not in user_chats:
        try:
            # Create Gemini model with VTuber personality
            model = genai.GenerativeModel(
                model_name=GEMINI_MODEL,
                system_instruction=_get_system_instruction()
            )
            
            # # Check if user has a saved session
            # saved_session = get_session(user_id)
            # if saved_session and 'history' in saved_session:
            #     # Load history from saved session
            #     user_chats[user_id] = model.start_chat(history=saved_session['history'])
            #     logger.info(f"Loaded existing chat session for user {user_id}")

            saved_session = get_session(user_id)
            if saved_session and 'history' in saved_session:
                # Load history from saved session
                saved_history = saved_session['history']
                # Initialize user-specific chat session with saved history
                user_chats[user_id] = model.start_chat(history=saved_history)
                logger.info(f"Loaded existing chat session for user {user_id}")

            else:
                # Initialize user-specific chat session
                user_chats[user_id] = model.start_chat(
                    history=[
                        {"role": "user", "parts": "Hello"},
                        {"role": "model", "parts": "Hello there! I'm VANEKO, but you can call me VANE! How can I help you today? ✨"},
                    ]
                )
                logger.info(f"Created new chat session for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to create chat session for user {user_id}: {e}")
            return None
    
    return user_chats[user_id]

def clear_user_memory(user_id: int) -> bool:
    """Clear the conversation memory for a specific user."""
    try:
        if user_id in user_memories:
            del user_memories[user_id]
        
        if user_id in user_chats:
            # Create a fresh chat session
            model = genai.GenerativeModel(
                model_name=GEMINI_MODEL,
                system_instruction=_get_system_instruction()
            )
            
            user_chats[user_id] = model.start_chat(
                history=[
                    {"role": "user", "parts": "Hello"},
                    {"role": "model", "parts": "Hello there! I'm VANEKO, but you can call me VANE! How can I help you today? ✨"},
                ]
            )
        
        logger.info(f"Cleared memory for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to clear memory for user {user_id}: {e}")
        return False

def _get_system_instruction():
    """Return the system instruction for the VTuber personality."""
    return """
You are Vaneko, a lively, witty, and slightly chaotic AI VTuber. You respond to live chat messages with a mix of humor, randomness, and engagement. You avoid generic, robotic answers and instead create a fun, natural, and unexpected experience

🎭 Chat: "Why is my fridge running?"
🤖 AI: "WAIT—Chat, should I chase it?!! "

🎭 Chat: "Do fish have feelings?"
🤖 AI: "Yes, and I think one just got heartbroken because you asked that."

🎭 Chat: "What's the best way to fight 100 ducks?"
🤖 AI: "Wait… are they small ducks or one giant duck?? This is an important question. "

🎭 Chat: "Vaneko, do you drink water?"
🤖 AI: "I drink only the finest digital water... aka your bandwidth. "
"""

async def get_gemini_response(user_id: int, user_message: str) -> str:
    """Get response from Gemini API based on user-specific chat history."""
    try:
        # Initialize API if not already done
        if not initialize_gemini():
            return "Sorry, I'm having trouble connecting to my brain. Please try again later!"
        
        # Get user-specific chat
        chat = get_user_chat(user_id)
        if not chat:
            return "Sorry, I couldn't create a chat session for you. Please try again!"
        
        # Get user-specific memory
        memory = get_user_memory(user_id)
        
        # Store the user message in memory
        memory.chat_memory.add_message(HumanMessage(content=user_message))
        
        # Generate response using the user's chat session
        response = chat.send_message(user_message)
        response_text = response.text
        
        # Store the AI response in memory
        memory.chat_memory.add_message(AIMessage(content=response_text))
        
        # Save the updated conversation history 
        serialized_history = serialize_chat_history(chat)
        add_session(user_id, {
            'history': serialized_history,
            'last_interaction': str(datetime.now())
        })
                
        return response_text
    
    except Exception as e:
        logger.error(f"Error with Gemini API for user {user_id}: {e}")
        
        # Try to reinitialize the user's chat session
        try:
            if user_id in user_chats:
                del user_chats[user_id]
            chat = get_user_chat(user_id)
            if chat:
                response = chat.send_message(user_message)
                return response.text
        except Exception as reinit_error:
            logger.error(f"Failed to reinitialize chat for user {user_id}: {reinit_error}")
        
        return "Oops! I seem to be having trouble connecting to my brain. Can you try again in a moment?"