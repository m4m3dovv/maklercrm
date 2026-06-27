# NEXORA CRM

Enterprise-level Telegram-based CRM System for Real Estate Agencies.
Developed using Clean Architecture and SOLID principles.

## 🚀 Texnologiyalar
- **Dil:** Python 3.13
- **Bot Framework:** aiogram 3.x
- **Verilənlər Bazası:** PostgreSQL
- **ORM:** asinxron SQLAlchemy 2.x
- **Miqrasiyalar:** Alembic
- **Validasiya:** Pydantic & Pydantic Settings
- **AI İnteqrasiyası:** OpenAI, Claude, Gemini (Strategy Pattern)
- **Konteynerləşdirmə:** Docker, Docker Compose
- **Testlər:** Pytest (Asinxron in-memory db ilə)

## 📁 Arxitektura Xülasəsi
Layihə "Domain-Driven Design" fəlsəfəsinə yaxın **Clean Architecture** ilə yazılıb:
1. `Bot (Handlers)` yalnız `Services`-lərə müraciət edir.
2. `Services` biznes məntiqini icra edir və `Repositories`-lərlə danışır.
3. `Repositories` birbaşa SQLAlchemy modelləri vasitəsilə `Database` ilə əlaqə qurur.

Bu struktur imkan verir ki, gələcəkdə `FastAPI` (REST API) əlavə edilərsə, bot-un məntiqi dəyişmədən eyni `Services` təkrar istifadə edilsin.

## 🛠 Qurulum (Lokal)

### 1. Docker vasitəsilə (Tövsiyə olunur)
```bash
# 1. Konfiqurasiya faylını yaradın
cp .env.example .env

# 2. Konteynerləri işə salın
docker-compose up -d --build
```
Bu həm PostgreSQL-i, həm də Bot-u eyni anda qaldıracaq. Başlamazdan əvvəl avtomatik olaraq verilənlər bazası miqrasiyaları (`alembic upgrade head`) baş tutacaq.

### 2. Manual (Docker olmadan)
```bash
python -m venv venv
source venv/bin/activate
pip install -e .[dev]

# Bazanı qurmaq üçün .env içərisində DATABASE_URL düzəldin və sonra:
alembic upgrade head

python app/bot/main.py
```

## 🧪 Testlərin İşlədilməsi
```bash
pytest
```
Testlər heç bir fiziki PostgreSQL bazası tələb etmir. Testlər çalışdıqda `in-memory` (yaddaşda) asinxron `sqlite` bazası yaradılır və test bitdikdə silinir.
