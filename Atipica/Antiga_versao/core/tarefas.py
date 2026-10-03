from datetime import datetime
from data.data_manager import salvar_dados


def _agora():
    return datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%H:%M")


# ── Tarefas ───────────────────────────────────────────────────────────────────

def adicionar_tarefa(dados, usuario, chave, titulo, horario="", data=""):
    if horario and data:
        for t in dados[usuario][chave]:
            if t.get("horario") == horario and t.get("data") == data and not t.get("concluida", False):
                return False
    dados[usuario][chave].append({
        "titulo": titulo, "horario": horario, "data": data,
        "concluida": False, "passos": [], "tempo_limite_min": 0
    })
    salvar_dados(dados)
    return True


def atualizar_tarefa(dados, usuario, chave, idx, titulo=None, horario=None, data=None):
    tarefas = dados[usuario][chave]
    if not 0 <= idx < len(tarefas):
        return False
    tarefa = tarefas[idx]
    novo_titulo = tarefa.get("titulo", "") if titulo is None else titulo
    novo_horario = tarefa.get("horario", "") if horario is None else horario
    nova_data = tarefa.get("data", "") if data is None else data
    if not novo_titulo.strip():
        return False
    if novo_horario and nova_data:
        for i, outra in enumerate(tarefas):
            if i != idx and outra.get("horario") == novo_horario and outra.get("data") == nova_data and not outra.get("concluida", False):
                return False
    tarefa.update({"titulo": novo_titulo.strip(), "horario": novo_horario, "data": nova_data})
    salvar_dados(dados)
    return True


def definir_tempo_limite(dados, usuario, chave, idx, minutos):
    tarefas = dados[usuario][chave]
    if 0 <= idx < len(tarefas) and minutos >= 0:
        tarefas[idx]["tempo_limite_min"] = minutos
        salvar_dados(dados)
        return True
    return False


def alternar_status_tarefa(dados, usuario, chave, idx):
    tarefas = dados[usuario][chave]
    if 0 <= idx < len(tarefas):
        tarefa = tarefas[idx]
        tarefa["concluida"] = not tarefa.get("concluida", False)
        concluida_agora = tarefa["concluida"]
        if concluida_agora:
            data, hora = _agora()
            dados[usuario].setdefault("historico", []).append({
                "atividade": tarefa["titulo"], "categoria": chave,
                "data": data, "hora": hora, "status": "concluida"
            })
            dados[usuario]["pontuacao"] = dados[usuario].get("pontuacao", 0) + 10
        salvar_dados(dados)
        return concluida_agora
    return False


def excluir_tarefa(dados, usuario, chave, idx):
    tarefas = dados[usuario][chave]
    if 0 <= idx < len(tarefas):
        tarefas.pop(idx)
        salvar_dados(dados)
        return True
    return False


def alternar_passo(dados, usuario, chave, idx_tarefa, idx_passo):
    tarefas = dados[usuario][chave]
    if 0 <= idx_tarefa < len(tarefas):
        passos = tarefas[idx_tarefa].get("passos", [])
        if 0 <= idx_passo < len(passos):
            passos[idx_passo]["concluido"] = not passos[idx_passo].get("concluido", False)
            salvar_dados(dados)
            return True
    return False


def injetar_passos_ia(dados, usuario, chave, idx, passos):
    tarefas = dados[usuario][chave]
    if 0 <= idx < len(tarefas):
        tarefas[idx]["passos"] = [{"texto": p, "concluido": False} for p in passos]
        salvar_dados(dados)
        return True
    return False


# ── Estudos ───────────────────────────────────────────────────────────────────

def adicionar_estudo(dados, usuario, materia, objetivo, tempo_estimado, prioridade):
    if not materia or tempo_estimado <= 0:
        return False
    dados[usuario].setdefault("estudos", []).append({
        "materia": materia, "objetivo": objetivo, "tempo_estimado": tempo_estimado,
        "tempo_estudado": 0, "prioridade": prioridade, "concluido": False
    })
    salvar_dados(dados)
    return True


def registrar_progresso_estudo(dados, usuario, idx, minutos):
    estudos = dados[usuario].setdefault("estudos", [])
    if 0 <= idx < len(estudos) and minutos > 0:
        estudo = estudos[idx]
        estudo["tempo_estudado"] += minutos
        if estudo["tempo_estudado"] >= estudo["tempo_estimado"] and not estudo.get("concluido"):
            estudo["concluido"] = True
            data, hora = _agora()
            dados[usuario].setdefault("historico", []).append({"atividade": f"Estudo: {estudo['materia']}", "categoria": "estudos", "data": data, "hora": hora, "status": "concluido"})
            dados[usuario]["pontuacao"] = dados[usuario].get("pontuacao", 0) + 15
        salvar_dados(dados)
        return True
    return False


# ── Lembretes ─────────────────────────────────────────────────────────────────

def adicionar_lembrete(dados, usuario, mensagem, horario, tipo_alerta):
    if not tipo_alerta:
        tipo_alerta = dados[usuario].setdefault("preferencias", {}).get("tipo_alerta", "visual")
    dados[usuario].setdefault("lembretes", []).append({"mensagem": mensagem, "horario": horario, "tipo_alerta": tipo_alerta, "ativo": True})
    salvar_dados(dados)
    return True


def atualizar_lembrete(dados, usuario, idx, mensagem=None, horario=None, tipo_alerta=None):
    lembretes = dados[usuario].setdefault("lembretes", [])
    if not 0 <= idx < len(lembretes):
        return False
    lem = lembretes[idx]
    if mensagem is not None and mensagem.strip():
        lem["mensagem"] = mensagem.strip()
    if horario is not None and horario.strip():
        lem["horario"] = horario.strip()
    if tipo_alerta:
        lem["tipo_alerta"] = tipo_alerta
    salvar_dados(dados)
    return True


def alternar_lembrete(dados, usuario, idx):
    lembretes = dados[usuario].setdefault("lembretes", [])
    if 0 <= idx < len(lembretes):
        lembretes[idx]["ativo"] = not lembretes[idx].get("ativo", True)
        salvar_dados(dados)
        return lembretes[idx]["ativo"]
    return None


def desativar_lembrete(dados, usuario, idx):
    lembretes = dados[usuario].setdefault("lembretes", [])
    if 0 <= idx < len(lembretes):
        lembretes[idx]["ativo"] = False
        salvar_dados(dados)
        return True
    return False
