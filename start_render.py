
import os
import signal
import subprocess
import sys
import time
import urllib.request


def esperar_backend():
    url = "http://127.0.0.1:8000/health"

    for intento in range(30):
        try:
            with urllib.request.urlopen(
                url, timeout=2
            ) as respuesta:
                if respuesta.status == 200:
                    print(
                        "FastAPI disponible.",
                        flush=True
                    )
                    return True
        except Exception:
            pass

        if backend.poll() is not None:
            return False

        time.sleep(1)

    return False


def detener_procesos(signum=None, frame=None):
    for proceso in [frontend, backend]:
        if proceso.poll() is None:
            proceso.terminate()

    for proceso in [frontend, backend]:
        if proceso.poll() is None:
            try:
                proceso.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proceso.kill()

    sys.exit(0)


# Variables de entorno
os.environ["BACKEND_URL"] = (
    "http://127.0.0.1:8000"
)

puerto = os.environ.get("PORT", "8501")

# Iniciar backend
backend = subprocess.Popen([
    sys.executable,
    "-m",
    "uvicorn",
    "backend.main:app",
    "--host",
    "127.0.0.1",
    "--port",
    "8000"
])

if not esperar_backend():
    print(
        "ERROR: FastAPI no pudo iniciar.",
        flush=True
    )
    backend.terminate()
    sys.exit(1)

# Iniciar frontend
frontend = subprocess.Popen([
    sys.executable,
    "-m",
    "streamlit",
    "run",
    "frontend/app.py",
    "--server.address=0.0.0.0",
    f"--server.port={puerto}",
    "--server.headless=true"
])

signal.signal(signal.SIGTERM, detener_procesos)
signal.signal(signal.SIGINT, detener_procesos)

print(
    "Chatbot Actuario Vida iniciado.",
    flush=True
)

# Supervisar ambos procesos
while True:
    if backend.poll() is not None:
        print(
            "ERROR: FastAPI se detuvo.",
            flush=True
        )
        detener_procesos()

    if frontend.poll() is not None:
        print(
            "ERROR: Streamlit se detuvo.",
            flush=True
        )
        detener_procesos()

    time.sleep(2)
