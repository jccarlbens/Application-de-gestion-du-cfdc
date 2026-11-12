FROM python:3.12-slim

RUN pip install --no-cache-dir "uv>=0.11,<0.12"

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PROJECT_ENVIRONMENT=/opt/venv PATH="/opt/venv/bin:$PATH"

# Les dépendances d'abord, pour que le cache Docker survive à un changement de code.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .
RUN uv sync --frozen --no-dev

# Render fournit PORT ; en local, 8000.
ENV PORT=8000
EXPOSE 8000

# Les migrations passent avant chaque démarrage : une base en retard ne sert jamais l'API.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --proxy-headers --forwarded-allow-ips='*'"]
