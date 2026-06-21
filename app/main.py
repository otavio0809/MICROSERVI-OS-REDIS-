import time
import logging  
from fastapi import FastAPI, HTTPException
import redis
import fakeredis

from app.utils import serializar_dados, deserializar_dados

# Configuração básica de log estruturado para monitoramento da aplicação
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("microservico_clima")

app = FastAPI(title="Microserviço de Cache Meteorológico")

# Dicionário global para armazenamento de métricas/contadores simples
metricas = {
    "cache_hits": 0,
    "cache_misses": 0
}

# Tentativa de conexão com o Redis (Docker ou Local)
try:
    cliente_redis = redis.Redis(
        host="localhost",
        port=6379,
        decode_responses=True,
        socket_timeout=1
    )
    cliente_redis.ping()
    logger.info("Conectado com sucesso ao Redis local.")
except Exception:
    logger.warning("Redis local não encontrado. Utilizando fakeredis para fins de testes.")
    cliente_redis = fakeredis.FakeStrictRedis(decode_responses=True)


# Endpoint /health para Health Check, incluindo estado dos componentes e métricas acumuladas
@app.get("/health")
def health_check():
    status_redis = "UNKNOWN"
    if cliente_redis:
        try:
            if cliente_redis.ping():
                status_redis = "UP"
        except Exception:
            status_redis = "DOWN"
            
    return {
        "status": "UP",
        "componentes": {
            "api": "UP",
            "cache_redis": status_redis
        },
        "metricas_acumuladas": metricas
    }


def buscar_clima_na_api_externa(cidade: str):
    """Simula uma consulta demorada a um serviço meteorológico externo (ex: OpenWeather)"""
    time.sleep(2)  # Simulando a lentidão da internet ou da API externa

    if cidade.upper() == "INVALIDA":
        logger.error(f"Tentativa de busca com cidade inválida no provedor: {cidade}")
        raise Exception("Cidade não encontrada no provedor meteorológico")
    return {
        "cidade": cidade.upper(),  # <-- Corrigido aqui!
        "temperatura": 28.5,
        "condicao": "Ensolarado",
        "fonte": "Serviço Meteorológico Externo"
    }

@app.get("/clima/{cidade}")
def obter_clima(cidade: str):
    chave_cache = f"clima:{cidade.lower()}"

    # Tenta buscar no Cache (Redis)
    if cliente_redis:
        try:
            dados_cached = cliente_redis.get(chave_cache)
            if dados_cached:
                logger.info(f"[CACHE HIT] Dados recuperados com sucesso do Redis para a cidade: {cidade}")
                metricas["cache_hits"] += 1  # Incrementa o contador de Hit
                resultado = deserializar_dados(dados_cached)
                resultado["fonte"] = "Cache (Redis)"
                resultado["cached"] = True
                return resultado
        except redis.exceptions.ConnectionError:
            logger.error("Falha de conexão com o Redis durante a leitura. Prosseguindo com fallback.")
            pass  # Se o Redis cair, o sistema continua funcionando (Fallback)

    # Se não estava no cache (Cache Miss), busca na API Externa
    logger.info(f"[CACHE MISS] Solicitando dados na API externa para a cidade: {cidade}")
    metricas["cache_misses"] += 1  # Incrementa o contador de Miss
    
    try:
        dados_reais = buscar_clima_na_api_externa(cidade)
    except Exception as e:
        logger.critical(f"Erro crítico ao consultar o provedor externo: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail=f"Serviço de meteorologia indisponível: {str(e)}"
        )

    # Salva no Cache para as próximas consultas (com TTL de 10 segundos)
    if cliente_redis:
        try:
            cliente_redis.setex(
                chave_cache,
                10,  # Tempo de vida do cache em segundos
                serializar_dados(dados_reais)
            )
        except redis.exceptions.ConnectionError:
            logger.error("Falha de conexão com o Redis durante a gravação do cache.")
            pass

    dados_reais["cached"] = False
    return dados_reais


@app.post("/cache/clear")
def limpar_cache():
    if cliente_redis:
        cliente_redis.flushdb()
        logger.info("O cache meteorológico foi limpo manualmente via requisição de API.")
        return {"status": "Cache meteorológico limpo com sucesso"}

    raise HTTPException(
        status_code=500,
        detail="Redis indisponível"
    )