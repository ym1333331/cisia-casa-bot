

import asyncio
import requests
from bs4 import BeautifulSoup
import concurrent.futures

# ===== TELEGRAM CONFIG =====
BOT_TOKEN = "8393459969:AAGwuRANl7yELrQcFM2paMCKD3o76axojMQ"
CHAT_ID = "1683272434"

# ===== CONFIG =====
URL = "https://testcisia.it/calendario.php?tolc=cents&lingua=inglese"
CHECK_INTERVAL = 300    # 5 minutes between checks

ALLOWED_MODALITIES = {"CENT@CASA"} 

def sync_check_spots():
    """
    Check CISIA calendar page once.
    Returns list of strings describing available slots, or None if none.
    """
    try:
        print("🔍 Checking CISIA website...")
        r = requests.get(URL, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        spots = []

        # Each test row is a <tr> with 8 <td>:
        # 0 MODALITÀ | 1 UNIVERSITÀ | 2 REGIONE | 3 CITTÀ |
        # 4 FINE ISCRIZIONI | 5 POSTI | 6 STATO | 7 DATA TEST
        for row in soup.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) < 8:
                continue

            modality = cols[0].get_text(strip=True)
            university = cols[1].get_text(strip=True)
            region = cols[2].get_text(strip=True)
            city = cols[3].get_text(strip=True)
            end_date = cols[4].get_text(strip=True)
            posti = cols[5].get_text(strip=True)
            stato = cols[6].get_text(strip=True)
            test_date = cols[7].get_text(strip=True)

            # We want only allowed modalities (e.g. CENT@UNI) with POSTI DISPONIBILI
            if modality in ALLOWED_MODALITIES and stato == "POSTI DISPONIBILI":
                desc = (
                    f"Data test: {test_date}\n"
                    f"Città: {city} ({region})\n"
                    f"Ateneo: {university}\n"
                    f"Posti: {posti}\n"
                    f"Stato: {stato}\n"
                    f"Fine iscrizioni: {end_date}"
                )
                spots.append(desc)
                print(f"✅ SPOT: {test_date} | {city} | {university} | posti={posti} | {stato}")

        print(f"Total spots found: {len(spots)}")
        return spots if spots else None

    except Exception as e:
        print(f"Check failed: {e}")
        return None


def send_telegram(msg: str):
    """
    Send a Telegram message via raw HTTP API (no extra libraries).
    """
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": msg}
        r = requests.post(url, data=data, timeout=10)
        print(f"Telegram response: {r.status_code} {r.text[:100]}")
    except Exception as e:
        print(f"Telegram failed: {e}")


async def watcher():
    """
    Infinite watcher loop: check, alert if needed, sleep, repeat.
    """
    global already_alerted
    already_alerted = False

    send_telegram("🤖 CISIA CENT@UNI watcher is LIVE (24/7)")

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

    try:
        while True:
            loop = asyncio.get_running_loop()
            spots = await loop.run_in_executor(executor, sync_check_spots)

            if spots and not already_alerted:
                message = "🚨 CENT@UNI SPOTS AVAILABLE 🚨\n\n"
                for s in spots[:5]:  # limit to first 5 in message
                    message += s + "\n\n"
                message += "👉 Prenota da qui:\nhttps://testcisia.it/calendario.php?tolc=cents&lingua=inglese"
                send_telegram(message)
                already_alerted = True
                print("🚨 ALERT SENT!")

            if not spots:
                already_alerted = False
                print("No matching spots found.")

            print(f"⏳ Next check in {CHECK_INTERVAL // 60} minutes...")
            await asyncio.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        executor.shutdown(wait=True)


if __name__ == "__main__":
    print("Starting CISIA CENT@UNI watcher...")
    asyncio.run(watcher())
