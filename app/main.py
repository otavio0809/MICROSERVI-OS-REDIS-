import time
from fastapi import FastAPI, HTTPException
import redis
import fakeredis

from app.utils import serializar_dados, deserializar_dados

app = FastAPI()

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


def buscar_preco_na_api_externa(simbolo: str):
    time.sleep(2)

    if simbolo.upper() == "INVALIDO":
        raise Exception("Erro na API externa")

    return {
        "simbolo": simbolo.upper(),
        "preco": 150.50,
        "fonte": "API Externa"
    }


@app.get("/preco/{simbolo}")
def obter_preco(simbolo: str):

    chave_cache = f"preco:{simbolo.lower()}"

    if cliente_redis:
        try:
            dados_cached = cliente_redis.get(chave_cache)

            if dados_cached:
                resultado = deserializar_dados(dados_cached)
                resultado["fonte"] = "Cache (Redis)"
                resultado["cached"] = True
                return resultado

        except redis.exceptions.ConnectionError:
            pass

    try:
        dados_reais = buscar_preco_na_api_externa(simbolo)

    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Serviço externo indisponível: {str(e)}"
        )

    if cliente_redis:
        try:
            cliente_redis.setex(
                chave_cache,
                10,
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
        return {"status": "Cache limpo com sucesso"}

    raise HTTPException(
        status_code=500,
        detail="Redis indisponível"
    )