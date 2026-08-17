from datetime import datetime
from data.data_manager import salvar_dados


# ── Tarefas (diárias e educacionais) ────────────────────────────────────────

def adicionar_tarefa(dados: dict, usuario: str, chave: str, titulo: str,
                     horario: str = "", data: str = "") -> bool:
    """
    Cria uma tarefa. Valida conflito de horário (RF04 RN02).
    Retorna False se houver conflito, True se criada com sucesso.
    """
    if horario and data:
        for t in dados[usuario][chave]:
            if t.get("horario") == horario and t.get("data") == data and not t["concluida"]:
                return False  # conflito de horário

    dados[usuario][chave].append({
        "titulo": titulo,
        "horario": horario,
        "data": data,
        "concluida": False,
        "passos": [],
        "tempo_limite_min": 0   # 0 = sem limite; RF04 RN05
    })
    salvar_dados(dados)
    return True


def definir_tempo_limite(dados: dict, usuario: str, chave: str,
                         idx: int, minutos: int):
    """RF04 RN05 / RF07 RN03 — define tempo máximo para conclusão."""
    tarefas = dados[usuario][chave]
    if 0 <= idx < len(tarefas):
        tarefas[idx]["tempo_limite_min"] = minutos
        salvar_dados(dados)


def alternar_status_tarefa(dados: dict, usuario: str, chave: str,
                           idx: int) -> bool:
    """
    Alterna concluída/pendente.
    Se marcar como concluída: registra no histórico e soma pontos (RF04 RN04).
    Retorna True se concluída agora, False caso contrário.
    """
    tarefas = dados[usuario][chave]
    if 0 <= idx < len(tarefas):
        tarefas[idx]["concluida"] = not tarefas[idx]["concluida"]
        concluida_agora = tarefas[idx]["concluida"]

        if concluida_agora:
            # RF08 — registrar no histórico
            dados[usuario]["historico"].append({
                "atividade": tarefas[idx]["titulo"],
                "categoria": chave,
                "data": datetime.now().strftime("%Y-%m-%d"),
                "hora": datetime.now().strftime("%H:%M"),
                "status": "concluida"
            })
            # RF04 RN04 — pontuar
            dados[usuario]["pontuacao"] = dados[usuario].get("pontuacao", 0) + 10

        salvar_dados(dados)
        return concluida_agora
    return False


def excluir_tarefa(dados: dict, usuario: str, chave: str, idx: int):
    """RF04 RN03 — exclusão de tarefa."""
    tarefas = dados[usuario][chave]
    if 0 <= idx < len(tarefas):
        tarefas.pop(idx)
        salvar_dados(dados)


def alternar_passo(dados: dict, usuario: str, chave: str,
                   idx_tarefa: int, idx_passo: int):
    """RF07 RN02 — marcar/desmarcar passo individual do checklist."""
    tarefas = dados[usuario][chave]
    if 0 <= idx_tarefa < len(tarefas):
        passos = tarefas[idx_tarefa].get("passos", [])
        if 0 <= idx_passo < len(passos):
            passos[idx_passo]["concluido"] = not passos[idx_passo]["concluido"]
            salvar_dados(dados)


def injetar_passos_ia(dados: dict, usuario: str, chave: str,
                      idx: int, passos: list):
    """RF07 RN01 — divide tarefa em etapas."""
    tarefas = dados[usuario][chave]
    if 0 <= idx < len(tarefas):
        tarefas[idx]["passos"] = [{"texto": p, "concluido": False} for p in passos]
        salvar_dados(dados)


# ── Estudos ──────────────────────────────────────────────────────────────────

def adicionar_estudo(dados: dict, usuario: str, materia: str,
                     objetivo: str, tempo_estimado: int, prioridade: str):
    """RF05 — cria entrada de estudo com matéria, objetivo e tempo."""
    if not materia or tempo_estimado <= 0:
        return False  # RF05 RN01 e RN02
    dados[usuario]["estudos"].append({
        "materia": materia,
        "objetivo": objetivo,
        "tempo_estimado": tempo_estimado,   # minutos
        "tempo_estudado": 0,
        "prioridade": prioridade,           # "alta" | "media" | "baixa"
        "concluido": False
    })
    salvar_dados(dados)
    return True


def registrar_progresso_estudo(dados: dict, usuario: str,
                                idx: int, minutos: int):
    """RF05 RN03 — acumula tempo estudado e marca como concluído se atingir meta."""
    estudos = dados[usuario]["estudos"]
    if 0 <= idx < len(estudos):
        estudos[idx]["tempo_estudado"] += minutos
        if estudos[idx]["tempo_estudado"] >= estudos[idx]["tempo_estimado"]:
            estudos[idx]["concluido"] = True
            dados[usuario]["historico"].append({
                "atividade": f"Estudo: {estudos[idx]['materia']}",
                "categoria": "estudos",
                "data": datetime.now().strftime("%Y-%m-%d"),
                "hora": datetime.now().strftime("%H:%M"),
                "status": "concluido"
            })
            dados[usuario]["pontuacao"] = dados[usuario].get("pontuacao", 0) + 15
        salvar_dados(dados)


# ── Lembretes ────────────────────────────────────────────────────────────────

def adicionar_lembrete(dados: dict, usuario: str, mensagem: str,
                       horario: str, tipo_alerta: str):
    """RF06 — cria lembrete respeitando preferência do usuário."""
    # RF06 RN01 — respeita preferência do perfil se não informado
    if not tipo_alerta:
        tipo_alerta = dados[usuario]["preferencias"].get("tipo_alerta", "visual")

    dados[usuario]["lembretes"].append({
        "mensagem": mensagem,
        "horario": horario,
        "tipo_alerta": tipo_alerta,
        "ativo": True
    })
    salvar_dados(dados)


def desativar_lembrete(dados: dict, usuario: str, idx: int):
    """RF06 RN03 — desativa lembrete."""
    lembretes = dados[usuario]["lembretes"]
    if 0 <= idx < len(lembretes):
        lembretes[idx]["ativo"] = False
        salvar_dados(dados)
