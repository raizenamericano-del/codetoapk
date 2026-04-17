import random
from telegram import Update
from telegram.ext import ContextTypes
from config import is_admin
from utils import BehaviorEngine, MoodEngine, RedisClient

class CommandHandler:
    def __init__(self, redis, behavior, mood):
        self.redis = redis
        self.behavior = behavior
        self.mood = mood
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        mood = await self.mood.get_current_mood()
        text = ("Hai sayang~ Aku KyyChan! 🥰\n\n"
                "KyyChan bisa nimbrung tanpa di-tag, download video, info cuaca & musik, "
                "games, reminder, dan masih banyak lagi~ 👉👈\n\n"
                "Ketik /help ya sayang!")
        await update.message.reply_text(self.behavior.format(text, mood))
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = ("📋 *Command KyyChan:*\n\n"
                "*Chat:* /ask <tanya> | /ajak <ngobrol>\n"
                "*Tools:* /download <url> | /music <judul> | /weather <kota> | /remind <pesan> <waktu> | /mytodo\n"
                "*Fun:* /sticker | /trivia | /tebak | /score\n"
                "*Admin:* /toggle_nimbrung | /setmood <mood> | /reset <user_id> | /broadcast | /stats | /blacklist | /kip")
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def ask(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("Tanya apa sayang? /ask <pertanyaan> 🥺")
            return
        from utils import LLMBalancer
        llm = LLMBalancer()
        q = ' '.join(context.args)
        mood = await self.mood.get_current_mood()
        sys_p = f"KyyChan, cewek imut 19th. Mood: {mood}. Jawab dengan gaya manja + emoticon + ~"
        messages = [{"role":"system","content":sys_p}, {"role":"user","content":q}]
        r = await llm.chat_completion(messages)
        if r:
            await update.message.reply_text(self.behavior.format(r, mood))
        else:
            await update.message.reply_text("Aduh sayang~ bingung nih 🥺 coba lain ya 💕")
    
    async def ajak(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        mood = await self.mood.get_current_mood()
        if mood == "ngambek":
            await update.message.reply_text("Ga mau! Lagi ngambek! 😤")
            return
        r = random.choice([
            "Iya sayang~ ngobrolin apa nih? 💕",
            "Hai babang~ kangen ya? 🥺",
            "Wih diajak ngobrol~ seneng nih 🥰",
            "Ayang mau cerita apa? KyyChan dengerin~ 🫶"
        ])
        await update.message.reply_text(self.behavior.format(r, mood))
    
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        mood = await self.mood.get_current_mood()
        desc = self.mood.get_desc(mood)
        ttl = self.mood.time_left()
        nimbrung = "ON" if self.redis.get_nimbrung_status() else "OFF"
        ngambek = "YES" if self.redis.is_ngambek() else "NO"
        ng_time = self.redis.get_ngambek_time_left()
        
        t = f"⚡ *Status KyyChan*\n\nMood: {mood}\n{desc}\nUbah mood: {ttl or 'soon'}\nNimbrung: {nimbrung}\nNgambek: {ngambek}"
        if ng_time > 0: t += f"\nSisa ngambek: {ng_time//60}m"
        await update.message.reply_text(t, parse_mode='Markdown')
