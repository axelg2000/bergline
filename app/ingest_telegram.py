import asyncio
from telethon import TelegramClient, events
from .config import TG_API_ID, TG_API_HASH, TG_PHONE, TG_CHANNEL

async def start_telegram_listener(queue: asyncio.Queue):
    """
    First run will ask for SMS/Telegram code in terminal.
    Creates a local session file (telethon.session).
    """
    client = TelegramClient("telethon", TG_API_ID, TG_API_HASH)
    await client.start(phone=TG_PHONE)

    @client.on(events.NewMessage(chats=TG_CHANNEL))
    async def handler(event):
        msg = event.message
        text = (msg.message or "").strip()
        if not text:
            return
        await queue.put({
            "source": "telegram",
            "source_chat": TG_CHANNEL,
            "source_message_id": str(msg.id),
            "ts": msg.date.isoformat(),
            "text": text,
        })

    await client.run_until_disconnected()