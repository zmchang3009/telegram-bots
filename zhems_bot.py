import os
from dotenv import load_dotenv
from typing import Final

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()
TOKEN: Final = os.environ.get('ZHEMS_BOT_API')
BOT_USERNAME: Final = '@zhemsbot'

# import logging

# # Enable logging
# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
# )
# # set higher logging level for httpx to avoid all GET and POST requests being logged
# logging.getLogger("httpx").setLevel(logging.WARNING)

# logger = logging.getLogger(__name__)


## Command handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(f"Hello! I am {BOT_USERNAME}.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("I am a basic bot that echoes what you send!")


## Response handlers
def response_handler(text: str) -> str:
    """Echo the user message."""
    return text


## Message handlers
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages."""
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User {update.message.chat.id} in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = response_handler(new_text)
        else:
            return
    else:
        response: str = response_handler(text)

    print(f'Bot: "{response}"')

    await update.message.reply_text(response)


## Error handlers
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    print(f'Update {update} caused error {context.error}')



def main() -> None:
    """Start the bot."""
    ## Create the Application with token.
    print('Starting bot...')
    application = Application.builder().token(TOKEN).build()

    ## Commands
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))

    ## Messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    ## Errors
    application.add_error_handler(error_handler)

    # Run the bot until the user presses Ctrl-C
    print('Polling...')
    application.run_polling(allowed_updates=Update.ALL_TYPES)



if __name__ == "__main__":
    main()