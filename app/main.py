import time
from fastapi import FastAPI, HTTPException
import redis
import fakeredis  # <-- Adicionamos o simulador aqui
from app.utils import serializar_dados, deserializar_dados

app = FastAPI()

# Se o Docker não estiver rodando, o fakeredis assume o controle automaticamente
try:
    # Tenta conectar no Redis real (Docker)
    cliente_redis = redis.Redis(host="localhost", port=6379, decode_responses=True, socket_timeout=1)
    cliente_redis.ping()
except Exception:
    # Plano B: Se o Docker falhar, usa o Redis simulado em memória
    print("⚠️ Redis local não encontrado. Utilizando fakeredis para fins de testes.")
    cliente_redis = fakeredis.FakeStrictRedis(decode_responses=True)

def buscar_preco_na_api_externa(simbolo: str):
    """Simula uma chamada demorada para uma API externa."""
    time.sleep(2)  # Simula lentidão
    if simbolo.upper() == "INVALIDO":
        raise Exception("Erro na API externa")
    return {"simbolo": simbolo.upper(), "preco": 150.50, "fonte": "API Externa"}

@app.get("/preco/{simbolo}")
def obter_preco(simbolo: str):
    chave_cache = f"preco:{simbolo.lower()}"
    
    # 1. Tenta buscar do cache (Redis)
    if cliente_redis:
        try:
            dados_cached = cliente_redis.get(chave_cache)
            if dados_cached:
                resultado = deserializar_dados(dados_cached)
                resultado["fonte"] = "Cache (Redis)"
                return resultado
        except redis.Exceptions.ConnectionError:
            pass # Se o Redis cair, a API continua funcionando (Fall através)

    # 2. Se não achou ou Redis tá fora, busca na "API Externa"
    try:
        dados_reais = buscar_preco_na_api_externa(simbolo)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Serviço externo indisponível: {str(e)}")

    # 3. Salva no cache por 10 segundos (TTL)
    if cliente_redis:
        try:
            cliente_redis.setex(chave_cache, 10, serializar_dados(dados_reais))
        except redis.Exceptions.ConnectionError:
            pass

    return dados_reais

@app.post("/cache/clear")
def limpar_cache():
    """Endpoint exigido para limpar o cache."""
    if cliente_redis:
        cliente_redis.flushdb()
        return {"status": "Cache limpo com sucesso"}
    raise HTTPException(status_code=500, detail="Redis indisponível")
