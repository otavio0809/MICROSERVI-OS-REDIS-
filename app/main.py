import time
from fastapi import FastAPI, HTTPException
import redis
import fakeredis

from app.utils import serializar_dados, deserializar_dados

app = FastAPI(title="Microserviço de Cache Meteorológico")

# Tentativa de conexão com o Redis (Docker ou Local)
try:
    cliente_redis = redis.Redis(
        host="localhost",
        port=6379,
        decode_responses=True,
        socket_timeout=1
    )
    cliente_redis.ping()
except Exception:
    print("Redis local não encontrado. Utilizando fakeredis para fins de testes.")
    cliente_redis = fakeredis.FakeStrictRedis(decode_responses=True)


def buscar_clima_na_api_externa(cidade: str):
    """Simula uma consulta demorada a um serviço meteorológico externo (ex: OpenWeather)"""
    time.sleep(2)  # Simulando a lentidão da internet/API externa

    if cidade.upper() == "INVALIDA":
        raise Exception("Cidade não encontrada no provedor meteorológico")

    # Dados simulados baseados na cidade
    return {
        "cidade": cidade.upper(),
        "temperatura": 28.5,
        "condicao": "Ensolarado",
        "fonte": "Serviço Meteorológico Externo"
    }


@app.get("/clima/{cidade}")
def obter_clima(cidade: str):
    chave_cache = f"clima:{cidade.lower()}"

    # 1. Tenta buscar no Cache (Redis)
    if cliente_redis:
        try:
            dados_cached = cliente_redis.get(chave_cache)
            if dados_cached:
                resultado = deserializar_dados(dados_cached)
                resultado["fonte"] = "Cache (Redis)"
                resultado["cached"] = True
                return resultado
        except redis.exceptions.ConnectionError:
            pass  # Se o Redis cair, o sistema continua funcionando (Fallback)

    # 2. Se não estava no cache (Cache Miss), busca na API Externa
    try:
        dados_reais = buscar_clima_na_api_externa(cidade)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Serviço de meteorologia indisponível: {str(e)}"
        )

    # 3. Salva no Cache para as próximas consultas (com TTL de 10 segundos)
    if cliente_redis:
        try:
            cliente_redis.setex(
                chave_cache,
                10,  # Tempo de vida do cache em segundos
                serializar_dados(dados_reais)
            )
        except redis.exceptions.ConnectionError:
            pass

    dados_reais["cached"] = False
    return dados_reais


@app.post("/cache/clear")
def limpar_cache():
    if cliente_redis:
        cliente_redis.flushdb()
        return {"status": "Cache meteorológico limpo com sucesso"}

    raise HTTPException(
        status_code=500,
        detail="Redis indisponível"
    )