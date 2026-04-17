from PIL import Image
from telegram import Update
from telegram.ext import ContextTypes
import os

class StickerHandler:
    async def create(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message.reply_to_message or not update.message.reply_to_message.photo:
            await update.message.reply_text("Reply foto dulu sayang~ baru /sticker 📸")
            return
        
        msg = await update.message.reply_text("Tunggu ya sayang~ KyyChan proses 💕")
        
        try:
            photo = update.message.reply_to_message.photo[-1]
            file = await photo.get_file()
            await file.download_to_drive("temp_sticker.jpg")
            
            img = Image.open("temp_sticker.jpg")
            img.thumbnail((512, 512))
            img.save("temp_sticker.webp", "WEBP")
            
            with open("temp_sticker.webp", "rb") as f:
                await update.message.reply_sticker(f)
            
            os.remove("temp_sticker.jpg")
            os.remove("temp_sticker.webp")
            await msg.delete()
            
        except Exception as e:
            await msg.edit_text(f"Gagal sayang~ 🥺 {str(e)[:100]}")
