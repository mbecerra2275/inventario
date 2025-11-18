# =============================
# 🐳 Dockerfile - Sistema de Inventario (FastAPI)
# =============================

# Etapa base: usa Python 3.12 en su versión ligera (slim)
FROM python:3.12-slim

# Define el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos de dependencias primero (para aprovechar la cache)
COPY requirements.txt .

# Instala las dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código del backend
COPY . .

# Expone el puerto donde se ejecutará FastAPI
EXPOSE 8000

# Comando por defecto al iniciar el contenedor
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--workers", "4", "--bind", "0.0.0.0:8000"]
