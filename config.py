import os
from datetime import datetime

# ═══════════════════════════════════════════════════
# KONFIGURASI KYYCHAN - BOT TELEGRAM
# ═══════════════════════════════════════════════════

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
ALLOWED_GROUP_ID = int(os.getenv("ALLOWED_GROUP_ID", "0"))

# AI / LLM API KEYS
GROQ_API_KEYS = [
    k.strip() for k in os.getenv("GROQ_API_KEYS", "").split(",") if k.strip()
]

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_AISTUDIO_KEY = os.getenv("GEMINI_AISTUDIO_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Redis
REDIS_URL = os.getenv("REDIS_URL")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# External APIs
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# ═══════════════════════════════════════════════════
# KONFIGURASI NIMBRUNG
# ═══════════════════════════════════════════════════

AUTO_JOIN_CHANCE = {
    'keyword': 1.0,
    'question': 0.6,
    'interesting': 0.4,
    'burst': 0.3,
    'random': 0.15
}

TYPING_DELAY_MIN = 2
TYPING_DELAY_MAX = 5
MAX_JOIN_PER_TOPIC = 2
COOLDOWN_SECONDS = 30

# ═══════════════════════════════════════════════════
# MOOD SYSTEM
# ═══════════════════════════════════════════════════

MOOD_TYPES = ['happy', 'playful', 'clingy', 'lazy', 'sad', 'ngambek', 'kesal']
MOOD_DURATION_HOURS = 6

TRIGGER_WORDS = [
    'kyychan', 'kyy chan', 'kyy', 'chan',
    'jokowi', 'pakde', 'jkw',
    'prabowo', 'prabowo subianto'
]

NGAMBEK_TRIGGERS = [
    'bot lain', 'bot laen', 'ai lain', 'gpt', 'chatgpt',
    'claude', 'gemini', 'copilot', 'bard', 'bing',
    'pake bot', 'pake ai',
    'kyychan jelek', 'kyychan bodoh', 'kyychan ga lucu',
    'kyychan annoying', 'diam kyychan', 'kyychan nyebelin',
    'kyychan bawel', 'kyychan gajelas',
    'ga suka kyychan', 'benci kyychan'
]

NGAMBEK_DURATION_MINUTES = 15
NGAMBEK_COOLDOWN_SECONDS = 300

GAA_MOOD_TRIGGERS = [
    'cuek', 'diam', 'diemin', 'skip',
    'ga penting', 'kyychan ga guna', 'kyychan error',
    'kyychan lemot', 'kyychan mati', 'kyychan bingung',
    'kyychan ngawur', 'bodoh', 'goblok', 'tolol'
]

# ═══════════════════════════════════════════════════
# JADWAL
# ═══════════════════════════════════════════════════

GREETING_SCHEDULE = {
    'morning': (6, 10),
    'afternoon': (12, 14),
    'evening': (18, 20),
    'night': (21, 23)
}

NEWS_SCHEDULE_HOURS = [8, 20]

# ═══════════════════════════════════════════════════
# HELPER
# ═══════════════════════════════════════════════════

def get_current_hour():
    return datetime.now().hour

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

def is_allowed_group(chat_id: int) -> bool:
    return chat_id == ALLOWED_GROUP_ID
