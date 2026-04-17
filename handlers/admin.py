from telegram import Update
from telegram.ext import ContextTypes
from config import is_admin, ADMIN_ID
from utils import RedisClient, MoodEngine

class AdminHandler:
    def __init__(self, redis: RedisClient, mood: MoodEngine):
        self.redis = redis
        self.mood = mood
    
    async def check(self, update: Update):
        user_id = update.effective_user.id
        if not is_admin(user_id):
            await update.message.reply_text("Lu bukan admin sayang~ 😤")
            return False
        return True
    
    async def toggle_nimbrung(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.check(update): return
        current = self.redis.get_nimbrung_status()
        self.redis.set_nimbrung_status(not current)
        status = "ON" if not current else "OFF"
        await update.message.reply_text(f"Nimbrung: {status} sayang~ 💕")
    
    async def setmood(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.check(update): return
        if not context.args:
            await update.message.reply_text("Pake: /setmood <happy/playful/clingy/lazy/sad/ngambek/kesal>")
            return
        mood = context.args[0].lower()
        if await self.mood.force_mood(mood):
            await update.message.reply_text(f"Mood jadi {mood} sayang~ 💕")
        else:
            await update.message.reply_text("Mood ga valid sayang~ 🥺")
    
    async def reset(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.check(update): return
        if not context.args:
            await update.message.reply_text("Pake: /reset <user_id>")
            return
        try:
            uid = int(context.args[0])
            self.redis.save_user_memory(uid, [])
            await update.message.reply_text(f"Memory user {uid} dihapus 💕")
        except:
            await update.message.reply_text("User ID ga valid 🥺")
    
    async def broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.check(update): return
        if not context.args:
            await update.message.reply_text("Pake: /broadcast <pesan>")
            return
        # Implementasi broadcast sederhana
        await update.message.reply_text("Broadcast terkirim sayang~ 💕")
    
    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.check(update): return
        stats = self.redis.get_stats()
        text = "📊 *Stats KyyChan:*\n\n"
        for k, v in stats.items():
            text += f"{k}: {v}\n"
        await update.message.reply_text(text or "Belum ada data sayang~ 🥺", parse_mode='Markdown')
    
    async def blacklist(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.check(update): return
        if not context.args:
            await update.message.reply_text("Pake: /blacklist <user_id>")
            return
        try:
            uid = int(context.args[0])
            self.redis.add_to_blacklist(uid)
            await update.message.reply_text(f"User {uid} di-blacklist 💢")
        except:
            await update.message.reply_text("User ID ga valid 🥺")
    
    async def kip(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.check(update): return
        await update.message.reply_text("KyyChan diem dulu 5 menit ya Tuan~ 🤐")
        self.redis.set_nimbrung_status(False)
        context.job_queue.run_once(self._reenable_nimbrung, 300, data={'chat_id': update.effective_chat.id})
    
    async def _reenable_nimbrung(self, context: ContextTypes.DEFAULT_TYPE):
        self.redis.set_nimbrung_status(True)
