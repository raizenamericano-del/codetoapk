import re
import random
from datetime import datetime

def is_question(text):
    q = ['apa','siapa','kapan','dimana','kenapa','mengapa','bagaimana','berapa','apakah','bisa','gimana','nggak','dmn','kmn']
    t = text.lower()
    return '?' in t or any(t.startswith(w) for w in q)

def is_interesting(text):
    k = ['makan','film','nonton','game','cinta','pacar','kerja','capek','musik','cuaca','tidur','uang','travel','liburan','healing','anime','drakor']
    return any(x in text.lower() for x in k)

def has_trigger(text, triggers):
    return any(t in text.lower() for t in triggers)

def extract_urls(text):
    return re.findall(r'http[s]?://\S+', text)

def is_yt(url): return 'youtube' in url or 'youtu.be' in url
def is_ig(url): return 'instagram' in url
def is_tt(url): return 'tiktok' in url

def parse_time(t):
    t = t.lower().strip()
    for p, u in [(r'(\d+)m','minutes'),(r'(\d+)h','hours'),(r'(\d+)d','days'),(r'(\d+)j','hours')]:
        m = re.match(p, t)
        if m: return {'value':int(m.group(1)), 'unit':u}
    return None

def chunk_text(text, size=4000):
    if len(text) <= size: return [text]
    chunks = []
    while text:
        if len(text) <= size: chunks.append(text); break
        pos = text.rfind(' ', 0, size)
        if pos == -1: pos = size
        chunks.append(text[:pos]); text = text[pos:].strip()
    return chunks
