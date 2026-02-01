import asyncio
from telegram import Bot

BOT_TOKEN = "PUT_YOUR_BOT_TOKEN_HERE"
CHAT_ID = "PUT_YOUR_CHAT_ID_HERE"

bot = Bot(token=BOT_TOKEN)

async def send_telegram_message(msg: str):
    await bot.send_message(chat_id=CHAT_ID, text=msg)

def main():
    msg = "🚨 Test message from cloud container"
    asyncio.run(send_telegram_message(msg))

if __name__ == "__main__":
    main()
