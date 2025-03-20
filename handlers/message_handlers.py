import logging
from telegram import Update
from telegram.ext import ContextTypes

from services.gemini_service import get_gemini_response

logger = logging.getLogger(__name__)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles user messages and responds using Gemini AI with user-specific context."""
    user = update.effective_user
    user_id = user.id
    user_message = update.message.text

    logger.info(f"User {user_id} sent message: {user_message[:50]}{'...' if len(user_message) > 50 else ''}")
    
    # Get typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Get AI response using user-specific chat history
    ai_response = await get_gemini_response(user_id, user_message)
    
    # Send response
    await update.message.reply_text(ai_response)