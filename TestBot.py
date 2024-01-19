# Import python modules
from bottle import Bottle, run, post, request as bottle_request
from dotenv import dotenv_values
import logging
from telegram import Bot, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
import asyncio
from concurrent.futures import ThreadPoolExecutor

config = dotenv_values(".env")
# Retrieve your bot token from a .env file.
token = config.get("TELEGRAM_TOKEN")
ngrok_public_url = config.get("NGROK_URL")


# Enable logging.
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

start, cancel_command = range(2)

# Define conversation states
cancel_state = 0

# Start the conversation.


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info("Entered start function.")
    await update.message.reply_text(
        "Hey, I am your test bot!\n"
        "Select /cancel if you don't want to talk to me.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return cancel_command

# Conclude the conversation.


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info("Entered cancel_command function.")
    user = update.message.from_user
    await update.message.reply_text(
        "Goodbye! Have a great day!\n"
        "If you change your mind, feel free to start a new conversation by typing /start.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


# Delete webhook


# async def delete_webhook():
#     bot = Bot(token=token)
#     await bot.deleteWebhook()
#     logger.info("Webhook deleted successfully.")

# Set the Telegram webhook URL


async def set_webhook():
    #await delete_webhook()  # Delete existing webhook
    webhook_url = f"https://api.telegram.org/bot{token}/setWebhook?url={ngrok_public_url}"
    bot = Bot(token=token)
    logger.info("Setting up ngrok webhook...")
    await bot.setWebhook(url=webhook_url)
    logger.info("Webhook set successfully.")

# Print a message indicating that the webhook URL has been set
print(f"Webhook URL set to: {ngrok_public_url}")

# Run the bot.
application = Application.builder().token(token).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={cancel_state: [CommandHandler('cancel', cancel_command),
                           MessageHandler(filters.TEXT, cancel_command)]
            },
    fallbacks=[CommandHandler('cancel', cancel_command)]
)

application.add_handler(conv_handler)


# Handle webhook updates in a separate thread
def handle_webhook_update(update_json, bot):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    update = Update.de_json(update_json, bot)
    loop.run_until_complete(application.process_update(update))


# Create a Bottle web application.
app = Bottle()


@app.post('/')
def webhook_handler():
    logger.info("Received webhook request.")
    try:
        update_json = bottle_request.json
        with ThreadPoolExecutor() as executor:
            executor.submit(handle_webhook_update,
                            update_json, application.bot)
        logger.info("Webhook request processed successfully.")
    except Exception as e:
        logger.error(f"Error processing update: {e}")
    return ''


# Run the Bottle web application using ngrok.
if __name__ == '__main__':
    try:
        # Run the set_webhook function
        asyncio.run(set_webhook())
        # Run the Bottle web application
        app.run(host='localhost', port=8080, debug=True, server='waitress')
    finally:
        # Close the asyncio event loop to avoid ResourceWarning
        asyncio.get_event_loop().close()


