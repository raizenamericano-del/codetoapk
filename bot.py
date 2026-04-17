#!/usr/bin/env python3
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler as TGCommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

from config import TELEGRAM_BOT_TOKEN
from utils import RedisClient, LLMBalancer, BehaviorEngine, MoodEngine
from handlers import (
    AutoChatHandler, CommandHandler, DownloaderHandler,
    MusicHandler, WeatherHandler, ReminderHandler,
    StickerHandler, GamesHandler, AdminHandler
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class KyyChanBot:
    def __init__(self):
        print("🚀 Starting KyyChan Bot...")

        self.redis = RedisClient()
        self.llm = LLMBalancer()
        self.behavior = BehaviorEngine()
        self.mood = MoodEngine(self.redis)

        self.auto_chat = AutoChatHandler(
            self.redis, self.llm, self.behavior, self.mood
        )

        self.commands = CommandHandler(self.redis, self.behavior, self.mood)
        self.downloader = DownloaderHandler()
        self.music = MusicHandler()
        self.weather = WeatherHandler()
        self.reminder = ReminderHandler(self.redis)
        self.sticker = StickerHandler()
        self.games = GamesHandler(self.redis)
        self.admin = AdminHandler(self.redis, self.mood)

        self.app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self._setup_handlers()

    def _setup_handlers(self):
        # Commands
        self.app.add_handler(TGCommandHandler("start", self.commands.start))
        self.app.add_handler(TGCommandHandler("help", self.commands.help))
        self.app.add_handler(TGCommandHandler("ask", self.commands.ask))
        self.app.add_handler(TGCommandHandler("ajak", self.commands.ajak))
        self.app.add_handler(TGCommandHandler("status", self.commands.status))

        self.app.add_handler(TGCommandHandler("download", self.downloader.download))
        self.app.add_handler(TGCommandHandler("music", self.music.search))
        self.app.add_handler(TGCommandHandler("weather", self.weather.get))

        self.app.add_handler(TGCommandHandler("remind", self.reminder.set_reminder))
        self.app.add_handler(TGCommandHandler("mytodo", self.reminder.list_todo))

        self.app.add_handler(TGCommandHandler("sticker", self.sticker.create))
        self.app.add_handler(TGCommandHandler("trivia", self.games.trivia))
        self.app.add_handler(TGCommandHandler("tebak", self.games.tebak))
        self.app.add_handler(TGCommandHandler("score", self.games.score))

        # Admin
        self.app.add_handler(TGCommandHandler("toggle_nimbrung", self.admin.toggle_nimbrung))
        self.app.add_handler(TGCommandHandler("setmood", self.admin.setmood))
        self.app.add_handler(TGCommandHandler("reset", self.admin.reset))
        self.app.add_handler(TGCommandHandler("broadcast", self.admin.broadcast))
        self.app.add_handler(TGCommandHandler("stats", self.admin.stats))
        self.app.add_handler(TGCommandHandler("blacklist", self.admin.blacklist))
        self.app.add_handler(TGCommandHandler("kip", self.admin.kip))

        # Auto handlers
        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_text)
        )
        self.app.add_handler(
            MessageHandler(filters.VOICE, self.auto_chat.handle_voice)
        )

        print("✅ Handlers registered")

    async def _handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat = update.effective_chat
        message = update.message

        if not message or not message.text:
            return

        text = message.text.lower()

        # === GROUP / SUPERGROUP ===
        if chat.type in ("group", "supergroup"):
            mentioned = False

            if message.entities:
                for e in message.entities:
                    if e.type == "mention":
                        mentioned = True
                        break

            keywords = ["kyychan", "kyy chan", "kyy", "chan"]

            if mentioned or any(k in text for k in keywords):
                await self.auto_chat.handle(update, context)

            await self.games.check_trivia_answer(update, context)
            await self.games.check_tebak(update, context)
            return

        # === PRIVATE CHAT ===
        await self._private_chat(update, context)

    async def _private_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text or ""

        triggered, level = await self.mood.check_ngambek(text)
        if triggered:
            await update.message.reply_text(
                self.behavior.ngambek_resp(level)
            )
            return

        mood = await self.mood.get_current_mood()

        sys_prompt = f"""
Lo KyyChan, cewek imut 19 tahun.
Mood: {mood}
BUKAN BOT.
Natural, manja, Indo gaul, pake emoticon.
Jawab singkat tapi gemes.
"""

        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": text}
        ]

        resp = await self.llm.chat_completion(
            messages,
            temperature=0.8,
            max_tokens=200
        )

        if resp:
            await update.message.reply_text(
                self.behavior.format(
                    resp,
                    mood,
                    update.effective_user.username
                )
            )

    def run(self):
        print("🤖 KyyChan is running!")
        self.app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    bot = KyyChanBot()
    bot.run()
