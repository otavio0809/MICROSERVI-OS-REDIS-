import json

def serializar_dados(dados: dict) -> str:
    """Converte dicionário para string JSON para salvar no Redis."""
    if not isinstance(dados, dict):
        raise ValueError("Os dados precisam ser um dicionário")
    return json.dumps(dados)

def deserializar_dados(dados_str: str) -> dict:
    """Converte string JSON do Redis de volta para dicionário Python."""
    if not dados_str:
        return {}
    return json.loads(dados_str)