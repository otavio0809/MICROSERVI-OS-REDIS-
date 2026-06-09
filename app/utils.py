import json

def serializar_dados(dados: dict) -> str:
    if not isinstance(dados, dict):
        raise ValueError("Os dados precisam ser um dicionário")
    return json.dumps(dados)

def deserializar_dados(dados_str: str) -> dict:
    if not dados_str:
        return {}
    return json.loads(dados_str)