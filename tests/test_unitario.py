import pytest
from app.utils import serializar_dados, deserializar_dados
#Testa a conversão de Dicionário Python para Texto JSON (Validar o fluxo padrão de salvamento no cache).
def test_serializar_com_sucesso():
    dados = {"produto": "soja", "valor": 100}
    resultado = serializar_dados(dados)
    assert resultado == '{"produto": "soja", "valor": 100}'

#Testa a conversão de Texto JSON para Dicionário Python (Validar o fluxo padrão de leitura do cache).
def test_deserializar_com_sucesso():
    json_str = '{"produto": "milho", "valor": 50}'
    resultado = deserializar_dados(json_str)
    assert resultado["produto"] == "milho"
    assert resultado["valor"] == 50

#Testa se o sistema bloqueia e rejeita dados inválidos (Validar o comportamento de segurança).
def test_serializar_deve_lancar_erro_se_nao_for_dicionario():
    with pytest.raises(ValueError):
        serializar_dados("isso é uma string, vai falhar")