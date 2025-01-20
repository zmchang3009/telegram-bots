## Bot to collate user responses
import os
from dotenv import load_dotenv
from typing import Final

from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, ConversationHandler, filters

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


## States
TOPIC, ITEMS = range(2)


## Global variables
collated_responses: dict = {}
list_owner: str = ''
list_topic: str = ''
message_ids: dict = {} ## Tracks notable messages


## Command handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    global collated_responses, list_topic, list_owner
    collated_responses.clear()
    list_topic = ''
    user: str = update.message.from_user.username
    list_owner = user
    
    sent_message = await update.message.reply_text(
        f'{user} has started a new list. Please suggest a topic or title.',
        reply_markup=ForceReply(selective=True)
    )

    message_ids[TOPIC] = sent_message.message_id

    return TOPIC


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text('I help collate responses from users.\nSimply start a list, then @mention me to add your response to the list.')


async def collate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /collate is issued."""
    response: str = collate_responses()
    await update.message.reply_text(response)


## Message handlers
## Handle setting list topic (Only listens to replies)
async def topic_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle setting the list topic."""
    global collated_responses, list_topic, list_owner
    text: str = update.message.text
    user: str = update.message.from_user.username
    replied_id: int = update.message.reply_to_message.message_id
    
    if replied_id == message_ids[TOPIC] and user == list_owner:
        list_topic = text
        await update.message.reply_text(f'Please start suggesting items for list {list_topic}.')
        
        return ITEMS


## Handle incoming list items
async def items_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming list items."""
    global collated_responses, list_topic, list_owner
    message_type: str = update.message.chat.type
    text: str = update.message.text
    user: str = update.message.from_user.username

    ## Add item to list
    if message_type == 'group' or message_type == 'supergroup':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            collated_responses[user] = new_text
            print(f'User {user} response recorded')
    else:
        collated_responses[user] = text
        print(f'User {user} response recorded')


## Fallback handler
async def stop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Close the list."""
    global collated_responses, list_topic, list_owner

    response: str = collate_responses()
    await update.message.reply_text(f'No longer accepting responses for {list_topic}. Final list:\n\n{response}')

    collated_responses.clear()
    list_topic = ''
    list_owner = ''

    return ConversationHandler.END
    

## Error handlers
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    print(f'Update {update} caused error {context.error}')


## Helper functions
def collate_responses() -> str:
    """Organize the user responses."""
    global collated_responses, list_topic, list_owner
    output: str = ''

    if list_topic == '':
        return 'No list topic yet.'

    if not collated_responses:
        return 'No responses yet.'

    output += f'{list_topic}  (by {list_owner})\n'
    for user, response in collated_responses.items():
        output += f'{user}: {response}\n'

    return output


def main() -> None:
    """Start the bot."""
    ## Create the Application with token.
    print('Starting bot...')
    application = Application.builder().token(TOKEN).build()

    ## Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_command)],
        states={
            TOPIC: [MessageHandler(filters.REPLY, topic_handler)],
            ITEMS: [MessageHandler(filters.Mention(f'@{BOT_USERNAME}') & ~filters.COMMAND, items_handler)]
        },
        fallbacks=[CommandHandler('stop', stop_handler)]
    )
    application.add_handler(conv_handler)

    ## Commands
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("collate", collate_command))
    
    ## Errors
    application.add_error_handler(error_handler)

    # ## Run the bot until the user presses Ctrl-C
    # print('Polling...')
    # application.run_polling(allowed_updates=Update.ALL_TYPES)

    ## Run webhook
    PORT = int(os.environ.get('PORT', '8443'))
    application.run_webhook(
        listen='0.0.0.0',
        port=PORT,
        # secret_token='ASecretTokenIHaveChangedByNow',
        webhook_url='https://zhemsbot-71ff43521989.herokuapp.com/'
    )



if __name__ == "__main__":
    main()