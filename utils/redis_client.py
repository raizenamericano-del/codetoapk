import json
import redis
import time
from typing import Optional, List, Dict, Any

class RedisClient:
    def __init__(self):
        try:
            from config import REDIS_URL, REDIS_PASSWORD
            self.r = redis.from_url(
                REDIS_URL,
                password=REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            self.r.ping()
            self.connected = True
            print("✅ Redis connected")
        except Exception as e:
            print(f"⚠️ Redis failed: {e}")
            self.connected = False
            self.r = None
    
    def save_user_memory(self, user_id: int, messages: List[Dict]):
        if not self.connected: return
        key = f"kyychan:chat:user:{user_id}"
        self.r.setex(key, 86400, json.dumps(messages[-10:]))
    
    def get_user_memory(self, user_id: int) -> List[Dict]:
        if not self.connected: return []
        key = f"kyychan:chat:user:{user_id}"
        data = self.r.get(key)
        return json.loads(data) if data else []
    
    def save_group_memory(self, group_id: int, messages: List[Dict]):
        if not self.connected: return
        key = f"kyychan:chat:group:{group_id}"
        self.r.setex(key, 86400, json.dumps(messages[-20:]))
    
    def get_group_memory(self, group_id: int) -> List[Dict]:
        if not self.connected: return []
        data = self.r.get(f"kyychan:chat:group:{group_id}")
        return json.loads(data) if data else []
    
    def set_user_name(self, user_id: int, name: str):
        if not self.connected: return
        self.r.hset(f"kyychan:user:{user_id}", "name", name)
    
    def get_user_name(self, user_id: int) -> str:
        if not self.connected: return ""
        return self.r.hget(f"kyychan:user:{user_id}", "name") or ""
    
    def set_last_seen(self, user_id: int):
        if not self.connected: return
        self.r.hset(f"kyychan:user:{user_id}", "last_seen", str(int(time.time())))
    
    def get_last_seen(self, user_id: int) -> Optional[int]:
        if not self.connected: return None
        last = self.r.hget(f"kyychan:user:{user_id}", "last_seen")
        return int(last) if last else None
    
    def get_nimbrung_status(self) -> bool:
        if not self.connected: return True
        return self.r.get("kyychan:nimbrung:status") != "off"
    
    def set_nimbrung_status(self, status: bool):
        if not self.connected: return
        self.r.set("kyychan:nimbrung:status", "on" if status else "off")
    
    def get_topic_count(self, group_id: int) -> int:
        if not self.connected: return 0
        count = self.r.get(f"kyychan:topic_count:{group_id}")
        return int(count) if count else 0
    
    def increment_topic_count(self, group_id: int):
        if not self.connected: return
        self.r.incr(f"kyychan:topic_count:{group_id}")
        self.r.expire(f"kyychan:topic_count:{group_id}", 3600)
    
    def reset_topic_count(self, group_id: int):
        if not self.connected: return
        self.r.delete(f"kyychan:topic_count:{group_id}")
    
    def get_current_mood(self) -> str:
        if not self.connected: return "happy"
        mood = self.r.get("kyychan:mood")
        return mood if mood else "happy"
    
    def set_mood(self, mood: str, duration_hours: int = 6):
        if not self.connected: return
        self.r.setex("kyychan:mood", duration_hours * 3600, mood)
    
    def get_mood_expiry(self) -> Optional[int]:
        if not self.connected: return None
        ttl = self.r.ttl("kyychan:mood")
        return ttl if ttl > 0 else None
    
    def is_ngambek(self) -> bool:
        if not self.connected: return False
        return self.r.get("kyychan:ngambek") == "1"
    
    def set_ngambek(self, duration_minutes: int = 15):
        if not self.connected: return
        self.r.setex("kyychan:ngambek", duration_minutes * 60, "1")
        self.set_mood("ngambek", duration_minutes // 60 + 1)
    
    def clear_ngambek(self):
        if not self.connected: return
        self.r.delete("kyychan:ngambek")
        self.set_mood("happy")
    
    def get_ngambek_time_left(self) -> int:
        if not self.connected: return 0
        ttl = self.r.ttl("kyychan:ngambek")
        return ttl if ttl > 0 else 0
    
    def get_last_ngambek(self) -> Optional[int]:
        if not self.connected: return None
        last = self.r.get("kyychan:last_ngambek")
        return int(last) if last else None
    
    def set_last_ngambek(self):
        if not self.connected: return
        self.r.set("kyychan:last_ngambek", str(int(time.time())))
    
    def decrease_mood_level(self, amount: int = 1):
        if not self.connected: return
        current = int(self.r.get("kyychan:mood_level") or "5")
        self.r.set("kyychan:mood_level", str(max(1, current - amount)))
    
    def get_mood_level(self) -> int:
        if not self.connected: return 5
        level = self.r.get("kyychan:mood_level")
        return int(level) if level else 5
    
    def increase_mood_level(self, amount: int = 1):
        if not self.connected: return
        current = int(self.r.get("kyychan:mood_level") or "5")
        self.r.set("kyychan:mood_level", str(min(10, current + amount)))
    
    def add_reminder(self, user_id: int, rid: str, data: Dict):
        if not self.connected: return
        self.r.setex(f"kyychan:reminder:{user_id}:{rid}", data.get('ttl', 86400), json.dumps(data))
    
    def get_reminders(self, user_id: int) -> List[Dict]:
        if not self.connected: return []
        keys = self.r.keys(f"kyychan:reminder:{user_id}:*") or []
        return [json.loads(self.r.get(k)) for k in keys if self.r.get(k)]
    
    def delete_reminder(self, user_id: int, rid: str):
        if not self.connected: return
        self.r.delete(f"kyychan:reminder:{user_id}:{rid}")
    
    def set_trivia_score(self, user_id: int, score: int):
        if not self.connected: return
        self.r.hset("kyychan:game:trivia", str(user_id), str(score))
    
    def get_trivia_score(self, user_id: int) -> int:
        if not self.connected: return 0
        score = self.r.hget("kyychan:game:trivia", str(user_id))
        return int(score) if score else 0
    
    def set_tebak_number(self, user_id: int, number: int, attempts: int = 0):
        if not self.connected: return
        data = {'number': number, 'attempts': attempts}
        self.r.setex(f"kyychan:game:tebak:{user_id}", 3600, json.dumps(data))
    
    def get_tebak_number(self, user_id: int) -> Optional[Dict]:
        if not self.connected: return None
        data = self.r.get(f"kyychan:game:tebak:{user_id}")
        return json.loads(data) if data else None
    
    def delete_tebak_number(self, user_id: int):
        if not self.connected: return
        self.r.delete(f"kyychan:game:tebak:{user_id}")
    
    def add_to_blacklist(self, user_id: int):
        if not self.connected: return
        self.r.sadd("kyychan:blacklist", str(user_id))
    
    def remove_from_blacklist(self, user_id: int):
        if not self.connected: return
        self.r.srem("kyychan:blacklist", str(user_id))
    
    def is_blacklisted(self, user_id: int) -> bool:
        if not self.connected: return False
        return self.r.sismember("kyychan:blacklist", str(user_id))
    
    def set_cooldown(self, group_id: int, seconds: int):
        if not self.connected: return
        self.r.setex(f"kyychan:cooldown:{group_id}", seconds, "1")
    
    def is_cooldown(self, group_id: int) -> bool:
        if not self.connected: return False
        return self.r.exists(f"kyychan:cooldown:{group_id}") == 1
    
    def increment_stat(self, stat_name: str):
        if not self.connected: return
        self.r.hincrby("kyychan:stats", stat_name, 1)
    
    def get_stats(self) -> Dict[str, int]:
        if not self.connected: return {}
        stats = self.r.hgetall("kyychan:stats")
        return {k: int(v) for k, v in stats.items()} if stats else {}
