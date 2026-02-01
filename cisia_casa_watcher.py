import asyncio
from telegram import Bot

BOT_TOKEN = "8393459969:AAGwuRANl7yELrQcFM2paMCKD3o76axojMQ"
CHAT_ID = "1683272434"

bot = Bot(token=BOT_TOKEN)

async def send_telegram_message(msg: str):
    await bot.send_message(chat_id=CHAT_ID, text=msg)

def main():
    msg = "🚨 Test message from cloud container"
    asyncio.run(send_telegram_message(msg))

if __name__ == "__main__":
    main()

