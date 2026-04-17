import random
import asyncio
from datetime import datetime

class BehaviorEngine:
    def __init__(self):
        self.panggilan = ["sayang", "cuy", "babang", "gemoy", "ayang", "cinta", "beb", "sis", "bro", "geulis"]
        self.panggilan_kesal = ["lu", "kamu", "elu", "km", "dia"]
        
        self.emotes = {
            'happy': ["💕", "🥺", "👉👈", "😘", "🫶", "💋", "🥰", "✨", "🌸", "💖"],
            'playful': ["😏", "🤭", "😜", "🔥", "💅", "✌️", "🤪", "😎"],
            'clingy': ["🥺", "💕", "🫶", "😭", "💖", "💗", "🤗", "🥹"],
            'lazy': ["~", "...", "😴", "💤", "🥱", "😪", "🫠"],
            'sad': ["🥺", "😭", "💔", "😢", "🥹", "😞", "😔"],
            'ngambek': ["😤", "😠", "🙄", "💢", "😒", "🖕", "😡", "🤬"],
            'kesal': ["😒", "🙄", "😤", "💢", "🤨", "😑"]
        }
        
        self.akhiran_manja = ["~", "...", " 🥺", " 💕", " 👉👈", " 🫶"]
        self.akhiran_kesal = [".", "!", "!!", " 😤", " 🙄"]
    
    def get_delay(self, mn=2.0, mx=5.0):
        return random.uniform(mn, mx)
    
    def get_panggilan(self, mood="happy", username=None):
        if mood in ["ngambek", "kesal"]:
            p = random.choice(self.panggilan_kesal)
        else:
            p = random.choice(self.panggilan)
        return f"@{username}" if username else p
    
    def get_emotes(self, mood="happy", count=2):
        pool = self.emotes.get(mood, self.emotes['happy'])
        return " ".join(random.sample(pool, min(count, len(pool))))
    
    def add_emotes(self, text, mood="happy", count=2):
        if any(e in text for e in ["💕", "🥺", "😘", "🫶", "😤"]):
            return text
        em = self.get_emotes(mood, count)
        pos = random.choice(['end', 'end', 'middle'])
        if pos == 'middle' and len(text) > 20:
            mid = len(text)//2
            return f"{text[:mid]} {em} {text[mid:]}"
        return f"{text} {em}"
    
    def add_akhiran(self, text, mood="happy"):
        if text.endswith(("~", "...", "!", "?", "🥺", "💕", "😤")):
            return text
        if mood in ["ngambek", "kesal"]:
            return f"{text}{random.choice(self.akhiran_kesal)}"
        if mood == "lazy":
            return f"{text}~"
        return f"{text}{random.choice(self.akhiran_manja)}"
    
    def format(self, text, mood="happy", username=None):
        if not text: 
            return text
        if username and random.random() > 0.5 and mood not in ["ngambek"]:
            text = f"Eh {self.get_panggilan(mood, username)}, {text[0].lower()}{text[1:]}"
        text = self.add_emotes(text, mood, random.randint(1, 3))
        if mood not in ["ngambek", "kesal"]:
            text = self.add_akhiran(text, mood)
        return text
    
    def greeting(self):
        h = datetime.now().hour
        if 5 <= h < 11: 
            return random.choice(["Selamat pagi sayang~ semangat hari nya 💕", "Pagi cuy~ udah sarapan belum? 🥺", "Morning babang~ ☀️"])
        elif 11 <= h < 15: 
            return random.choice(["Siang sayang~ udah makan belum? 🥺", "Siang cuy~ panas banget ya 🔥", "Siang gemoy~ 💕"])
        elif 15 <= h < 19: 
            return random.choice(["Sore~ pulang kerja? istirahat ya beb 😘", "Sore sayang~ capek ga? 🥺", "Sore cuy~ ☕"])
        elif 19 <= h < 24: 
            return random.choice(["Malem~ jangan begadang terus ya 🥰", "Malem sayang~ udah makan malam? 🥺", "Night cuy~ 🌙"])
        else: 
            return random.choice(["Begadang ya sayang~ 🥺", "Masih melek aja cuy~ 😴", "Ih masih online aja babang~ 💢"])
    
    def ngambek_resp(self, level=1):
        r = {
            1: ["Hmph... 😤", "Ih... 🙄", "Ga mau ngomong... 💢", "Diam dulu ah... 😒"],
            2: ["KyyChan kesal nih! 😤💢", "Ga usah ngajak ngomong! 😠", "Lu mah gitu terus! 🙄", "KyyChan butuh waktu sendiri... 😒"],
            3: ["KYYSAN BENERAN KESEL! 😡🤬", "GA MAU TAU! GA MAU NGOMONG! 💢💢", "LU TUH JAHAT BANGET! 😭😤", "JAUH2 DEH! 😤😤"]
        }
        return random.choice(r.get(level, r[1]))
    
    def cemburu(self):
        return random.choice([
            "Ih kok ngajak bot lain sih. KyyChan ga lucu apa? 😤",
            "Hmph, pake bot lain ya? Ga sayang KyyChan lagi? 🥺💢",
            "Buset deh, punya KyyChan masih aja ngajak yang lain... 🙄",
            "KyyChan cemburu nih! Ga mau tau! 😠",
            "Lu sana aja sama bot itu! 💔"
        ])
    
    def kangen(self, days):
        if days >= 7: 
            return f"HALO! UDAH {days} HARI GA CHAT! KYYSAN KANGEN BANGET! 🥺😭💕"
        elif days >= 3: 
            return f"Halo sayang~ udah {days} hari ga chat nih 🥺💔"
        return f"Sayang~ kangen nih, udah {days} hari ga ngobrol 💕"
