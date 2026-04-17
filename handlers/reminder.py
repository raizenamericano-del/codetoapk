import uuid
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from utils import RedisClient
from utils.helpers import parse_time

class ReminderHandler:
    def __init__(self, redis: RedisClient):
        self.redis = redis
    
    async def set_reminder(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if len(context.args) < 2:
            await update.message.reply_text("Format: /remind <pesan> <waktu> (contoh: /remind makan 30m)")
            return
        
        time_str = context.args[-1]
        parsed = parse_time(time_str)
        
        if not parsed:
            await update.message.reply_text("Waktunya ga jelas sayang~ pake: 10m, 2h, 1d 🥺")
            return
        
        pesan = ' '.join(context.args[:-1])
        user_id = update.effective_user.id
        
        if parsed['unit'] == 'minutes':
            seconds = parsed['value'] * 60
        elif parsed['unit'] == 'hours':
            seconds = parsed['value'] * 3600
        else:
            seconds = parsed['value'] * 86400
        
        rid = str(uuid.uuid4())[:8]
        data = {
            'user_id': user_id,
            'message': pesan,
            'chat_id': update.effective_chat.id,
            'ttl': seconds + 60
        }
        
        self.redis.add_reminder(user_id, rid, data)
        
        # Schedule job
        context.job_queue.run_once(
            self._send_reminder,
            seconds,
            data={'chat_id': update.effective_chat.id, 'text': f"⏰ Reminder sayang~: {pesan} 💕", 'user_id': user_id},
            name=f"remind_{rid}"
        )
        
        await update.message.reply_text(f"Oke sayang~ KyyChan ingetin {parsed['value']} {parsed['unit']} lagi ya 💕")
    
    async def _send_reminder(self, context: ContextTypes.DEFAULT_TYPE):
        job = context.job
        await context.bot.send_message(job.data['chat_id'], job.data['text'])
    
    async def list_todo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        reminders = self.redis.get_reminders(user_id)
        
        if not reminders:
            await update.message.reply_text("Ga ada reminder sayang~ 🥺")
            return
        
        text = "📝 *Reminder Kamu:*\n\n"
        for i, r in enumerate(reminders[:10], 1):
            text += f"{i}. {r['message']}\n"
        await update.message.reply_text(text, parse_mode='Markdown')
