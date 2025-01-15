## Bot to collate user responses
import os
from dotenv import load_dotenv
from typing import Final

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()
TOKEN: Final = os.environ.get('ZHEMS_BOT_API')
BOT_USERNAME: Final = '@zhemsbot'


## Responses
collated_responses: dict = {}

## Command handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    collated_responses.clear()
    await update.message.reply_text(f"Hello! I am {BOT_USERNAME}.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("I help collate responses from users.")


async def collate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /collate is issued."""
    response: str = collate_responses()
    await update.message.reply_text(response)


## Response handlers
def collate_responses() -> str:
    """Organize the user responses."""
    output: str = ''

    if not collated_responses:
        return 'No responses yet.'

    for user, response in collated_responses.items():
        output += f'{user}: {response}\n'

    return output


## Message handlers
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages."""
    message_type: str = update.message.chat.type
    text: str = update.message.text
    user: str = update.message.from_user.username

    print(f'User {user} in {message_type}: "{text}"')

    if message_type == 'group' or message_type == 'supergroup':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            collated_responses[user] = new_text
        else:
            return
    else:
        collated_responses[user] = text

    print(f'User {user} response received')


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
    application.add_handler(CommandHandler("collate", collate_command))

    ## Messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    ## Errors
    application.add_error_handler(error_handler)

    # Run the bot until the user presses Ctrl-C
    print('Polling...')
    application.run_polling(allowed_updates=Update.ALL_TYPES)



if __name__ == "__main__":
    main()