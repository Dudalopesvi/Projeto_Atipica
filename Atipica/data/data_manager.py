import json
import os

# Caminho absoluto relativo ao arquivo, funciona de qualquer diretório
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_USUARIOS = os.path.join(BASE_DIR, "..", "tpac_users.json")


def carregar_dados() -> dict:
    caminho = os.path.normpath(ARQUIVO_USUARIOS)
    if os.path.exists(caminho):
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def salvar_dados(dados: dict):
    caminho = os.path.normpath(ARQUIVO_USUARIOS)
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)


def perfil_padrao(nome: str, email: str, senha_hash: str, estilo: str,
                  preferencias_sensoriais: str, tipo_alerta: str) -> dict:
    """Retorna a estrutura completa de um novo usuário."""
    return {
        "nome": nome,
        "email": email,
        "senha": senha_hash,
        "tentativas_login": 0,
        "bloqueado": False,
        "codigo_desbloqueio": None,
        "preferencias": {
            "estilo_instrucao": estilo,          # "direto" | "detalhado"
            "preferencias_sensoriais": preferencias_sensoriais,  # "visual" | "sonoro" | "ambos"
            "tipo_alerta": tipo_alerta,           # "visual" | "sonoro" | "ambos"
            "lembretes_ativos": True
        },
        "pontuacao": 0,
        "tarefas_diarias": [],
        "tarefas_educacionais": [],
        "estudos": [],
        "lembretes": [],
        "historico": []
    }
