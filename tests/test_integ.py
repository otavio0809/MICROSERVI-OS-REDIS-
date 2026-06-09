from fastapi.testclient import TestClient
from app.main import app, cliente_redis

client = TestClient(app)

def test_fluxo_integracao_cache_e_limpeza():
    client.post("/cache/clear")
    
    resposta_1 = client.get("/preco/ouro")
    assert resposta_1.status_code == 200
    assert resposta_1.json()["fonte"] == "API Externa"
    
    resposta_2 = client.get("/preco/ouro")
    assert resposta_2.status_code == 200
    assert resposta_2.json()["fonte"] == "Cache (Redis)"

def test_cenario_de_falha_api_externa():
    resposta = client.get("/preco/invalido")
    assert resposta.status_code == 502
    assert "Serviço externo indisponível" in resposta.json()["detail"]