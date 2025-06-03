FROM python:3.13-slim

ENV PYTHONDONTWRITEEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN apt-get update  && apt-get install -y --no-install-recommends build-essential \
    python3-distutils \
    python3-setuptools

WORKDIR /app

COPY . .

RUN python -m pip install --no-cache-dir --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]
