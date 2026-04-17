import asyncio
import random
from typing import Optional, List, Dict
import requests
import groq
from groq import Groq

class LLMBalancer:
    def __init__(self):
        from config import GROQ_API_KEYS, MISTRAL_API_KEY, CEREBRAS_API_KEY
        from config import GEMINI_API_KEY, OPENROUTER_API_KEY
        
        self.groq_keys = GROQ_API_KEYS.copy()
        self.current_index = 0
        self.fallbacks = ['cerebras', 'mistral', 'gemini', 'openrouter']
        self.mistral_key = MISTRAL_API_KEY
        self.cerebras_key = CEREBRAS_API_KEY
        self.gemini_key = GEMINI_API_KEY
        self.openrouter_key = OPENROUTER_API_KEY
    
    def next_groq(self) -> str:
        key = self.groq_keys[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.groq_keys)
        return key
    
    async def chat_completion(self, messages, temperature=0.7, max_tokens=1024, model="llama-3.3-70b-versatile"):
        for _ in range(len(self.groq_keys)):
            try:
                client = Groq(api_key=self.next_groq())
                resp = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=30
                )
                return resp.choices[0].message.content
            except Exception as e:
                print(f"Groq fail: {e}")
                await asyncio.sleep(0.5)
        
        for provider in self.fallbacks:
            try:
                if provider == 'cerebras':
                    r = await self._cerebras(messages, temperature, max_tokens)
                elif provider == 'mistral':
                    r = await self._mistral(messages, temperature, max_tokens)
                elif provider == 'gemini':
                    r = await self._gemini(messages, temperature, max_tokens)
                else:
                    r = await self._openrouter(messages, temperature, max_tokens)
                if r: 
                    return r
            except Exception as e:
                print(f"{provider} fail: {e}")
        return None
    
    async def _cerebras(self, messages, temp, max_tok):
        headers = {"Authorization": f"Bearer {self.cerebras_key}", "Content-Type": "application/json"}
        data = {"model": "llama-3.3-70b", "messages": messages, "temperature": temp, "max_tokens": max_tok}
        r = requests.post("https://api.cerebras.ai/v1/chat/completions", headers=headers, json=data, timeout=30)
        return r.json()['choices'][0]['message']['content'] if r.status_code == 200 else None
    
    async def _mistral(self, messages, temp, max_tok):
        headers = {"Authorization": f"Bearer {self.mistral_key}", "Content-Type": "application/json"}
        data = {"model": "mistral-large-latest", "messages": messages, "temperature": temp, "max_tokens": max_tok}
        r = requests.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=data, timeout=30)
        return r.json()['choices'][0]['message']['content'] if r.status_code == 200 else None
    
    async def _gemini(self, messages, temp, max_tok):
        # Pakai REST API langsung, ga pake library deprecated
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
        
        # Convert messages ke format Gemini
        contents = []
        for m in messages:
            role = "user" if m["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": m["content"]}]})
        
        data = {
            "contents": contents,
            "generationConfig": {"temperature": temp, "maxOutputTokens": max_tok}
        }
        
        r = requests.post(url, json=data, timeout=30)
        if r.status_code == 200:
            result = r.json()
            if "candidates" in result and len(result["candidates"]) > 0:
                return result["candidates"][0]["content"]["parts"][0]["text"]
        return None
    
    async def _openrouter(self, messages, temp, max_tok):
        headers = {"Authorization": f"Bearer {self.openrouter_key}", "Content-Type": "application/json"}
        data = {"model": "anthropic/claude-3.5-sonnet", "messages": messages, "temperature": temp, "max_tokens": max_tok}
        r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=30)
        return r.json()['choices'][0]['message']['content'] if r.status_code == 200 else None
    
    async def transcribe_audio(self, audio_bytes: bytes) -> Optional[str]:
        for _ in range(len(self.groq_keys)):
            try:
                client = Groq(api_key=self.next_groq())
                r = client.audio.transcriptions.create(
                    file=("audio.ogg", audio_bytes),
                    model="whisper-large-v3",
                    response_format="text"
                )
                return r
            except Exception as e:
                print(f"Whisper fail: {e}")
        return None
