import random
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from config import ALLOWED_GROUP_ID, AUTO_JOIN_CHANCE, TRIGGER_WORDS
from utils import RedisClient, LLMBalancer, BehaviorEngine, MoodEngine
from utils.helpers import is_question, is_interesting, has_trigger

class AutoChatHandler:
    def __init__(self, redis, llm, behavior, mood):
        self.redis = redis
        self.llm = llm
        self.behavior = behavior
        self.mood = mood
    
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message or not update.effective_chat: return
        chat_id = update.effective_chat.id
        if chat_id != ALLOWED_GROUP_ID: return
        if not self.redis.get_nimbrung_status(): return
        
        user_id = update.effective_user.id if update.effective_user else None
        if user_id and self.redis.is_blacklisted(user_id): return
        
        text = update.message.text or update.message.caption or ""
        
        # CEK NGAMBEK TRIGGER
        triggered, level = await self.mood.check_ngambek(text)
        if triggered:
            await asyncio.sleep(random.uniform(2,4))
            await update.message.reply_text(self.behavior.ngambek_resp(level))
            return
        
        if self.mood.should_ignore(user_id): return
        
        prob = self._calc_prob(text)
        if has_trigger(text, TRIGGER_WORDS): prob = 1.0
        
        if random.random() > prob: return
        if self.redis.is_cooldown(chat_id): return
        if self.redis.get_topic_count(chat_id) >= 2: return
        
        await self._nimbrung(update, context, text)
    
    def _calc_prob(self, text):
        prob = 0.0
        if is_question(text): prob = AUTO_JOIN_CHANCE['question']
        elif is_interesting(text): prob = AUTO_JOIN_CHANCE['interesting']
        else: prob = AUTO_JOIN_CHANCE['random']
        
        mood = self.redis.get_current_mood()
        if mood == 'lazy': prob *= 0.5
        elif mood == 'clingy': prob *= 1.3
        elif mood == 'happy': prob *= 1.1
        return min(prob, 1.0)
    
    async def _nimbrung(self, update, context, text):
        msg = update.message
        user = update.effective_user
        delay = self.behavior.get_delay()
        
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        await asyncio.sleep(delay)
        
        mood = await self.mood.get_current_mood()
        sys_prompt = f"""Lo KyyChan, cewek imut 19 tahun. Mood: {mood}. BUKAN BOT.
Panggilan: sayang,cuy,babang,gemoy,ayang,cinta,beb.
Bhs: Indo gaul + emoticon + ~ di akhir. Natural, 1-3 kalimat. Bisa ngeledek/usil/manja."""
        
        messages = [
            {"role":"system","content":sys_prompt},
            {"role":"user","content":f"@{user.username or user.first_name} bilang: '{text}'. Nimbrung natural."}
        ]
        
        resp = await self.llm.chat_completion(messages, temperature=0.8, max_tokens=150)
        if resp:
            formatted = self.behavior.format(resp, mood, user.username)
            await msg.reply_text(formatted)
            self.redis.increment_stat('nimbrung')
            self.redis.increment_topic_count(update.effective_chat.id)
            self.redis.set_cooldown(update.effective_chat.id, 30)
    
    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message or not update.message.voice: return
        if self.redis.is_ngambek():
            await update.message.reply_text("Ga denger! Lagi ngambek! 😤")
            return
        
        file = await update.message.voice.get_file()
        audio = await file.download_as_bytearray()
        transcript = await self.llm.transcribe_audio(bytes(audio))
        
        if transcript:
            mood = await self.mood.get_current_mood()
            r = self.behavior.format(f"Nih sayang~ isi voice note nya: \"{transcript}\"", mood)
            await update.message.reply_text(r)
        else:
            await update.message.reply_text("Aduh sayang~ ga jelas nih 🥺 coba lagi ya 💕")
