import os

# ── Tenta usar Gemini real; cai no simulado se não houver chave ──────────────
try:
    from google import genai
    from google.genai import types as genai_types
    _API_KEY = os.environ.get("GEMINI_API_KEY")
    _client  = genai.Client(api_key=_API_KEY) if _API_KEY else None
except ImportError:
    _client = None

_MODELO = "gemini-2.5-flash"


# ── Prompt base adaptado para TEA/TPAC ───────────────────────────────────────

def _instrucao_base(estilo: str) -> str:
    base = (
        "Você é um assistente especializado em acessibilidade para pessoas com TEA "
        "(Transtorno do Espectro Autista) e TPAC.\n"
        "Seu papel é reduzir a carga cognitiva, cansaço mental e ambiguidade.\n"
        "Regras obrigatórias:\n"
        "- Nunca use parágrafos longos ou jargões complexos.\n"
        "- Use frases curtas com ordem direta: Sujeito + Verbo + Objeto.\n"
        "- Divida respostas em tópicos curtos e visuais.\n"
        "- Nunca use linguagem ambígua, ironia ou metáforas abstratas.\n"
    )
    if estilo == "direto":
        base += "- Seja extremamente conciso. Mínimo de palavras possível."
    else:
        base += "- Explique em etapas lógicas e sequenciais simples."
    return base


# ── Respostas simuladas (fallback sem API) ────────────────────────────────────

def _resposta_simulada(estilo: str) -> list:
    if estilo == "direto":
        return [
            "Ação 1: Foque no comando central.",
            "Ação 2: Retire distrações do ambiente.",
            "Ação 3: Pause 5 minutos ao terminar."
        ]
    return [
        "Passo 1: Identifique a tarefa principal.",
        "Passo 2: Organize seu espaço de trabalho.",
        "Passo 3: Execute em blocos de 15 minutos.",
        "Dica: Descanse 5 minutos entre cada bloco."
    ]


def _passos_simulados() -> list:
    return [
        "Organize o espaço retirando distrações visuais.",
        "Execute a primeira parte por 15 minutos.",
        "Faça uma pausa de 5 minutos em silêncio.",
        "Retome e finalize a tarefa."
    ]


# ── Funções públicas ──────────────────────────────────────────────────────────

def obter_resposta_ia(pergunta: str, estilo_usuario: str) -> list:
    """
    RF07 / RF09 — Responde à pergunta adaptando linguagem ao perfil do usuário.
    Usa Gemini se GEMINI_API_KEY estiver configurada, senão usa modo simulado.
    """
    if not _client:
        return _resposta_simulada(estilo_usuario)

    try:
        resposta = _client.models.generate_content(
            model=_MODELO,
            contents=pergunta,
            config=genai_types.GenerateContentConfig(
                system_instruction=_instrucao_base(estilo_usuario),
                temperature=0.3,
            ),
        )
        linhas = [l.strip() for l in resposta.text.split("\n") if l.strip()]
        return linhas if linhas else _resposta_simulada(estilo_usuario)
    except Exception as e:
        return [f"Erro ao conectar com a IA: {str(e)}", "Usando modo offline."] + _resposta_simulada(estilo_usuario)


def gerar_passos_tarefa(titulo_tarefa: str) -> list:
    """
    RF07 RN01 — Quebra uma tarefa em 3–4 micro-ações sequenciais.
    Usa Gemini se disponível, senão usa modo simulado.
    """
    if not _client:
        return _passos_simulados()

    prompt = (
        f"Quebre esta tarefa em exatamente 3 ou 4 passos sequenciais, "
        f"curtos e fáceis de executar: '{titulo_tarefa}'. "
        f"Escreva apenas os passos, um por linha, sem introduções ou numeração."
    )
    system = (
        "Você é especialista em produtividade para pessoas com TEA. "
        "Crie checklists limpos com verbos de ação claros e sem texto desnecessário."
    )
    try:
        resposta = _client.models.generate_content(
            model=_MODELO,
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                system_instruction=system,
                temperature=0.2,
            ),
        )
        passos = [l.strip() for l in resposta.text.split("\n") if l.strip()]
        # Remove marcadores automáticos que o modelo possa gerar
        passos_limpos = [p.lstrip("0123456789.-* ") for p in passos if p]
        return passos_limpos if passos_limpos else _passos_simulados()
    except Exception as e:
        return [f"Erro ao gerar passos: {str(e)}"] + _passos_simulados()


def usar_gemini() -> bool:
    """Informa se a integração real com Gemini está ativa."""
    return _client is not None
