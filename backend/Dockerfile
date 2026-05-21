# Imagen oficial slim de Python para reducir el tamano del contenedor.
FROM python:3.12-slim

# Variables que mejoran el comportamiento de Python dentro de containers:
# PYTHONDONTWRITEBYTECODE evita los .pyc; PYTHONUNBUFFERED hace que los logs
# salgan en tiempo real, util al hacer docker-compose logs.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Paquetes de sistema requeridos para compilar psycopg2 (libpq-dev) y bcrypt
# (build-essential). curl se queda para health checks manuales.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Se copia primero requirements.txt para aprovechar la cache de Docker:
# si no cambian las dependencias, este layer no se reconstruye.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Se copia el resto del codigo de la app.
COPY . .

EXPOSE 8000

# Comando por defecto. En docker-compose se sobrescribe para correr antes
# las migraciones de Alembic y habilitar --reload en desarrollo.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
