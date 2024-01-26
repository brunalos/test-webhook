# Import python modules
from bottle import Bottle, post, request as bottle_request
from dotenv import dotenv_values
import logging
from telegram import Bot, Update
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

# Retrieve your variables from a .env file.
config = dotenv_values(".env")
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


async def parse_message(message):
    print("message-->", message)
    chat_id = message['message']['chat']['id']
    txt = message['message']['text']
    print("chat_id-->", chat_id)
    print("txt-->", txt)
    return chat_id, txt

async def send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    response = await bottle_request.post(url, json=payload)
    return response
   
# Start the conversation

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info("Entered start function.")
    chat_id = update.effective_chat.id
    await send_message(chat_id, "Hey, I am your test bot!\nSelect /cancel if you don't want to talk to me.")
    return cancel_command

# Conclude the conversation

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info("Entered cancel_command function.")
    user = update.message.from_user
    await update.message.reply_text(
        "Goodbye! Have a great day!\n"
        "If you change your mind, feel free to start a new conversation by typing /start."
    )
    return ConversationHandler.END

async def index():
    msg = bottle_request.get_json()
    chat_id, txt = await parse_message(msg)
    if txt == "/start":
        await send_message(chat_id, await start(None, None))
    else:
        await send_message(chat_id, await cancel_command(None, None))


# Set the Telegram webhook URL

async def set_webhook():
    webhook_url = f"https://api.telegram.org/bot{token}/setWebhook?url={ngrok_public_url}/post"
    bot = Bot(token=token)
    logger.info("Setting up ngrok webhook...")
    await bot.setWebhook(url=webhook_url)
    logger.info("Webhook set successfully.")

# Print a message indicating that the webhook URL has been set
print(f"Webhook URL set to: {ngrok_public_url}")

# Run the bot.
application = Application.builder().token(token).build()
application.initialize()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={cancel_state: [CommandHandler('cancel', cancel_command),
                           MessageHandler(filters.TEXT, cancel_command)]
            },
    fallbacks=[CommandHandler('cancel', cancel_command)]
)

application.add_handler(conv_handler)


# Handle webhook updates in a separate thread
async def handle_webhook_update(update_json, bot):
    try:
        update = Update.de_json(update_json, bot)
        await application.process_update(update)
        logger.info("Webhook request processed successfully.")
    except Exception as e:
        logger.error(f"Error processing update: {e}")


# Create a Bottle web application.
app = Bottle()

@app.get('/')
def webhook_updated():
    return "Received webhook request"

@app.post('/post')
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
    except KeyboardInterrupt:
        pass
    finally:
        # Cleanup resources
        asyncio.run(application.shutdown())
