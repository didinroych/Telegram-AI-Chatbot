import logging
from telegram import Update
from telegram.ext import ContextTypes

from services.gemini_service import get_gemini_response, clear_user_memory

logger = logging.getLogger(__name__)

# Set to track members who have started the bot
registered_members = set()

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for the /start command"""
    user = update.effective_user
    user_id = user.id
    logger.info(f"User {user_id} ({user.first_name}) started the bot")
    
    # Check if user is new or returning
    is_new_user = user_id not in registered_members
    
    if is_new_user:
        registered_members.add(user_id)
        welcome_message = f"This person {user.first_name} is new! Give them a warm welcome."
    else:
        welcome_message = f"This person {user.first_name} has already started before but is back to chat. Give them a warm welcome!"

    # Get welcome message from AI using user-specific chat
    ai_response = await get_gemini_response(user_id, welcome_message)
    await update.message.reply_text(ai_response)

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for the /help command"""
    help_text = (
        "VANEKO Bot Commands:\n\n"
        "/start - Start or restart the bot\n"
        "/help - Show this help message\n"
        "/clear - Clear your conversation history\n\n"
        "Just send a message to chat with VANEKO!"
    )
    await update.message.reply_text(help_text)

async def clear_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for the /clear command to reset conversation history"""
    user_id = update.effective_user.id
    
    # Clear user memory
    success = clear_user_memory(user_id)
    
    if success:
        await update.message.reply_text("Your conversation history has been cleared! What would you like to talk about now?")
    else:
        await update.message.reply_text("Sorry, I couldn't clear your conversation history. Please try again later!")