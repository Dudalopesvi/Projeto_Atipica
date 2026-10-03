import json
import os
from copy import deepcopy

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_USUARIOS = os.path.join(BASE_DIR, "..", "tpac_users.json")
ARQUIVO_COMUNIDADE = os.path.join(BASE_DIR, "..", "tpac_community.json")

BIBLIOTECA_BASE = [
    {"id": "art-rotina-visual", "titulo": "Rotinas visuais e previsibilidade", "tipo": "Artigo", "categoria": "rotina", "descricao": "Estratégias para organizar atividades com apoio visual.", "fonte": "Autoria Atípica", "url": ""},
    {"id": "art-comunicacao", "titulo": "Comunicação acessível no dia a dia", "tipo": "Artigo", "categoria": "comunicacao", "descricao": "Princípios para reduzir ambiguidades e ampliar a participação.", "fonte": "Autoria Atípica", "url": ""},
    {"id": "livro-temple", "titulo": "O cérebro autista", "tipo": "Livro", "categoria": "leitura", "descricao": "Introdução a diferentes formas de perceber e interagir com o mundo.", "fonte": "Temple Grandin", "url": ""},
    {"id": "livro-neurodiversidade", "titulo": "Neurodiversidade: um olhar para além do diagnóstico", "tipo": "Livro", "categoria": "leitura", "descricao": "Conteúdo introdutório sobre inclusão e respeito às diferenças.", "fonte": "Biblioteca Atípica", "url": ""},
    {"id": "serie-atypical", "titulo": "Atypical", "tipo": "Série", "categoria": "audiovisual", "descricao": "Série de ficção que aborda adolescência, família e autismo.", "fonte": "Netflix", "url": ""},
    {"id": "filme-temple", "titulo": "Temple Grandin", "tipo": "Filme", "categoria": "audiovisual", "descricao": "Filme biográfico sobre uma profissional autista e sua trajetória.", "fonte": "Cinema", "url": ""},
]


def _usuario_sugerido(nome, email):
    base = "".join(char.lower() if char.isalnum() else "-" for char in (nome or "pessoa")).strip("-") or "pessoa"
    sufixo = "".join(char for char in (email or "").lower().split("@", 1)[0] if char.isalnum())[-4:]
    return f"{base[:20]}-{sufixo}".strip("-")[:30]


def _normalizar_perfil(perfil):
    perfil.setdefault("nome", "")
    perfil.setdefault("nome_crianca", "")
    perfil.setdefault("informacoes_crianca", {"idade": "", "comunicacao": "", "necessidades": "", "interesses": ""})
    perfil.setdefault("questionario", {"respondido": False, "respostas": {}, "atualizado_em": ""})
    perfil.setdefault("rede_apoio", [])
    perfil.setdefault("profissionais", [])
    perfil.setdefault("interacoes", [])
    perfil.setdefault("biblioteca", [])
    perfil.setdefault("historico", [])
    perfil.setdefault("tarefas_diarias", [])
    perfil.setdefault("tarefas_educacionais", [])
    perfil.setdefault("estudos", [])
    perfil.setdefault("lembretes", [])
    perfil.setdefault("pontuacao", 0)
    publico = perfil.setdefault("usuario_publico", {})
    publico.setdefault("nome_exibicao", perfil.get("nome", ""))
    publico.setdefault("usuario", _usuario_sugerido(perfil.get("nome", ""), perfil.get("email", "")))
    publico.setdefault("bio", "")
    publico.setdefault("visibilidade", "publico")
    comunidade = perfil.setdefault("comunidade", {})
    comunidade.setdefault("seguindo", [])
    comunidade.setdefault("seguidores", [])
    comunidade.setdefault("publicacoes", [])
    preferencias = perfil.setdefault("preferencias", {})
    preferencias.setdefault("estilo_instrucao", "direto")
    preferencias.setdefault("preferencias_sensoriais", "visual")
    preferencias.setdefault("tipo_alerta", "visual")
    preferencias.setdefault("lembretes_ativos", True)
    preferencias.setdefault("compartilhar_com_ia", False)
    preferencias.setdefault("ia_permissoes", {"perfil": False, "preferencias": False, "rotina": False, "historico": False})
    permissoes_ia = preferencias["ia_permissoes"]
    if not isinstance(permissoes_ia, dict):
        permissoes_ia = {}
        preferencias["ia_permissoes"] = permissoes_ia
    for categoria in ("perfil", "preferencias", "rotina", "historico"):
        permissoes_ia.setdefault(categoria, False)
    perfil.setdefault("ia_permissoes_log", [])
    for tarefa in perfil["tarefas_diarias"] + perfil["tarefas_educacionais"]:
        tarefa.setdefault("periodo", "manha")
        tarefa.setdefault("pontos", 10)
        tarefa.setdefault("passos", [])
        if not tarefa["passos"]:
            tarefa["passos"] = [{"texto": tarefa.get("titulo", "Atividade"), "concluida": bool(tarefa.get("concluida", False))}]
        tarefa.setdefault("tempo_limite_min", 0)
        tarefa.setdefault("concluida", False)
    for lembrete in perfil["lembretes"]:
        lembrete.setdefault("ativo", True)
        lembrete.setdefault("tipo_alerta", preferencias["tipo_alerta"])
    return perfil


def carregar_dados():
    caminho = os.path.normpath(ARQUIVO_USUARIOS)
    if not os.path.exists(caminho):
        return {}
    with open(caminho, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    alterado = False
    for perfil in dados.values():
        antes = repr(perfil)
        _normalizar_perfil(perfil)
        alterado = alterado or antes != repr(perfil)
    if alterado:
        salvar_dados(dados)
    return dados


def salvar_dados(dados):
    caminho = os.path.normpath(ARQUIVO_USUARIOS)
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    temporario = caminho + ".tmp"
    with open(temporario, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=2, ensure_ascii=False)
    os.replace(temporario, caminho)


def carregar_comunidade():
    caminho = os.path.normpath(ARQUIVO_COMUNIDADE)
    if not os.path.exists(caminho):
        return {"conversas": {}, "grupos": {}}
    with open(caminho, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    dados.setdefault("conversas", {})
    dados.setdefault("grupos", {})
    return dados


def salvar_comunidade(dados):
    caminho = os.path.normpath(ARQUIVO_COMUNIDADE)
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    temporario = caminho + ".tmp"
    with open(temporario, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=2, ensure_ascii=False)
    os.replace(temporario, caminho)


def perfil_padrao(nome, email, senha_hash, estilo="direto", preferencias_sensoriais="visual", tipo_alerta="visual", nome_crianca="", informacoes_crianca=None):
    return {
        "nome": nome,
        "nome_crianca": nome_crianca,
        "email": email,
        "senha": senha_hash,
        "tentativas_login": 0,
        "bloqueado": False,
        "codigo_desbloqueio": None,
        "preferencias": {"estilo_instrucao": estilo, "preferencias_sensoriais": preferencias_sensoriais, "tipo_alerta": tipo_alerta, "lembretes_ativos": True, "compartilhar_com_ia": False, "ia_permissoes": {"perfil": False, "preferencias": False, "rotina": False, "historico": False}},
        "informacoes_crianca": informacoes_crianca or {"idade": "", "comunicacao": "", "necessidades": "", "interesses": ""},
        "usuario_publico": {"nome_exibicao": nome, "usuario": _usuario_sugerido(nome, email), "bio": "", "visibilidade": "publico"},
        "comunidade": {"seguindo": [], "seguidores": [], "publicacoes": []},
        "questionario": {"respondido": False, "respostas": {}, "atualizado_em": ""},
        "rede_apoio": [], "profissionais": [], "interacoes": [], "biblioteca": [],
        "pontuacao": 0, "tarefas_diarias": [], "tarefas_educacionais": [], "estudos": [], "lembretes": [], "historico": [], "ia_permissoes_log": [],
    }


def listar_biblioteca(termo="", tipo=""):
    itens = deepcopy(BIBLIOTECA_BASE)
    termo = (termo or "").strip().lower()
    tipo = (tipo or "").strip().lower()
    if termo:
        itens = [item for item in itens if termo in " ".join(str(item.get(chave, "")) for chave in ("titulo", "descricao", "categoria", "fonte")).lower()]
    if tipo and tipo != "todos":
        itens = [item for item in itens if item["tipo"].lower() == tipo]
    return itens


def listar_rede_apoio(dados=None, usuario=None):
    if dados is None:
        dados = carregar_dados()
    if usuario and usuario in dados:
        return dados[usuario].get("rede_apoio", [])
    return []