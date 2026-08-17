import hashlib
import os
import random
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from data.data_manager import carregar_dados, salvar_dados, perfil_padrao, listar_biblioteca
from core.ia_service import obter_resposta_ia, gerar_passos_tarefa

app = FastAPI(title="Atípica API", version="2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")],
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
    nome_crianca: str = Field(min_length=1)
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
    lista[payload.indice]["concluida"] = not lista[payload.indice].get("concluida", False)
    salvar_dados(dados)
    return lista[payload.indice]


class NovaTarefa(BaseModel):
    email: str
    tipo: str = "tarefas_diarias"
    titulo: str
    horario: str = ""
    data: str = ""
    tempo_limite_min: int = 0


@app.post("/api/tarefas")
def criar_tarefa(payload: NovaTarefa):
    dados, chave, perfil = _get_perfil(payload.email)
    perfil.setdefault(payload.tipo, []).append({"titulo": payload.titulo, "horario": payload.horario, "data": payload.data, "concluida": False, "passos": [], "tempo_limite_min": payload.tempo_limite_min})
    salvar_dados(dados)
    return perfil[payload.tipo][-1]


class EditarTarefa(BaseModel):
    titulo: Optional[str] = None
    horario: Optional[str] = None
    data: Optional[str] = None
    tempo_limite_min: Optional[int] = None


@app.patch("/api/tarefas/{indice}")
def editar_tarefa(indice: int, payload: EditarTarefa, email: str, tipo: str = "tarefas_diarias"):
    dados, chave, perfil = _get_perfil(email)
    lista = perfil.get(tipo, [])
    if not 0 <= indice < len(lista): raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    item = lista[indice]
    for campo, valor in payload.model_dump(exclude_none=True).items(): item[campo] = valor
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
