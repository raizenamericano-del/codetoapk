#!/usr/bin/env python3
import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler as TGCommandHandler, MessageHandler, filters, ContextTypes
from config import TELEGRAM_BOT_TOKEN, ALLOWED_GROUP_ID, ADMIN_ID
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
logger = logging.getLogger(__name__)

# Railway kasih PORT via environment variable
PORT = int(os.environ.get("PORT", 8080))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")  # Nanti diisi dari Railway

class KyyChanBot:
    def __init__(self):
        print("🚀 Starting KyyChan Bot...")
        self.redis = RedisClient()
        self.llm = LLMBalancer()
        self.behavior = BehaviorEngine()
        self.mood = MoodEngine(self.redis)
        
        self.auto_chat = AutoChatHandler(self.redis, self.llm, self.behavior, self.mood)
        self.commands = CommandHandler(self.redis, self.llm, self.behavior, self.mood)
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
        
        # Admin commands
        self.app.add_handler(TGCommandHandler("toggle_nimbrung", self.admin.toggle_nimbrung))
        self.app.add_handler(TGCommandHandler("setmood", self.admin.setmood))
        self.app.add_handler(TGCommandHandler("reset", self.admin.reset))
        self.app.add_handler(TGCommandHandler("broadcast", self.admin.broadcast))
        self.app.add_handler(TGCommandHandler("stats", self.admin.stats))
        self.app.add_handler(TGCommandHandler("blacklist", self.admin.blacklist))
        self.app.add_handler(TGCommandHandler("kip", self.admin.kip))
        
        # Auto handlers
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_text))
        self.app.add_handler(MessageHandler(filters.VOICE, self.auto_chat.handle_voice))
        
        print("✅ Handlers registered")
    
    async def _handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle semua pesan text"""
        # Skip kalo ga ada message
        if not update.message or not update.message.text:
            return
        
        # Log incoming message
        chat_type = update.effective_chat.type
        chat_id = update.effective_chat.id
        user = update.effective_user
        text = update.message.text[:50] + "..." if len(update.message.text) > 50 else update.message.text
        
        logger.info(f"📨 [{chat_type}] {chat_id} | @{user.username or user.first_name}: {text}")
        
        # Cek apakah di grup yang diizinkan
        if chat_type in ['group', 'supergroup']:
            if chat_id != ALLOWED_GROUP_ID:
                logger.info(f"⏭️ Skip - Group {chat_id} not allowed")
                return
            
            # Auto chat / nimbrung
            await self.auto_chat.handle(update, context)
            
            # Cek jawaban games
            await self.games.check_trivia_answer(update, context)
            await self.games.check_tebak(update, context)
        
        else:
            # Private chat - selalu respon
            await self._private_chat(update, context)
    
    async def _private_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle private chat"""
        text = update.message.text or ""
        user = update.effective_user
        username = user.username or user.first_name
        
        # Cek ngambek trigger
        triggered, level = await self.mood.check_ngambek(text)
        if triggered:
            resp = self.behavior.ngambek_resp(level)
            await update.message.reply_text(resp)
            return
        
        mood = await self.mood.get_current_mood()
        sys_p = f"""Lo KyyChan, cewek imut 19 tahun. Mood: {mood}. BUKAN BOT.
Natural, manja, pake emoticon, gaya Indo gaul. Jawab dengan singkat tapi gemes.
User: @{username}"""
        
        messages = [
            {"role": "system", "content": sys_p},
            {"role": "user", "content": text}
        ]
        
        resp = await self.llm.chat_completion(messages, temperature=0.8, max_tokens=200)
        if resp:
            formatted = self.behavior.format_response(resp, mood, username)
            await update.message.reply_text(formatted)
    
    async def _health_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Simple health check"""
        await update.message.reply_text("💕 KyyChan alive! ~")
    
    def run_webhook(self):
        """Run dengan webhook (buat Railway)"""
        if not WEBHOOK_URL:
            print("❌ WEBHOOK_URL not set!")
            return
        
        webhook_path = f"/webhook/{TELEGRAM_BOT_TOKEN}"
        full_url = f"{WEBHOOK_URL}{webhook_path}"
        
        print(f"🌐 Setting webhook: {full_url}")
        
        # Set webhook
        import asyncio
        async def set_webhook():
            await self.app.bot.set_webhook(url=full_url)
            print(f"✅ Webhook set to: {full_url}")
        
        asyncio.run(set_webhook())
        
        # Run webhook server
        print(f"🚀 Starting webhook server on port {PORT}...")
        self.app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=full_url,
            drop_pending_updates=True
        )
    
    def run_polling(self):
        """Run dengan polling (buat local/VPS)"""
        print("🤖 Starting polling mode...")
        self.app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    bot = KyyChanBot()
    
    # Cek environment: Railway = webhook, Local = polling
    if os.environ.get("RAILWAY_ENVIRONMENT") or os.environ.get("WEBHOOK_URL"):
        print("🌐 Running in WEBHOOK mode (Railway)")
        bot.run_webhook()
    else:
        print("🏠 Running in POLLING mode (Local)")
        bot.run_polling()
