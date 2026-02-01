import time
import requests
import asyncio
from bs4 import BeautifulSoup
from telegram import Bot

# ===== TELEGRAM CONFIG (TEMP – CHANGE LATER) =====
BOT_TOKEN = "8393459969:AAGwuRANl7yELrQcFM2paMCKD3o76axojMQ"
CHAT_ID = "1683272434"

# ===== CONFIG =====
URL = "https://testcisia.it/calendario.php?tolc=cents&lingua=inglese"
CHECK_INTERVAL = 300  # 5 minutes
ALLOWED_STATUSES = ["DISPONIBILI", "APERTE", "PRENOTABILE"]

bot = Bot(token=BOT_TOKEN)
already_alerted = False


async def send(msg):
    await bot.send_message(chat_id=CHAT_ID, text=msg)


def casa_available():
    r = requests.get(URL, timeout=20)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    rows = soup.find_all("tr")

    for row in rows:
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

    await send("🤖 CISIA CENT@CASA watcher is LIVE (24/7)")

    while True:
        try:
            modality, status = casa_available()

            if modality and not already_alerted:
                await send(
                    "🚨 CENT@CASA AVAILABLE 🚨\n\n"
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
            await send(f"⚠️ Bot error:\n{e}")
            await asyncio.sleep(600)


if __name__ == "__main__":
    asyncio.run(main())

