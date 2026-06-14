import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app, cliente_redis

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(autouse=True)
def limpar_redis_antes_e_depois():
    cliente_redis.flushdb()
    yield
    cliente_redis.flushdb()


def test_fluxo_integracao_clima_cache_miss_e_hit(client):
    mock_retorno_clima = {
        "cidade": "PALMAS",
        "temperatura": 28.5,
        "condicao": "Ensolarado",
        "fonte": "Serviço Meteorológico Externo"
    }
    
    with patch("app.main.buscar_clima_na_api_externa") as mock_api:
        mock_api.return_value = mock_retorno_clima

        # 1ª Chamada: Tem que ir na API Externa (Cache Miss)
        resposta_1 = client.get("/clima/palmas")
        assert resposta_1.status_code == 200
        assert resposta_1.json()["fonte"] == "Serviço Meteorológico Externo"
        assert resposta_1.json()["cached"] is False
        mock_api.assert_called_once_with("palmas")

        # 2ª Chamada: Tem que vir do Redis (Cache Hit)
        resposta_2 = client.get("/clima/palmas")
        assert resposta_2.status_code == 200
        assert resposta_2.json()["fonte"] == "Cache (Redis)"
        assert resposta_2.json()["cached"] is True
        # O contador continua 1, provando que a API externa NÃO foi chamada de novo
        assert mock_api.call_count == 1


def test_cenario_de_falha_api_meteorologia_indisponivel(client):
    with patch("app.main.buscar_clima_na_api_externa") as mock_api:
        mock_api.side_effect = Exception("Timeout ao conectar no provedor")

        resposta = client.get("/clima/palmas")
        
        assert resposta.status_code == 502
        assert "Serviço de meteorologia indisponível" in resposta.json()["detail"]