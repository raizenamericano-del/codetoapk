import random
import json
from telegram import Update
from telegram.ext import ContextTypes
from utils import RedisClient

class GamesHandler:
    def __init__(self, redis: RedisClient):
        self.redis = redis
        self.trivia_data = self._load_trivia()
    
    def _load_trivia(self):
        try:
            with open('data/trivia.json', 'r') as f:
                return json.load(f)
        except:
            return []
    
    async def trivia(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.trivia_data:
            await update.message.reply_text("Database trivia kosong sayang~ 🥺")
            return
        
        q = random.choice(self.trivia_data)
        context.user_data['current_trivia'] = q
        text = f"🎯 *Trivia Time!*\n\n{q['question']}\n\n"
        for i, opt in enumerate(q['options'], 1):
            text += f"{i}. {opt}\n"
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def check_trivia_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if 'current_trivia' not in context.user_data:
            return
        
        q = context.user_data['current_trivia']
        text = update.message.text.strip()
        
        if text.lower() == q['answer'].lower() or text == str(q['options'].index(q['answer']) + 1):
            user_id = update.effective_user.id
            score = self.redis.get_trivia_score(user_id) + 1
            self.redis.set_trivia_score(user_id, score)
            await update.message.reply_text(f"Benar sayang! 🎉 Skor lu: {score} 💕")
            del context.user_data['current_trivia']
    
    async def tebak(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        number = random.randint(1, 100)
        self.redis.set_tebak_number(user_id, number)
        await update.message.reply_text("KyyChan udah pilih angka 1-100 sayang~ tebak! 🤔")
    
    async def check_tebak(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text.strip()
        if not text.isdigit():
            return
        
        user_id = update.effective_user.id
        game = self.redis.get_tebak_number(user_id)
        if not game:
            return
        
        guess = int(text)
        game['attempts'] += 1
        self.redis.set_tebak_number(user_id, game['number'], game['attempts'])
        
        if guess == game['number']:
            await update.message.reply_text(f"Benar sayang! {guess} bener! 🎉 Percobaan: {game['attempts']} 💕")
            self.redis.delete_tebak_number(user_id)
        elif guess < game['number']:
            await update.message.reply_text("Kekecilan sayang~ 🔼")
        else:
            await update.message.reply_text("Kebesaran sayang~ 🔽")
    
    async def score(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        trivia = self.redis.get_trivia_score(user_id)
        await update.message.reply_text(f"🏆 Skor Trivia: {trivia} 💕")
