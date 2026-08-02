# ---- Builder stage: install dependencies ----
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt


# ---- Final stage: runtime image ----
FROM python:3.11-slim

RUN useradd --create-home --shell /bin/bash app

WORKDIR /app

COPY --from=builder --chown=app:app /root/.local /home/app/.local
COPY --chown=app:app app/ ./app/

ENV PATH=/home/app/.local/bin:$PATH

USER app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
