from fastapi.testclient import TestClient
from app.main import app, cliente_redis

client = TestClient(app)

def test_fluxo_e2e_ciclo_de_vida_do_cache_meteorologico():
    if cliente_redis:
        cliente_redis.flushall()

    cidade_teste = "London"

    # 1. Primeira chamada -> Cache Miss
    resposta_1 = client.get(f"/clima/{cidade_teste}")
    assert resposta_1.status_code == 200
    assert resposta_1.json()["cached"] is False

    # 2. Segunda chamada -> Cache Hit (Rápido)
    resposta_2 = client.get(f"/clima/{cidade_teste}")
    assert resposta_2.status_code == 200
    assert resposta_2.json()["cached"] is True

    # 3. Limpeza do cache via rota do usuário
    resposta_limpeza = client.post("/cache/clear")
    assert resposta_limpeza.status_code == 200
    assert "limpo com sucesso" in resposta_limpeza.json()["status"]

    # 4. Terceira chamada pós-limpeza -> Deve ser Cache Miss de novo
    resposta_3 = client.get(f"/clima/{cidade_teste}")
    assert resposta_3.status_code == 200
    assert resposta_3.json()["cached"] is False
    
def test_endpoint_health_check():
    resposta = client.get("/health")
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "UP"
    assert "componentes" in resposta.json()
    assert "metricas_acumuladas" in resposta.json() 