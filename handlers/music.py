import requests
from telegram import Update
from telegram.ext import ContextTypes
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

class MusicHandler:
    def __init__(self):
        self.token = None
    
    def _get_token(self):
        if self.token: return self.token
        r = requests.post("https://accounts.spotify.com/api/token", data={
            "grant_type": "client_credentials",
            "client_id": SPOTIFY_CLIENT_ID,
            "client_secret": SPOTIFY_CLIENT_SECRET
        })
        self.token = r.json().get('access_token')
        return self.token
    
    async def search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("Cari lagu apa sayang? /music <judul> 🎵")
            return
        
        query = ' '.join(context.args)
        try:
            token = self._get_token()
            headers = {"Authorization": f"Bearer {token}"}
            params = {"q": query, "type": "track", "limit": 1}
            r = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)
            data = r.json()
            
            if not data['tracks']['items']:
                await update.message.reply_text("Ga ketemu sayang~ coba judul lain 🥺")
                return
            
            track = data['tracks']['items'][0]
            artists = ', '.join(a['name'] for a in track['artists'])
            text = (f"🎵 *{track['name']}*\n"
                    f"👤 {artists}\n"
                    f"💿 {track['album']['name']}\n"
                    f"📅 {track['album']['release_date'][:4]}\n"
                    f"⏱️ {track['duration_ms']//60000}:{(track['duration_ms']//1000)%60:02d}\n"
                    f"🔗 [Listen]({track['external_urls']['spotify']})")
            
            await update.message.reply_text(text, parse_mode='Markdown', disable_web_page_preview=True)
            
        except Exception as e:
            await update.message.reply_text(f"Error sayang~ 🥺 {str(e)[:100]}")
