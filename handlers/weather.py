import requests
from telegram import Update
from telegram.ext import ContextTypes
from config import WEATHER_API_KEY

class WeatherHandler:
    async def get(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("Cuaca kota mana sayang? /weather <kota> 🌤️")
            return
        
        city = ' '.join(context.args)
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=id"
            r = requests.get(url, timeout=10)
            data = r.json()
            
            if r.status_code != 200:
                await update.message.reply_text(f"Kota ga ketemu sayang~ 🥺")
                return
            
            temp = data['main']['temp']
            feels = data['main']['feels_like']
            desc = data['weather'][0]['description']
            hum = data['main']['humidity']
            
            text = f"Aduuh di {city} {desc} banget cuy, {temp}°C (feels like {feels}°C). Kelembaban {hum}%. KyyChan mau meleleh 🥵" if temp > 30 else f"Di {city} lagi {desc}, {temp}°C. Jangan lupa jaket ya sayang~ 🥺"
            await update.message.reply_text(text)
            
        except Exception as e:
            await update.message.reply_text(f"Error sayang~ {str(e)[:100]} 🥺")
