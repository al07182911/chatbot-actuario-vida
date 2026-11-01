
# Imagen base de Python
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del frontend
COPY frontend/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir \
    -r /app/requirements.txt

# Copiar interfaz Streamlit
COPY frontend/ /app/frontend/

# Crear usuario sin privilegios
RUN useradd --create-home appuser \
    && chown -R appuser:appuser /app

USER appuser

# Puerto de Streamlit
EXPOSE 8501

# Iniciar interfaz web
CMD ["streamlit", "run", "frontend/app.py", \
     "--server.address=0.0.0.0", \
     "--server.port=8501", \
     "--server.headless=true"]
