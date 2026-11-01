import os
import hmac
import requests
import streamlit as st
import time


# Configuracion de la aplicacion
st.set_page_config(
    page_title="Chatbot Actuario Vida",
    page_icon="🛡️",
    layout="centered"
)



# ==========================================
# CONTROL DE ACCESO - DEMOSTRACION ACADEMICA
# ==========================================

CLAVE_ACCESO = os.getenv(
    "CHATBOT_ACCESS_PASSWORD",
    ""
)

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# Control basico de intentos de acceso
MAX_INTENTOS = 5
BLOQUEO_SEGUNDOS = 300

if "intentos_fallidos" not in st.session_state:
    st.session_state.intentos_fallidos = 0

if "bloqueado_hasta" not in st.session_state:
    st.session_state.bloqueado_hasta = 0.0


# No permitir acceso si falta configuracion
if not CLAVE_ACCESO:
    st.error(
        "El acceso no esta configurado. "
        "Contacta al administrador."
    )
    st.stop()

# Pantalla de autenticacion
if not st.session_state.autenticado:

    st.title("Chatbot Actuario Vida")

    st.subheader(
        "Acceso a demostracion academica"
    )

    st.info(
        "Esta aplicacion es un prototipo academico. "
        "No utiliza polizas reales ni realiza "
        "cancelaciones de seguros."
    )

    with st.form("formulario_acceso"):

        password = st.text_input(
            "Contraseña de acceso",
            type="password"
        )

        ingresar = st.form_submit_button(
            "Ingresar al chatbot"
        )

    
    if ingresar:

        ahora = time.time()

        if ahora < st.session_state.bloqueado_hasta:

            restante = int(
                st.session_state.bloqueado_hasta - ahora
            )

            st.error(
                "Acceso temporalmente bloqueado. "
                f"Intenta nuevamente en {restante} segundos."
            )

        elif hmac.compare_digest(
            password.encode("utf-8"),
            CLAVE_ACCESO.encode("utf-8")
        ):

            st.session_state.autenticado = True
            st.session_state.intentos_fallidos = 0
            st.session_state.bloqueado_hasta = 0.0

            st.rerun()

        else:

            st.session_state.intentos_fallidos += 1

            if (
                st.session_state.intentos_fallidos
                >= MAX_INTENTOS
            ):

                st.session_state.bloqueado_hasta = (
                    ahora + BLOQUEO_SEGUNDOS
                )

                st.session_state.intentos_fallidos = 0

                st.error(
                    "Demasiados intentos incorrectos. "
                    "Acceso bloqueado durante 5 minutos."
                )

            else:

                st.error("Contraseña incorrecta.")


    st.stop()


# Direccion del backend FastAPI
API_URL = os.getenv(
    "BACKEND_URL",
    "http://localhost:8000"
).rstrip("/")

# Encabezado
st.title("Chatbot Actuario Vida")

st.caption(
    "Asistente inteligente para seguros de vida"
)

st.info(
    "Prototipo academico. No realiza cotizaciones "
    "oficiales, modificaciones ni cancelaciones "
    "reales de polizas."
)

# Inicializar el estado de la interfaz
if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {
            "role": "assistant",
            "content": (
                "¡Hola! Soy el asistente virtual "
                "de seguros de vida. "
                "Puedo ayudarte a explorar alternativas "
                "antes de cancelar tu poliza. "
                "¿En que puedo ayudarte?"
            )
        }
    ]

if "sesion_id" not in st.session_state:
    st.session_state.sesion_id = None

if "finalizada" not in st.session_state:
    st.session_state.finalizada = False


# Barra lateral
with st.sidebar:

    st.header("Chatbot Actuario Vida")
    
    if st.button(
        "Cerrar sesion",
        use_container_width=True
    ):
        st.session_state.clear()
        st.rerun()


    st.write("Rutas de atencion:")
    st.write("1. Economia personal")
    st.write("2. Beneficios del seguro")
    st.write("3. Mala experiencia de servicio")

    if st.button(
        "Nueva conversacion",
        use_container_width=True
    ):
        st.session_state.mensajes = [
            {
                "role": "assistant",
                "content": (
                    "¡Hola! ¿En que puedo ayudarte "
                    "con tu seguro de vida?"
                )
            }
        ]

        st.session_state.sesion_id = None
        st.session_state.finalizada = False
        st.rerun()


# Mostrar historial de conversacion
for mensaje in st.session_state.mensajes:

    with st.chat_message(mensaje["role"]):
        st.markdown(mensaje["content"])


# Recibir mensaje del cliente
mensaje_cliente = st.chat_input(
    "Escribe tu mensaje...",
    disabled=st.session_state.finalizada
)

if mensaje_cliente:

    # Mostrar mensaje del cliente
    st.session_state.mensajes.append({
        "role": "user",
        "content": mensaje_cliente
    })

    with st.chat_message("user"):
        st.markdown(mensaje_cliente)

    # Preparar solicitud a FastAPI
    datos = {
        "mensaje": mensaje_cliente
    }

    if st.session_state.sesion_id is not None:
        datos["sesion_id"] = (
            st.session_state.sesion_id
        )

    # Consultar el backend
    with st.chat_message("assistant"):

        with st.spinner("Analizando tu mensaje..."):

            try:
                respuesta = requests.post(
                    f"{API_URL}/chat/unificado",
                    json=datos,
                    timeout=90
                )

                respuesta.raise_for_status()

                resultado = respuesta.json()

                texto_respuesta = resultado["respuesta"]

                st.session_state.sesion_id = (
                    resultado.get("sesion_id")
                )

                if resultado.get("estado") == "finalizada":
                    st.session_state.finalizada = True

                st.markdown(texto_respuesta)

                st.session_state.mensajes.append({
                    "role": "assistant",
                    "content": texto_respuesta
                })

            except requests.exceptions.RequestException:
                st.error(
                    "No fue posible conectar con el chatbot. "
                    "Verifica que el backend este disponible."
                )

            except (ValueError, KeyError):
                st.error(
                    "El backend devolvio una respuesta "
                    "que no pudo procesarse."
                )
