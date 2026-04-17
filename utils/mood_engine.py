import random
from datetime import datetime
from typing import Tuple

class MoodEngine:
    def __init__(self, redis):
        self.redis = redis
        self.weights = {'happy': 30, 'playful': 25, 'clingy': 20, 'lazy': 15, 'sad': 8, 'kesal': 2}
        self.ngambek_level = 0
        self.neg_count = 0
    
    async def get_current_mood(self):
        if self.redis.is_ngambek(): return "ngambek"
        mood = self.redis.get_current_mood()
        if not mood or mood not in ['happy','playful','clingy','lazy','sad','ngambek','kesal']:
            mood = random.choices(list(self.weights.keys()), list(self.weights.values()))[0]
            self.redis.set_mood(mood, 6)
        return mood
    
    async def force_mood(self, mood, duration=6):
        if mood in ['happy','playful','clingy','lazy','sad','ngambek','kesal']:
            self.redis.set_mood(mood, duration)
            if mood == "ngambek": self.redis.set_ngambek(duration * 60)
            return True
        return False
    
    async def check_ngambek(self, text: str) -> Tuple[bool, int]:
        text = text.lower()
        from config import NGAMBEK_TRIGGERS, GAA_MOOD_TRIGGERS
        
        for t in NGAMBEK_TRIGGERS:
            if t in text:
                last = self.redis.get_last_ngambek()
                now = int(datetime.now().timestamp())
                if last and (now - last) < 300:
                    return False, 0
                
                self.neg_count += 1
                lvl = min(self.neg_count, 3)
                self.redis.set_ngambek(15 * lvl)
                self.redis.set_last_ngambek()
                self.ngambek_level = lvl
                return True, lvl
        
        for t in GAA_MOOD_TRIGGERS:
            if t in text:
                self.redis.decrease_mood_level(2)
                self.neg_count += 1
                return False, 0
        
        if self.neg_count > 0: self.neg_count = max(0, self.neg_count - 1)
        return False, 0
    
    async def calm(self, amount=1):
        self.ngambek_level = max(0, self.ngambek_level - amount)
        if self.ngambek_level == 0:
            self.redis.clear_ngambek()
            self.neg_count = 0
    
    def should_ignore(self, user_id):
        if not self.redis.is_ngambek(): return False
        return random.random() < 0.5 if self.ngambek_level >= 3 else False
    
    async def positive(self):
        if self.redis.is_ngambek(): await self.calm(1)
        self.redis.increase_mood_level(1)
    
    def get_desc(self, mood):
        d = {
            'happy': "KyyChan lagi seneng! 🥰✨",
            'playful': "KyyChan pengen bercanda~ 😏🔥",
            'clingy': "KyyChan lagi manja~ 🥺💕",
            'lazy': "KyyChan lagi males-malesan... 😴~",
            'sad': "KyyChan lagi sedih... 🥺💔",
            'ngambek': "KYYCHAN LAGI NGAMBEK! 😤💢",
            'kesal': "KyyChan lagi kesal... 😒"
        }
        return d.get(mood, "Normal~")
    
    def time_left(self):
        t = self.redis.get_mood_expiry()
        if not t: return None
        return f"{t//3600}j {(t%3600)//60}m"
