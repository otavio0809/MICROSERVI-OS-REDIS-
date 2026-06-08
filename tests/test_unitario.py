import pytest
from app.utils import serializar_dados, deserializar_dados

def test_serializar_com_sucesso():
    dados = {"produto": "soja", "valor": 100}
    resultado = serializar_dados(dados)
    assert resultado == '{"produto": "soja", "valor": 100}'

def test_deserializar_com_sucesso():
    json_str = '{"produto": "milho", "valor": 50}'
    resultado = deserializar_dados(json_str)
    assert resultado["produto"] == "milho"
    assert resultado["valor"] == 50

def test_serializar_deve_lancar_erro_se_nao_for_dicionario():
    with pytest.raises(ValueError):
        serializar_dados("isso é uma string, vai falhar")