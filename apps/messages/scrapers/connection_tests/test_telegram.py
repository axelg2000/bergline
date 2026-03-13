"""Quick script to test Telegram API connection.

Usage: python apps/messages/scrapers/connection_tests/test_telegram.py

First run will ask for your phone number + verification code.
After that, the session is saved in telethon_test.session.
"""

import asyncio
import os
import sys

try:
    from telethon import TelegramClient
except ImportError:
    print("telethon not installed. Run: pip install telethon")
    sys.exit(1)

# Load .env file manually (no Django needed)
env_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".env")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())

api_id = os.environ.get("TELEGRAM_API_ID", "")
api_hash = os.environ.get("TELEGRAM_API_HASH", "")
phone = os.environ.get("TELEGRAM_PHONE", "")
group = os.environ.get("TELEGRAM_GROUPS", "berghainberlin").split(",")[0].strip()

# Check credentials exist
if not api_id or not api_hash:
    print("TELEGRAM_API_ID or TELEGRAM_API_HASH not set in .env")
    sys.exit(1)

if not phone:
    print("TELEGRAM_PHONE not set in .env")
    sys.exit(1)

print(f"API ID:  {api_id}")
print(f"Phone:   {phone}")
print(f"Group:   {group}")
print()


async def main():
    client = TelegramClient("telethon_test", int(api_id), api_hash)
    await client.start(phone=phone)

    me = await client.get_me()
    print(f"Logged in as: {me.first_name} (@{me.username})")
    print()

    # Fetch last message from the group
    print(f"--- Latest message from '{group}' ---")
    async for message in client.iter_messages(group, limit=1):
        sender = await message.get_sender()
        sender_name = getattr(sender, "first_name", "Unknown") or "Unknown"
        print(f"From:   {sender_name}")
        print(f"Date:   {message.date.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        if message.text:
            preview = message.text[:300] + ("..." if len(message.text) > 300 else "")
            print(f"Text:   {preview}")
        else:
            print("Text:   (no text — media or other content)")

    print()
    print("Telegram connection works!")
    await client.disconnect()


asyncio.run(main())
