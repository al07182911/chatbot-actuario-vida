
# Imagen base de Python
FROM python:3.11-slim

# Evitar archivos temporales de Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del backend
COPY backend/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir \
    -r /app/requirements.txt

# Copiar codigo y catalogo academico
COPY backend/ /app/backend/
COPY data/ /app/data/

# Crear usuario sin privilegios
RUN useradd --create-home appuser \
    && chown -R appuser:appuser /app

USER appuser

# Puerto del backend
EXPOSE 8000

# Iniciar FastAPI
CMD ["uvicorn", "backend.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000"]
