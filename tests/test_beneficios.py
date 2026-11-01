
import pytest

from backend.beneficios import consultar_beneficios


def test_poliza_vida_001():
    resultado = consultar_beneficios("VIDA-001")

    assert resultado["encontrada"] is True
    assert len(resultado["beneficios"]) == 2


def test_poliza_vida_002():
    resultado = consultar_beneficios("VIDA-002")

    nombres = [
        b["nombre"] for b in resultado["beneficios"]
    ]

    assert resultado["encontrada"] is True
    assert "Asistencia funeraria" in nombres
    assert "Apoyo psicologico telefonico" in nombres


def test_poliza_vida_003():
    resultado = consultar_beneficios("VIDA-003")

    assert resultado["encontrada"] is True
    assert len(resultado["beneficios"]) == 1


def test_poliza_inexistente():
    resultado = consultar_beneficios("VIDA-999")

    assert resultado["encontrada"] is False
    assert resultado["beneficios"] == []


def test_excluir_beneficio_no_vigente():
    resultado = consultar_beneficios("VIDA-001")

    nombres = [
        b["nombre"] for b in resultado["beneficios"]
    ]

    assert "Promocion de bienestar" not in nombres


def test_identificador_minusculas():
    resultado = consultar_beneficios("vida-001")

    assert resultado["encontrada"] is True
    assert resultado["id_poliza"] == "VIDA-001"
