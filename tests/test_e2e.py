from fastapi.testclient import TestClient

from app.main import app, cliente_redis

client = TestClient(app)


def test_fluxo_e2e_ciclo_de_vida_do_cache():

    if cliente_redis:
        cliente_redis.flushall()

    simbolo_teste = "BTC"

    # Primeira chamada -> Cache Miss
    resposta_1 = client.get(f"/preco/{simbolo_teste}")

    assert resposta_1.status_code == 200

    dados_1 = resposta_1.json()

    assert dados_1["cached"] is False
    assert dados_1["fonte"] == "API Externa"

    # Segunda chamada -> Cache Hit
    resposta_2 = client.get(f"/preco/{simbolo_teste}")

    assert resposta_2.status_code == 200

    dados_2 = resposta_2.json()

    assert dados_2["cached"] is True
    assert dados_2["fonte"] == "Cache (Redis)"

    # Limpeza do cache
    resposta_limpeza = client.post("/cache/clear")

    assert resposta_limpeza.status_code == 200
    assert resposta_limpeza.json() == {
        "status": "Cache limpo com sucesso"
    }

    # Após limpar -> volta a ser Cache Miss
    resposta_3 = client.get(f"/preco/{simbolo_teste}")

    assert resposta_3.status_code == 200

    dados_3 = resposta_3.json()

    assert dados_3["cached"] is False
    assert dados_3["fonte"] == "API Externa"