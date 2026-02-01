import asyncio
import requests
from bs4 import BeautifulSoup
from telegram import Bot

# ===== TELEGRAM CONFIG =====
BOT_TOKEN = "8393459969:AAGwuRANl7yELrQcFM2paMCKD3o76axojMQ"  # replace with the working token
CHAT_ID = "1683272434"        # your chat id

# ===== CONFIG =====
URL = "https://testcisia.it/calendario.php?tolc=cents&lingua=inglese"
CHECK_INTERVAL = 300  # seconds between checks
ALLOWED_STATUSES = ["DISPONIBILI", "APERTE", "PRENOTABILE"]

bot = Bot(token=BOT_TOKEN)
already_alerted = False


async def send_message(msg):
    """Send a Telegram message asynchronously."""
    await bot.send_message(chat_id=CHAT_ID, text=msg)


def check_casa():
    """Check the CISIA page for CASA availability."""
    r = requests.get(URL, timeout=20)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    for row in soup.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) < 5:
            continue

        modality = cols[1].get_text(strip=True).upper()
        status = cols[4].get_text(strip=True).upper()

        if "CASA" not in modality:
            continue
        if "YNU" in modality:
            continue

        for ok in ALLOWED_STATUSES:
            if ok in status:
                return modality, status

    return None, None


async def main():
    global already_alerted

    await send_message("🤖 CISIA CENT@CASA watcher is LIVE (24/7)")

    while True:
        try:
            modality, status = check_casa()

            if modality and not already_alerted:
                await send_message(
                    f"🚨 CENT@CASA AVAILABLE 🚨\n\n"
                    f"Modality: {modality}\n"
                    f"Status: {status}\n\n"
                    "👉 BOOK NOW:\n"
                    "https://testcisia.it/calendario.php?tolc=cents&lingua=inglese"
                )
                already_alerted = True

            if not modality:
                already_alerted = False

            await asyncio.sleep(CHECK_INTERVAL)

        except Exception as e:
            await send_message(f"⚠️ Bot error:\n{e}")
            await asyncio.sleep(600)


if __name__ == "__main__":
    asyncio.run(main())

