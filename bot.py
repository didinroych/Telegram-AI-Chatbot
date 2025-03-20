import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from config.config import TOKEN_TG_VANEKO
from utils.logger import setup_logger
from handlers.command_handlers import start_handler, help_handler, clear_handler
from handlers.message_handlers import message_handler

# Initialize logger
logger = setup_logger(__name__)

def main():
    """Main function to start the bot."""
    # Get Telegram token
    telegram_token = TOKEN_TG_VANEKO
    if not telegram_token:
        logger.error("Telegram token not set in configuration")
        return
    
    # Initialize the Application
    logger.info("Initializing Telegram bot...")
    application = Application.builder().token(telegram_token).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("clear", clear_handler))
    
    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    # Start the bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=["message", "callback_query"])
    
if __name__ == "__main__":
    main()