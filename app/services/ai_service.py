import json
from abc import ABC, abstractmethod
from app.core.config import settings
from typing import Dict

# Provider kitabxanaları
from openai import AsyncOpenAI
import google.generativeai as genai
from anthropic import AsyncAnthropic

class AIProvider(ABC):
    @abstractmethod
    async def generate_text(self, prompt: str) -> str:
        """Verilən prompt əsasında mətn yaradır."""
        pass


class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate_text(self, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content or ""


class ClaudeProvider(AIProvider):
    def __init__(self, api_key: str):
        self.client = AsyncAnthropic(api_key=api_key)

    async def generate_text(self, prompt: str) -> str:
        response = await self.client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text


class GeminiProvider(AIProvider):
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    async def generate_text(self, prompt: str) -> str:
        # Gemini asinxron API-ni dəstəkləyir: generate_content_async
        response = await self.model.generate_content_async(prompt)
        return response.text


class AIService:
    """
    Seçilmiş provayder vasitəsilə biznes logikasını işlədir.
    Factory pattern istifadə olunur.
    """
    def __init__(self, provider_name: str = "openai"):
        self.provider = self._get_provider(provider_name)

    def _get_provider(self, name: str) -> AIProvider:
        name = name.lower()
        if name == "openai" and settings.OPENAI_API_KEY:
            return OpenAIProvider(settings.OPENAI_API_KEY)
        elif name == "claude" and settings.CLAUDE_API_KEY:
            return ClaudeProvider(settings.CLAUDE_API_KEY)
        elif name == "gemini" and settings.GEMINI_API_KEY:
            return GeminiProvider(settings.GEMINI_API_KEY)
        
        # Default olaraq OpenAI fallback (Əgər açar yoxdursa test üçün Mock qaytara bilərsiniz)
        raise ValueError(f"Seçilmiş AI provayderi ({name}) və ya API Key tapılmadı!")

    async def generate_social_media_pack(self, property_title: str, price: float, district: str, area: float) -> Dict[str, str]:
        prompt = (
            f"Sən peşəkar bir əmlak kopyarayterisən.\n"
            f"Ev məlumatları: Başlıq: {property_title}, Qiymət: {price} AZN, Rayon: {district}, Sahə: {area} kv.m.\n\n"
            f"Mənə aşağıdakıları Azərbaycan dilində, JSON formatında qaytar:\n"
            f"{{\n"
            f"  \"elan_metni\": \"Geniş və rəsmi elan mətni\",\n"
            f"  \"tiktok\": \"TikTok üçün qısa və trendə uyğun başlıq\",\n"
            f"  \"instagram\": \"Instagram postu (Emojilər və mütləq zəng etməyə təşviq ilə)\",\n"
            f"  \"whatsapp\": \"WhatsApp statusu (Çox qısa və vurucu)\",\n"
            f"  \"seo_title\": \"Veb-sayt üçün SEO başlıq (Maks 60 simvol)\",\n"
            f"  \"hashtags\": \"#emlak #baku #evler tipli 10 ədəd uyğun hashtag\"\n"
            f"}}"
            f"\nDiqqət: Yalnız düzgün formatlanmış JSON qaytar, heç bir əlavə mətn yazma."
        )
        
        response_text = await self.provider.generate_text(prompt)
        
        # AI bəzən markdown block (```json) qaytarır, onu təmizləyirik.
        clean_json = response_text.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(clean_json)
        except json.JSONDecodeError:
            return {"error": "AI-nin qaytardığı nəticə JSON formatında deyildi.", "raw": response_text}

ai_service = AIService(provider_name="openai") # Gələcəkdə bunu config-dən dinamik götürmək olar.
