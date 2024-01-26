# Telegram Bot with Webhook Setup
** work in progress **

This Python script sets up a basic Telegram bot using the Bottle framework to handle incoming webhook requests. The webhook is configured to interact with the Telegram API, and ngrok is used to expose the local development server to the internet.

## Prerequisites
- Python
- ngrok
- Telegram Bot Token (Create a bot on Telegram via [BotFather](https://core.telegram.org/bots#botfather))
- [python-telegram-bot](https://python-telegram-bot.readthedocs.io/) library
- [Bottle](https://bottlepy.org/docs/dev/)

## Getting Started
1. Install the required Python libraries:

   ```bash
   pip install python-telegram-bot bottle
   ```

2. Create a `.env` file with the following content:

   ```env
   TELEGRAM_TOKEN=<your_telegram_bot_token>
   NGROK_URL=<ngrok_public_url>
   ```

3. Install ngrok ([ngrok Installation](https://ngrok.com/download)) and expose the local server:

   ```bash
   ngrok http 8080
   ```

   Copy the generated ngrok public URL and update the `NGROK_URL` in the `.env` file.

4. Run the script:

   ```bash
   python your_script_name.py
   ```

## Code Overview
- **Imported Modules:**
  - `bottle`: Web framework used for handling incoming webhook requests.
  - `dotenv`: Load environment variables from a `.env` file.
  - `telegram`: Telegram bot API library.
  - `asyncio`: Asynchronous programming library.
  - `ThreadPoolExecutor`: Concurrent execution of tasks in a separate thread.

