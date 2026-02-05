import asyncio
import requests
from bs4 import BeautifulSoup
from telegram import Bot
from requests.exceptions import RequestException

# ===== TELEGRAM CONFIG =====
BOT_TOKEN = "8393459969:AAGwuRANl7yELrQcFM2paMCKD3o76axojMQ"
CHAT_ID = "1683272434"

# ===== CONFIG =====
URL = "https://testcisia.it/calendario.php?tolc=cents&lingua=inglese"
CHECK_INTERVAL = 300  # seconds between normal checks
RETRY_DELAY = 15      # seconds between retries if request fails
ALLOWED_STATUSES = ["DISPONIBILI", "APERTE", "PRENOTABILE"]

bot = Bot(token=BOT_TOKEN)
already_alerted = False

async def send_message(msg):
    """Send a Telegram message asynchronously."""
    await bot.send_message(chat_id=CHAT_ID, text=msg)

def check_casa():
    """Check the CISIA page for CASA availability, retrying endlessly if network fails."""
    while True:  # endless retry loop
        try:
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

            return None, None  # no available slot found

        except RequestException as e:
            print(f"Request failed: {e}. Retrying in {RETRY_DELAY}s...")
            asyncio.run(asyncio.sleep(RETRY_DELAY))
            continue  # retry endlessly

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
            await asyncio.sleep(30)  # short wait before next retry

if __name__ == "__main__":
    asyncio.run(main())
