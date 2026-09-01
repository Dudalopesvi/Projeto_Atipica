import hashlib
import os
import random
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from data.data_manager import _normalizar_perfil, carregar_comunidade, carregar_dados, salvar_comunidade, salvar_dados, perfil_padrao, listar_biblioteca
from core.ia_service import obter_resposta_ia, gerar_passos_tarefa

app = FastAPI(title="Atípica API", version="2.0")

_default_origins = {"http://localhost:5173", "http://127.0.0.1:5173"}
_configured_origins = {
    origin.strip().rstrip("/")
    for origin in os.environ.get("FRONTEND_ORIGIN", "").split(",")
    if origin.strip()
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(_default_origins | _configured_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()


def _encontrar_por_email(dados, email):
    for chave, perfil in dados.items():
        if perfil.get("email", "").lower() == email.lower():
            return chave, perfil
    return None, None


def _perfil_publico(perfil):
    return {
        "nome": perfil.get("nome", ""), "nome_crianca": perfil.get("nome_crianca", ""), "email": perfil.get("email", ""),
        "preferencias": perfil.get("preferencias", {}), "informacoes_crianca": perfil.get("informacoes_crianca", {}),
        "questionario": perfil.get("questionario", {}), "pontuacao": perfil.get("pontuacao", 0),
    }


def _get_perfil(email):
    dados = carregar_dados()
    chave, perfil = _encontrar_por_email(dados, email)
    if perfil is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return dados, chave, perfil


class Cadastro(BaseModel):
    nome: str = Field(min_length=2)
    nome_crianca: str = ""
    email: str
    senha: str = Field(min_length=6)
    idade_crianca: str = ""
    comunicacao_crianca: str = ""
    necessidades_crianca: str = ""
    interesses_crianca: str = ""
    estilo_instrucao: str = "direto"
    preferencias_sensoriais: str = "visual"
    tipo_alerta: str = "visual"


@app.post("/api/cadastro")
def cadastrar(payload: Cadastro):
    dados = carregar_dados()
    _, existente = _encontrar_por_email(dados, payload.email)
    if existente:
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")
    dados[payload.email.lower()] = perfil_padrao(
        payload.nome.strip(), payload.email.strip(), _hash_senha(payload.senha), payload.estilo_instrucao,
        payload.preferencias_sensoriais, payload.tipo_alerta, payload.nome_crianca.strip(),
        {"idade": payload.idade_crianca, "comunicacao": payload.comunicacao_crianca, "necessidades": payload.necessidades_crianca, "interesses": payload.interesses_crianca},
    )
    salvar_dados(dados)
    return _perfil_publico(dados[payload.email.lower()])


class Login(BaseModel):
    email: str
    senha: str


@app.post("/api/login")
def login(payload: Login):
    dados, chave, perfil = _get_perfil(payload.email)
    if perfil.get("bloqueado"):
        raise HTTPException(status_code=423, detail="Conta bloqueada. Use o código de desbloqueio.")
    if _hash_senha(payload.senha) != perfil.get("senha"):
        perfil["tentativas_login"] = perfil.get("tentativas_login", 0) + 1
        if perfil["tentativas_login"] >= 5:
            perfil["bloqueado"] = True
            perfil["codigo_desbloqueio"] = str(random.randint(100000, 999999))
        salvar_dados(dados)
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos")
    perfil["tentativas_login"] = 0
    salvar_dados(dados)
    return _perfil_publico(perfil)


@app.get("/api/perfil")
def obter_perfil(email: str):
    return _perfil_publico(_get_perfil(email)[2])


class AtualizacaoPerfil(BaseModel):
    nome: Optional[str] = None
    nome_crianca: Optional[str] = None
    informacoes_crianca: Optional[dict] = None
    preferencias: Optional[dict] = None


@app.patch("/api/perfil")
def atualizar_perfil(payload: AtualizacaoPerfil, email: str = Query(...)):
    dados, chave, perfil = _get_perfil(email)
    if payload.nome is not None: perfil["nome"] = payload.nome.strip()
    if payload.nome_crianca is not None: perfil["nome_crianca"] = payload.nome_crianca.strip()
    if payload.informacoes_crianca is not None: perfil["informacoes_crianca"].update(payload.informacoes_crianca)
    if payload.preferencias is not None: perfil["preferencias"].update(payload.preferencias)
    salvar_dados(dados)
    return _perfil_publico(perfil)


@app.get("/api/tarefas")
def listar_tarefas(email: str, tipo: str = "tarefas_diarias"):
    return _get_perfil(email)[2].get(tipo, [])


class TarefaToggle(BaseModel):
    email: str
    tipo: str = "tarefas_diarias"
    indice: int


@app.patch("/api/tarefas/concluir")
def concluir_tarefa(payload: TarefaToggle):
    dados, chave, perfil = _get_perfil(payload.email)
    lista = perfil.get(payload.tipo, [])
    if not 0 <= payload.indice < len(lista): raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    item = lista[payload.indice]
    estava_concluida = bool(item.get("concluida", False))
    item["concluida"] = not estava_concluida
    pontos = int(item.get("pontos", 10) or 10)
    perfil["pontuacao"] = max(0, int(perfil.get("pontuacao", 0) or 0) + (pontos if item["concluida"] else -pontos))
    item["pontos"] = pontos
    salvar_dados(dados)
    return {**item, "pontuacao": perfil["pontuacao"], "pontos_ganhos": pontos if item["concluida"] else -pontos}


class NovaTarefa(BaseModel):
    email: str
    tipo: str = "tarefas_diarias"
    titulo: str
    horario: str = ""
    data: str = ""
    periodo: str = "manha"
    passos: list = []
    tempo_limite_min: int = 0


@app.post("/api/tarefas")
def criar_tarefa(payload: NovaTarefa):
    dados, chave, perfil = _get_perfil(payload.email)
    periodo = payload.periodo if payload.periodo in {"manha", "tarde", "noite"} else "manha"
    passos = [{"texto": str(item.get("texto", "")).strip(), "concluida": bool(item.get("concluida", False))} for item in payload.passos if isinstance(item, dict) and str(item.get("texto", "")).strip()]
    perfil.setdefault(payload.tipo, []).append({"titulo": payload.titulo, "horario": payload.horario, "data": payload.data, "periodo": periodo, "concluida": False, "passos": passos, "tempo_limite_min": payload.tempo_limite_min, "pontos": 10})
    salvar_dados(dados)
    return perfil[payload.tipo][-1]


class EditarTarefa(BaseModel):
    titulo: Optional[str] = None
    horario: Optional[str] = None
    data: Optional[str] = None
    periodo: Optional[str] = None
    passos: Optional[list] = None
    tempo_limite_min: Optional[int] = None


@app.patch("/api/tarefas/{indice}")
def editar_tarefa(indice: int, payload: EditarTarefa, email: str, tipo: str = "tarefas_diarias"):
    dados, chave, perfil = _get_perfil(email)
    lista = perfil.get(tipo, [])
    if not 0 <= indice < len(lista): raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    item = lista[indice]
    for campo, valor in payload.model_dump(exclude_none=True).items():
        if campo == "periodo" and valor not in {"manha", "tarde", "noite"}:
            raise HTTPException(status_code=422, detail="Período inválido")
        if campo == "passos":
            valor = [{"texto": str(step.get("texto", "")).strip(), "concluida": bool(step.get("concluida", False))} for step in valor if isinstance(step, dict) and str(step.get("texto", "")).strip()]
        item[campo] = valor
    salvar_dados(dados)
    return item


@app.get("/api/estudos")
def listar_estudos(email: str): return _get_perfil(email)[2].get("estudos", [])


class NovoEstudo(BaseModel):
    email: str
    materia: str
    objetivo: str = ""
    tempo_estimado: int
    prioridade: str = "media"


@app.post("/api/estudos")
def criar_estudo(payload: NovoEstudo):
    dados, chave, perfil = _get_perfil(payload.email)
    perfil.setdefault("estudos", []).append({"materia": payload.materia, "objetivo": payload.objetivo, "tempo_estimado": payload.tempo_estimado, "tempo_estudado": 0, "prioridade": payload.prioridade, "concluido": False})
    salvar_dados(dados)
    return perfil["estudos"][-1]


@app.get("/api/lembretes")
def listar_lembretes(email: str): return _get_perfil(email)[2].get("lembretes", [])


class NovoLembrete(BaseModel):
    email: str
    mensagem: str
    horario: str
    tipo_alerta: str = "visual"


@app.post("/api/lembretes")
def criar_lembrete(payload: NovoLembrete):
    dados, chave, perfil = _get_perfil(payload.email)
    perfil.setdefault("lembretes", []).append({"mensagem": payload.mensagem, "horario": payload.horario, "tipo_alerta": payload.tipo_alerta, "ativo": True})
    salvar_dados(dados)
    return perfil["lembretes"][-1]


class EditarLembrete(BaseModel):
    mensagem: Optional[str] = None
    horario: Optional[str] = None
    tipo_alerta: Optional[str] = None
    ativo: Optional[bool] = None


@app.patch("/api/lembretes/{indice}")
def editar_lembrete(indice: int, payload: EditarLembrete, email: str):
    dados, chave, perfil = _get_perfil(email)
    lista = perfil.get("lembretes", [])
    if not 0 <= indice < len(lista): raise HTTPException(status_code=404, detail="Lembrete não encontrado")
    lista[indice].update(payload.model_dump(exclude_none=True))
    salvar_dados(dados)
    return lista[indice]


@app.get("/api/historico")
def listar_historico(email: str): return _get_perfil(email)[2].get("historico", [])


# ---------- Rede de apoio e profissionais ----------
class Pessoa(BaseModel):
    nome: str
    funcao: str = ""
    telefone: str = ""
    email: str = ""
    observacoes: str = ""
    tipo: str = "apoio"


@app.get("/api/rede-apoio")
def get_rede_apoio(email: str):
    return _get_perfil(email)[2].get("rede_apoio", [])


@app.post("/api/rede-apoio")
def criar_pessoa(payload: Pessoa, email: str):
    dados, chave, perfil = _get_perfil(email)
    item = payload.model_dump(); item["id"] = f"p-{len(perfil.get('rede_apoio', []))+1}"
    perfil.setdefault("rede_apoio", []).append(item)
    salvar_dados(dados)
    return item


@app.delete("/api/rede-apoio/{indice}")
def excluir_pessoa(indice: int, email: str):
    dados, chave, perfil = _get_perfil(email)
    lista = perfil.get("rede_apoio", [])
    if not 0 <= indice < len(lista): raise HTTPException(status_code=404, detail="Contato não encontrado")
    removido = lista.pop(indice); salvar_dados(dados); return removido


class Interacao(BaseModel):
    pessoa: str
    texto: str
    tipo: str = "apoio"


@app.post("/api/interacoes")
def criar_interacao(payload: Interacao, email: str):
    dados, chave, perfil = _get_perfil(email)
    item = {**payload.model_dump(), "data": datetime.now().strftime("%d/%m/%Y"), "hora": datetime.now().strftime("%H:%M")}
    perfil.setdefault("interacoes", []).insert(0, item); salvar_dados(dados); return item


@app.get("/api/interacoes")
def listar_interacoes(email: str): return _get_perfil(email)[2].get("interacoes", [])


# ---------- Comunidade de apoio ----------
def _perfil_comunidade(email, perfil, email_viewer=None):
    publico = perfil.get("usuario_publico", {})
    comunidade = perfil.get("comunidade", {})
    seguindo = [item.lower() for item in comunidade.get("seguindo", [])]
    seguidores = [item.lower() for item in comunidade.get("seguidores", [])]
    return {
        "usuario": publico.get("usuario", ""),
        "nome_exibicao": publico.get("nome_exibicao") or perfil.get("nome", ""),
        "bio": publico.get("bio", ""),
        "visibilidade": publico.get("visibilidade", "publico"),
        "seguidores": len(seguidores),
        "seguindo": len(seguindo),
        "segue": bool(email_viewer and email_viewer.lower() in seguindo),
        "proprio": bool(email_viewer and email_viewer.lower() == email.lower()),
    }


def _publicacao_publica(email, perfil, publicacao, email_viewer):
    curtidas = [item.lower() for item in publicacao.get("curtidas_por", [])]
    return {
        "id": publicacao.get("id", ""),
        "texto": publicacao.get("texto", ""),
        "tema": publicacao.get("tema", "geral"),
        "criado_em": publicacao.get("criado_em", ""),
        "autor": _perfil_comunidade(email, perfil, email_viewer),
        "curtidas": len(curtidas),
        "curtido": email_viewer.lower() in curtidas,
    }


@app.get("/api/comunidade/usuarios")
def buscar_usuarios(email: str, q: str = ""):
    dados = carregar_dados()
    termo = (q or "").strip().lower()
    if len(termo) < 2:
        return []
    encontrados = []
    for chave, perfil in dados.items():
        _normalizar_perfil(perfil)
        if chave.lower() == email.lower() or perfil.get("usuario_publico", {}).get("visibilidade", "publico") != "publico":
            continue
        publico = perfil.get("usuario_publico", {})
        campos = (publico.get("usuario", ""), publico.get("nome_exibicao", ""), publico.get("bio", ""))
        if termo not in " ".join(campos).lower():
            continue
        encontrados.append(_perfil_comunidade(chave, perfil, email))
    return encontrados[:20]


@app.get("/api/comunidade/feed")
def obter_feed_comunidade(email: str):
    dados = carregar_dados()
    _, perfil_atual = _encontrar_por_email(dados, email)
    if perfil_atual is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    _normalizar_perfil(perfil_atual)
    seguindo = {item.lower() for item in perfil_atual.get("comunidade", {}).get("seguindo", [])}
    autores = {email.lower()} | seguindo
    itens = []
    for chave, perfil in dados.items():
        if chave.lower() not in autores:
            continue
        _normalizar_perfil(perfil)
        if perfil.get("usuario_publico", {}).get("visibilidade", "publico") != "publico":
            continue
        for publicacao in perfil.get("comunidade", {}).get("publicacoes", []):
            itens.append(_publicacao_publica(chave, perfil, publicacao, email))
    itens.sort(key=lambda item: item.get("criado_em", ""), reverse=True)
    return {"perfil": _perfil_comunidade(email, perfil_atual, email), "publicacoes": itens[:50]}


class AtualizacaoComunidade(BaseModel):
    nome_exibicao: Optional[str] = None
    usuario: Optional[str] = None
    bio: Optional[str] = Field(default=None, max_length=160)
    visibilidade: Optional[str] = None


@app.patch("/api/comunidade/perfil")
def atualizar_perfil_comunidade(payload: AtualizacaoComunidade, email: str = Query(...)):
    dados, _, perfil = _get_perfil(email)
    _normalizar_perfil(perfil)
    publico = perfil["usuario_publico"]
    if payload.nome_exibicao is not None:
        publico["nome_exibicao"] = payload.nome_exibicao.strip()[:80]
    if payload.bio is not None:
        publico["bio"] = payload.bio.strip()
    if payload.visibilidade is not None:
        if payload.visibilidade not in {"publico", "privado"}:
            raise HTTPException(status_code=422, detail="Visibilidade inválida")
        publico["visibilidade"] = payload.visibilidade
    if payload.usuario is not None:
        novo_usuario = payload.usuario.strip().lower().lstrip("@").replace(" ", "-")
        if len(novo_usuario) < 3 or not novo_usuario.replace("-", "").isalnum():
            raise HTTPException(status_code=422, detail="Usuário deve ter ao menos 3 caracteres e usar letras, números ou hífen")
        for chave, outro in dados.items():
            if chave.lower() != email.lower() and outro.get("usuario_publico", {}).get("usuario", "").lower() == novo_usuario:
                raise HTTPException(status_code=409, detail="Esse usuário já está em uso")
        publico["usuario"] = novo_usuario
    salvar_dados(dados)
    return _perfil_comunidade(email, perfil, email)


class SeguirUsuario(BaseModel):
    usuario: str = Field(min_length=3, max_length=40)


@app.post("/api/comunidade/seguir")
def alternar_seguir(payload: SeguirUsuario, email: str = Query(...)):
    dados, _, perfil_atual = _get_perfil(email)
    alvo_email, alvo = None, None
    for chave, perfil in dados.items():
        _normalizar_perfil(perfil)
        if perfil.get("usuario_publico", {}).get("usuario", "").lower() == payload.usuario.strip().lstrip("@").lower():
            alvo_email, alvo = chave, perfil
            break
    if alvo is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if alvo_email.lower() == email.lower():
        raise HTTPException(status_code=400, detail="Você não pode seguir o próprio perfil")
    seguindo = perfil_atual["comunidade"]["seguindo"]
    seguidores = alvo["comunidade"]["seguidores"]
    seguindo_lower = {item.lower() for item in seguindo}
    if alvo_email.lower() in seguindo_lower:
        perfil_atual["comunidade"]["seguindo"] = [item for item in seguindo if item.lower() != alvo_email.lower()]
        alvo["comunidade"]["seguidores"] = [item for item in seguidores if item.lower() != email.lower()]
        esta_seguindo = False
    else:
        seguindo.append(alvo_email)
        if email.lower() not in {item.lower() for item in seguidores}:
            seguidores.append(email)
        esta_seguindo = True
    salvar_dados(dados)
    return {"usuario": alvo["usuario_publico"].get("usuario", ""), "seguindo": esta_seguindo, "seguidores": len(alvo["comunidade"]["seguidores"])}


class Publicacao(BaseModel):
    texto: str = Field(min_length=1, max_length=500)
    tema: str = Field(default="geral", max_length=40)


@app.post("/api/comunidade/publicacoes")
def criar_publicacao(payload: Publicacao, email: str = Query(...)):
    dados, _, perfil = _get_perfil(email)
    _normalizar_perfil(perfil)
    publicacao = {
        "id": f"pub-{int(datetime.now().timestamp() * 1000)}",
        "texto": payload.texto.strip(),
        "tema": payload.tema.strip() or "geral",
        "criado_em": datetime.now().isoformat(timespec="seconds"),
        "curtidas_por": [],
    }
    perfil["comunidade"]["publicacoes"].insert(0, publicacao)
    salvar_dados(dados)
    return _publicacao_publica(email, perfil, publicacao, email)


@app.post("/api/comunidade/publicacoes/{publicacao_id}/curtir")
def alternar_curtida(publicacao_id: str, email: str = Query(...)):
    dados, _, _ = _get_perfil(email)
    for _, perfil in dados.items():
        _normalizar_perfil(perfil)
        for publicacao in perfil["comunidade"]["publicacoes"]:
            if publicacao.get("id") != publicacao_id:
                continue
            curtidas = publicacao.setdefault("curtidas_por", [])
            curtidas_lower = {item.lower() for item in curtidas}
            if email.lower() in curtidas_lower:
                publicacao["curtidas_por"] = [item for item in curtidas if item.lower() != email.lower()]
                curtido = False
            else:
                curtidas.append(email)
                curtido = True
            salvar_dados(dados)
            return {"curtido": curtido, "curtidas": len(publicacao["curtidas_por"])}
    raise HTTPException(status_code=404, detail="Publicação não encontrada")


# ---------- Conversas e grupos ----------
def _nome_publico(dados, email):
    perfil = dados.get(email)
    if perfil is None:
        return email.split("@", 1)[0]
    _normalizar_perfil(perfil)
    return perfil.get("usuario_publico", {}).get("nome_exibicao") or perfil.get("nome", "Pessoa")


def _resumo_conversa(conversa, dados, email):
    mensagens = conversa.get("mensagens", [])
    ultima = mensagens[-1] if mensagens else None
    participantes = [item for item in conversa.get("participantes", []) if item.lower() != email.lower()]
    nome = conversa.get("nome", "Conversa")
    if conversa.get("tipo") == "direta" and participantes:
        nome = _nome_publico(dados, participantes[0])
    return {"id": conversa.get("id"), "tipo": conversa.get("tipo", "direta"), "nome": nome, "tema": conversa.get("tema", ""), "participantes": len(conversa.get("participantes", [])), "ultima_mensagem": ultima.get("texto", "") if ultima else "Ainda não há mensagens.", "ultima_data": ultima.get("criado_em", "") if ultima else conversa.get("criado_em", "")}


@app.get("/api/comunidade/conversas")
def listar_conversas(email: str):
    dados = carregar_dados()
    if _encontrar_por_email(dados, email)[1] is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    comunidade = carregar_comunidade()
    conversas = [item for item in comunidade["conversas"].values() if email.lower() in {p.lower() for p in item.get("participantes", [])}]
    grupos = [item for item in comunidade["grupos"].values() if email.lower() in {p.lower() for p in item.get("participantes", [])}]
    resultado = [_resumo_conversa(item, dados, email) for item in conversas]
    resultado += [_resumo_conversa({**item, "tipo": "grupo", "id": item["id"], "nome": item.get("nome", "Grupo")}, dados, email) for item in grupos]
    resultado.sort(key=lambda item: item.get("ultima_data", ""), reverse=True)
    return resultado


@app.get("/api/comunidade/grupos")
def listar_grupos(email: str):
    dados = carregar_dados()
    if _encontrar_por_email(dados, email)[1] is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    comunidade = carregar_comunidade()
    resultado = []
    for grupo in comunidade["grupos"].values():
        participantes = grupo.get("participantes", [])
        resultado.append({"id": grupo.get("id"), "nome": grupo.get("nome"), "tema": grupo.get("tema", "apoio"), "descricao": grupo.get("descricao", ""), "membros": len(participantes), "participa": email.lower() in {p.lower() for p in participantes}})
    return resultado


class NovoGrupo(BaseModel):
    nome: str = Field(min_length=3, max_length=80)
    tema: str = Field(default="apoio", max_length=40)
    descricao: str = Field(default="", max_length=240)


@app.post("/api/comunidade/grupos")
def criar_grupo(payload: NovoGrupo, email: str = Query(...)):
    dados, _, _ = _get_perfil(email)
    comunidade = carregar_comunidade()
    grupo_id = f"grupo-{int(datetime.now().timestamp() * 1000)}"
    comunidade["grupos"][grupo_id] = {"id": grupo_id, "nome": payload.nome.strip(), "tema": payload.tema.strip() or "apoio", "descricao": payload.descricao.strip(), "criador": email, "participantes": [email], "mensagens": [], "criado_em": datetime.now().isoformat(timespec="seconds")}
    salvar_comunidade(comunidade)
    return {"id": grupo_id, "nome": payload.nome.strip(), "tema": payload.tema.strip() or "apoio", "descricao": payload.descricao.strip(), "membros": 1, "participa": True}


class ParticipacaoGrupo(BaseModel):
    grupo_id: str = Field(min_length=3, max_length=80)


@app.post("/api/comunidade/grupos/{grupo_id}/participar")
def participar_grupo(grupo_id: str, email: str = Query(...)):
    dados, _, _ = _get_perfil(email)
    comunidade = carregar_comunidade()
    grupo = comunidade["grupos"].get(grupo_id)
    if grupo is None:
        raise HTTPException(status_code=404, detail="Grupo não encontrado")
    membros = grupo.setdefault("participantes", [])
    membros_lower = {item.lower() for item in membros}
    if email.lower() in membros_lower:
        grupo["participantes"] = [item for item in membros if item.lower() != email.lower()]
        participa = False
    else:
        membros.append(email)
        participa = True
    salvar_comunidade(comunidade)
    return {"participa": participa, "membros": len(grupo["participantes"])}


class NovaConversa(BaseModel):
    usuario: str = Field(min_length=3, max_length=40)


@app.post("/api/comunidade/conversas")
def criar_conversa(payload: NovaConversa, email: str = Query(...)):
    dados, _, _ = _get_perfil(email)
    alvo = next(((chave, perfil) for chave, perfil in dados.items() if perfil.get("usuario_publico", {}).get("usuario", "").lower() == payload.usuario.strip().lstrip("@").lower()), None)
    if alvo is None or alvo[0].lower() == email.lower():
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    participantes = sorted([email, alvo[0]], key=str.lower)
    conversa_id = "dm-" + hashlib.sha256("|".join(participantes).encode()).hexdigest()[:12]
    comunidade = carregar_comunidade()
    comunidade["conversas"].setdefault(conversa_id, {"id": conversa_id, "tipo": "direta", "participantes": participantes, "mensagens": [], "criado_em": datetime.now().isoformat(timespec="seconds")})
    salvar_comunidade(comunidade)
    return _resumo_conversa(comunidade["conversas"][conversa_id], dados, email)


@app.get("/api/comunidade/conversas/{conversa_id}/mensagens")
def listar_mensagens(conversa_id: str, email: str):
    dados = carregar_dados()
    comunidade = carregar_comunidade()
    conversa = comunidade["conversas"].get(conversa_id)
    if conversa is None:
        conversa = comunidade["grupos"].get(conversa_id)
    if conversa is None:
        grupo_id = conversa_id.removeprefix("grupo-")
        conversa = comunidade["grupos"].get(grupo_id)
    if conversa is None or email.lower() not in {p.lower() for p in conversa.get("participantes", [])}:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    return [{"id": item.get("id"), "texto": item.get("texto", ""), "criado_em": item.get("criado_em", ""), "autor": _nome_publico(dados, item.get("email", "")), "propria": item.get("email", "").lower() == email.lower()} for item in conversa.get("mensagens", [])]


class NovaMensagem(BaseModel):
    texto: str = Field(min_length=1, max_length=1000)


@app.post("/api/comunidade/conversas/{conversa_id}/mensagens")
def criar_mensagem(conversa_id: str, payload: NovaMensagem, email: str = Query(...)):
    dados, _, _ = _get_perfil(email)
    comunidade = carregar_comunidade()
    conversa = comunidade["conversas"].get(conversa_id)
    if conversa is None:
        conversa = comunidade["grupos"].get(conversa_id)
    if conversa is None:
        grupo_id = conversa_id.removeprefix("grupo-")
        conversa = comunidade["grupos"].get(grupo_id)
    if conversa is None or email.lower() not in {p.lower() for p in conversa.get("participantes", [])}:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    mensagem = {"id": f"msg-{int(datetime.now().timestamp() * 1000)}", "email": email, "texto": payload.texto.strip(), "criado_em": datetime.now().isoformat(timespec="seconds")}
    conversa.setdefault("mensagens", []).append(mensagem)
    salvar_comunidade(comunidade)
    return {"id": mensagem["id"], "texto": mensagem["texto"], "criado_em": mensagem["criado_em"], "autor": _nome_publico(dados, email), "propria": True}


# ---------- Biblioteca ----------
@app.get("/api/biblioteca")
def get_biblioteca(q: str = "", tipo: str = ""):
    return listar_biblioteca(q, tipo)


# ---------- IA ----------
class PerguntaIA(BaseModel):
    email: str
    pergunta: str


@app.post("/api/assistente")
def perguntar_ia(payload: PerguntaIA):
    perfil = _get_perfil(payload.email)[2]
    resposta = obter_resposta_ia(payload.pergunta, perfil.get("preferencias", {}).get("estilo_instrucao", "direto"))
    return {"resposta": resposta, "modo": "online" if isinstance(resposta, list) and resposta and not resposta[0].startswith("Modo offline") else "offline"}


class TituloTarefa(BaseModel): titulo: str


@app.post("/api/tarefas/passos")
def passos_tarefa(payload: TituloTarefa): return {"passos": gerar_passos_tarefa(payload.titulo)}
