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
list_owner: str = ''
list_topic: str = ''

## Command handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    global collated_responses, list_topic, list_owner
    collated_responses.clear()
    list_topic = ''
    user: str = update.message.from_user.username
    list_owner = user
    await update.message.reply_text(f"{user} has started a new list. Please suggest a topic or title.")


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
    global collated_responses, list_topic, list_owner
    output: str = ''

    if list_topic == '':
        return 'No list topic yet.'

    if not collated_responses:
        return 'No responses yet.'

    output += f'List of {list_topic} started by {list_owner}\n'
    for user, response in collated_responses.items():
        output += f'{user}: {response}\n'

    return output


## Message handlers
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages."""
    global collated_responses, list_topic, list_owner
    message_type: str = update.message.chat.type
    text: str = update.message.text
    user: str = update.message.from_user.username

    print(f'User {user} in {message_type}: "{text}"')

    ## Handle setting list topic
    if list_topic == '' and list_owner == user:
        list_topic = text
        await update.message.reply_text(f'Please start suggesting items for list {list_topic}.')
        return
    
    ## Add item to list
    if message_type == 'group' or message_type == 'supergroup':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            collated_responses[user] = new_text
        else:
            return
    else:
        collated_responses[user] = text

    print(f'User {user} response recorded')


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