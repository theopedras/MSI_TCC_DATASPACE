"""Testes da camada de interoperabilidade (funções puras)."""

import pytest

from interoperability import normalize_ibge_code, per_100k, to_float


def test_normalize_ibge_code_limpa_mascara():
    assert normalize_ibge_code("3106200") == "3106200"
    assert normalize_ibge_code(3106200) == "3106200"


def test_normalize_ibge_code_valida_7_digitos():
    with pytest.raises(ValueError):
        normalize_ibge_code("31062")


def test_to_float_aceita_int_e_float():
    assert to_float(2530701) == 2530701.0
    assert to_float(2.5) == 2.5


def test_to_float_inteiro_em_string():
    assert to_float("2530701") == 2530701.0


def test_to_float_milhar_brasileiro():
    assert to_float("2.530.701") == 2530701.0


def test_to_float_decimal_com_virgula():
    assert to_float("1.234,56") == 1234.56


def test_per_100k():
    assert per_100k(83, 2530701) == pytest.approx(3.279, abs=0.001)


def test_per_100k_zero_levanta():
    with pytest.raises(ZeroDivisionError):
        per_100k(10, 0)


def test_normalize_cnpj_limpa_mascara():
    from interoperability import normalize_cnpj

    assert normalize_cnpj("18.715.383/0001-40") == "18715383000140"
    assert normalize_cnpj(18715383000140) == "18715383000140"


def test_normalize_cnpj_valida_14_digitos():
    from interoperability import normalize_cnpj

    with pytest.raises(ValueError):
        normalize_cnpj("12345")
