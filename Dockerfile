# 1. Asılılıqların quraşdırılması mərhələsi (Builder)
FROM python:3.13-slim as builder

# Əməliyyat sistemi asılılıqlarını quraşdırırıq
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Asılılıq faylını kopyalayırıq
COPY pyproject.toml .

# Tək bir qovluğa asılılıqları (wheels olaraq) yığırıq ki, növbəti mərhələ təmiz olsun
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -e .[dev] && \
    pip wheel --no-cache-dir --wheel-dir /app/wheels \
    aiogram sqlalchemy asyncpg alembic pydantic pydantic-settings greenlet pandas openpyxl fpdf2 openai anthropic google-generativeai

# 2. İcra mərhələsi (Runner)
FROM python:3.13-slim

# Gərəkli runtime kitabxanaları (PostgreSQL asılılığı)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Builder-dən kitabxanaları kopyalayırıq
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Kodları kopyalayırıq
COPY . .

# Konfiqurasiya mühiti (Default olaraq /app)
ENV PYTHONPATH=/app

# Başlanğıc skripti (Əvvəl miqrasiya edir, sonra botu işə salır)
CMD ["sh", "-c", "alembic upgrade head && python app/bot/main.py"]
