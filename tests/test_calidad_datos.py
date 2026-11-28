
import json
import re
from pathlib import Path

import pytest

from backend.beneficios import consultar_beneficios


RUTA_CATALOGO = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "beneficios_polizas.json"
)


def rechazar_claves_duplicadas(pares):
    resultado = {}

    for clave, valor in pares:
        if clave in resultado:
            raise ValueError(
                f"Clave duplicada: {clave}"
            )

        resultado[clave] = valor

    return resultado


@pytest.fixture
def catalogo():
    return json.loads(
        RUTA_CATALOGO.read_text(encoding="utf-8"),
        object_pairs_hook=rechazar_claves_duplicadas
    )


# DQ-01: Validez del archivo JSON
def test_dq01_json_valido():
    assert RUTA_CATALOGO.is_file()

    datos = json.loads(
        RUTA_CATALOGO.read_text(encoding="utf-8")
    )

    assert datos is not None


# DQ-02: Estructura principal
def test_dq02_estructura_catalogo(catalogo):
    assert isinstance(catalogo, dict)
    assert len(catalogo) > 0


# DQ-03: Unicidad de identificadores
def test_dq03_identificadores_unicos(catalogo):
    identificadores = [
        clave.strip().upper()
        for clave in catalogo
    ]

    assert len(identificadores) == len(
        set(identificadores)
    )


# DQ-04: Formato de identificadores
def test_dq04_formato_identificadores(catalogo):
    for identificador in catalogo:
        assert re.fullmatch(
            r"VIDA-[0-9]{3}",
            identificador
        ), identificador


# DQ-05: Listas de beneficios
def test_dq05_lista_beneficios(catalogo):
    for poliza, beneficios in catalogo.items():
        assert isinstance(beneficios, list), poliza
        assert len(beneficios) > 0, poliza


# DQ-06: Campos obligatorios
def test_dq06_campos_obligatorios(catalogo):
    campos = {
        "nombre",
        "descripcion",
        "vigente"
    }

    for poliza, beneficios in catalogo.items():
        for beneficio in beneficios:
            assert isinstance(beneficio, dict)
            assert campos.issubset(
                beneficio.keys()
            ), poliza


# DQ-07: Nombres validos
def test_dq07_nombres_validos(catalogo):
    for beneficios in catalogo.values():
        for beneficio in beneficios:
            nombre = beneficio["nombre"]

            assert isinstance(nombre, str)
            assert nombre.strip()


# DQ-08: Descripciones validas
def test_dq08_descripciones_validas(catalogo):
    for beneficios in catalogo.values():
        for beneficio in beneficios:
            descripcion = beneficio["descripcion"]

            assert isinstance(descripcion, str)
            assert descripcion.strip()


# DQ-09: Vigencia booleana
def test_dq09_vigencia_booleana(catalogo):
    for beneficios in catalogo.values():
        for beneficio in beneficios:
            assert type(
                beneficio["vigente"]
            ) is bool


# DQ-10: Beneficios unicos por poliza
def test_dq10_beneficios_unicos(catalogo):
    for poliza, beneficios in catalogo.items():

        nombres = [
            beneficio["nombre"].strip().casefold()
            for beneficio in beneficios
        ]

        assert len(nombres) == len(
            set(nombres)
        ), poliza


# DQ-11: Consistencia entre datos y backend
def test_dq11_consistencia_backend(catalogo):
    for poliza, beneficios in catalogo.items():

        esperados = [
            {
                "nombre": beneficio["nombre"],
                "descripcion": beneficio["descripcion"]
            }
            for beneficio in beneficios
            if beneficio["vigente"] is True
        ]

        resultado = consultar_beneficios(
            poliza,
            ruta_archivo=RUTA_CATALOGO
        )

        assert resultado["encontrada"] is True
        assert resultado["id_poliza"] == poliza
        assert resultado["beneficios"] == esperados
