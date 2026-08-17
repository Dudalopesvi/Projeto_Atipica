import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(dotenv_path=None):
        return False

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

try:
    from google import genai
    from google.genai import types as genai_types
    _API_KEY = os.environ.get("GEMINI_API_KEY")
    _client = genai.Client(api_key=_API_KEY) if _API_KEY else None
except Exception:
    _client = None

_MODELO = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")


def _instrucao_base(estilo):
    detalhe = "Seja breve, organizado em etapas e use frases curtas." if estilo == "direto" else "Explique em etapas numeradas, com exemplos simples."
    return ("Você é o Assistente Atípica, voltado a apoiar famílias de pessoas autistas. "
            "Não diagnostique, não prescreva e não substitua profissionais. "
            "Use linguagem respeitosa, concreta, sem infantilizar e sem generalizar o autismo. " + detalhe)


def _offline(pergunta, estilo):
    pergunta = (pergunta or "").lower()
    if any(palavra in pergunta for palavra in ("crise", "sobrecarga", "meltdown")):
        return ["Reduza ruídos e pessoas ao redor.", "Use frases curtas e ofereça uma pausa segura.", "Não force contato físico.", "Se houver risco, procure ajuda profissional ou serviço de emergência."]
    if any(palavra in pergunta for palavra in ("rotina", "transição", "mudança")):
        return ["Avise a mudança com antecedência.", "Mostre o próximo passo em imagem ou frase curta.", "Ofereça uma escolha entre duas opções.", "Reforce o que funcionou sem punição."]
    return ["Identifique uma única situação para organizar.", "Divida a atividade em passos pequenos.", "Use linguagem direta e uma rotina visual.", "Observe o que ajuda e registre para conversar com a equipe."]


def _gerar_online(prompt, system, temperatura):
    if not _client:
        return None
    resposta = _client.models.generate_content(model=_MODELO, contents=prompt, config=genai_types.GenerateContentConfig(system_instruction=system, temperature=temperatura))
    texto = getattr(resposta, "text", "") or ""
    linhas = [linha.strip(" -*\t") for linha in texto.splitlines() if linha.strip()]
    return linhas or None


def obter_resposta_ia(pergunta, estilo_usuario="direto"):
    try:
        online = _gerar_online(pergunta, _instrucao_base(estilo_usuario), 0.25)
        if online:
            return online
    except Exception:
        pass
    return ["Modo offline: a IA online não está configurada. Estas são orientações gerais:"] + _offline(pergunta, estilo_usuario)


def gerar_passos_tarefa(titulo_tarefa):
    prompt = f"Divida a tarefa '{titulo_tarefa}' em exatamente 3 ou 4 passos curtos, um por linha. Não escreva introdução."
    try:
        online = _gerar_online(prompt, "Crie checklists acessíveis para pessoas autistas. Use verbos de ação, frases concretas e sem diagnóstico.", 0.2)
        if online:
            return online[:4]
    except Exception:
        pass
    return ["Prepare os materiais necessários.", "Faça o primeiro passo por alguns minutos.", "Faça uma pausa breve.", "Finalize e marque a atividade como concluída."]


def usar_gemini():
    return _client is not None
