import requests
from dotenv import dotenv_values

config = dotenv_values(".env")
# Retrieve your bot token from a .env file.
bot_token = config.get("TELEGRAM_TOKEN")
# Retrieve your ngrok public URL from a .env file.
ngrok_url = config.get("NGROK_URL")

api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook?url={ngrok_url}/webhook"

response = requests.post(api_url)

if response.status_code == 200:
    print("Webhook set successfully.")
else:
    print(f"Error setting webhook. Status code: {response.status_code}, Response: {response.text}") 