import os
from dotenv import load_dotenv

load_dotenv()

TG_API_ID = int(os.environ["TG_API_ID"])
TG_API_HASH = os.environ["TG_API_HASH"]
TG_PHONE = os.environ["TG_PHONE"]
TG_CHANNEL = os.environ.get("TG_CHANNEL", "berghainberlin")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"]

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

REDDIT_THREAD_ID = os.environ["REDDIT_THREAD_ID"]