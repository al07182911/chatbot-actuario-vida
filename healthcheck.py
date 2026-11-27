
import os
import sys
import urllib.request


def comprobar_servicio(nombre, url):

    try:

        with urllib.request.urlopen(
            url,
            timeout=3
        ) as respuesta:

            if respuesta.status != 200:
                print(
                    f"{nombre}: HTTP {respuesta.status}"
                )
                return False

        print(f"{nombre}: OK")
        return True

    except Exception as error:

        print(
            f"{nombre}: ERROR - "
            f"{type(error).__name__}"
        )

        return False


def main():

    puerto = os.environ.get("PORT", "8501")

    backend_ok = comprobar_servicio(
        "FastAPI",
        "http://127.0.0.1:8000/health"
    )

    frontend_ok = comprobar_servicio(
        "Streamlit",
        f"http://127.0.0.1:{puerto}/_stcore/health"
    )

    if backend_ok and frontend_ok:
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
