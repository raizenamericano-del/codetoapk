import os
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
import yt_dlp

class DownloaderHandler:
    async def download(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("Kirim linknya sayang~ /download <url> 🔥")
            return
        
        url = context.args[0]
        msg = await update.message.reply_text("Tunggu ya sayang~ KyyChan download dulu 💕")
        
        try:
            # FIX: Tambahin user-agent dan timeout
            ydl_opts = {
                'format': 'best[filesize<50M]',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'quiet': True,
                'socket_timeout': 30,
                'retries': 3,
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36'
                },
                # Khusus TikTok
                'extractor_args': {
                    'tiktok': {
                        'download_timeout': 60,
                    }
                }
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
                await msg.delete()
                
                # Cek file size
                file_size = os.path.getsize(filename)
                if file_size > 50 * 1024 * 1024:  # 50MB limit Telegram
                    await update.message.reply_text("File kegedean sayang~ max 50MB 🥺")
                    os.remove(filename)
                    return
                
                with open(filename, 'rb') as f:
                    if filename.endswith(('.mp4', '.webm', '.mkv')):
                        await update.message.reply_video(f, caption="Nih sayang~ 💕", supports_streaming=True)
                    else:
                        await update.message.reply_document(f, caption="Nih sayang~ 💕")
                
                os.remove(filename)
                
        except Exception as e:
            error_msg = str(e)
            if "timed out" in error_msg:
                await msg.edit_text("Aduh sayang~ TikTok/IG lagi block koneksi nih 🥺 Coba pake VPN atau link lain ya 💔")
            elif "private" in error_msg.lower():
                await msg.edit_text("Videonya private sayang~ ga bisa diakses 🥺")
            else:
                await msg.edit_text(f"Error sayang~ {error_msg[:100]} 🥺")
