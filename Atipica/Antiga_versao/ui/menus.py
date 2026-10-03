import random
import hashlib
from datetime import datetime

from ui.utils import (exibir_cabecalho, exibir_alerta, temporizador,
                      input_obrigatorio, confirmar)
from data.data_manager import carregar_dados, salvar_dados, perfil_padrao
import core.tarefas as core_tarefas
import core.ia_service as ia_service


# ── Helpers internos ─────────────────────────────────────────────────────────

def _hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()


def _encontrar_usuario_por_email(dados: dict, email: str):
    """Retorna (chave_dict, perfil) ou (None, None)."""
    for chave, perfil in dados.items():
        if perfil.get("email", "").lower() == email.lower():
            return chave, perfil
    return None, None


def _gerar_codigo_desbloqueio() -> str:
    return str(random.randint(100000, 999999))


def _verificar_lembretes_pendentes(dados: dict, usuario: str):
    """RF06 RN02 — exibe lembretes ativos cujo horário já passou hoje."""
    agora = datetime.now().strftime("%H:%M")
    lembretes = dados[usuario].get("lembretes", [])
    for lem in lembretes:
        if lem.get("ativo") and lem.get("horario", "") <= agora:
            tipo = dados[usuario]["preferencias"].get("tipo_alerta", "visual")
            exibir_alerta(lem["mensagem"], tipo)


# ── RF01 — Cadastro ──────────────────────────────────────────────────────────

def criar_usuario_menu(dados: dict):
    exibir_cabecalho("CRIAR NOVO PERFIL")

    # RF01 RN03 — campos obrigatórios
    nome  = input_obrigatorio("Nome do responsável: ")
    nome_crianca = input_obrigatorio("Nome da criança: ")
    email = input_obrigatorio("E-mail: ")

    # RF01 RN01 — e-mail único
    _, existente = _encontrar_usuario_por_email(dados, email)
    if existente:
        input("\n  ⚠  E-mail já cadastrado. Pressione Enter.")
        return

    # RF01 RN02 — senha mínimo 6 caracteres
    while True:
        senha = input("Senha (mín. 6 caracteres): ").strip()
        if len(senha) >= 6:
            break
        print("  ⚠  A senha precisa ter pelo menos 6 caracteres.")

    # Preferências de comunicação
    print("\n--- Estilo de Instrução ---")
    print("1. Direto — curto e objetivo (recomendado para TEA)")
    print("2. Detalhado — passo a passo explicativo")
    estilo = "direto" if input("Opção: ").strip() == "1" else "detalhado"

    # RF09 — preferências sensoriais
    print("\n--- Preferências Sensoriais ---")
    print("1. Visual  2. Sonoro  3. Ambos")
    op = input("Opção: ").strip()
    sens = {"1": "visual", "2": "sonoro", "3": "ambos"}.get(op, "visual")

    print("\n--- Tipo de Alerta para Lembretes ---")
    print("1. Visual  2. Sonoro  3. Ambos")
    op2 = input("Opção: ").strip()
    alerta = {"1": "visual", "2": "sonoro", "3": "ambos"}.get(op2, "visual")

    # Usa e-mail como chave interna (garante unicidade)
    chave = email.lower()
    dados[chave] = perfil_padrao(nome, email, _hash_senha(senha), estilo, sens, alerta)
    dados[chave]["nome_crianca"] = nome_crianca
    salvar_dados(dados)
    input(f"\n  ✅ Perfil de [{nome}] criado! Pressione Enter.")


# ── RF02 — Login ─────────────────────────────────────────────────────────────

def login_menu(dados: dict):
    """
    Retorna a chave do usuário autenticado ou None.
    RF02 RN01-RN04.
    """
    exibir_cabecalho("LOGIN")
    email = input("E-mail: ").strip()
    chave, perfil = _encontrar_usuario_por_email(dados, email)

    if not perfil:
        input("\n  ⚠  E-mail não encontrado. Pressione Enter.")
        return None

    # RF02 RN02 — bloqueio após 5 tentativas
    if perfil.get("bloqueado"):
        print("\n  🔒 Conta bloqueada após múltiplas tentativas incorretas.")
        if confirmar("  Deseja desbloquear via código de celular?"):
            _fluxo_desbloqueio(dados, chave, perfil)
        return None

    senha = input("Senha: ").strip()
    if _hash_senha(senha) == perfil["senha"]:
        perfil["tentativas_login"] = 0
        salvar_dados(dados)
        return chave
    else:
        perfil["tentativas_login"] = perfil.get("tentativas_login", 0) + 1
        # RF02 RN03 — mensagem de erro
        print(f"\n  ⚠  Senha incorreta. "
              f"Tentativa {perfil['tentativas_login']} de 5.")
        if perfil["tentativas_login"] >= 5:
            # RF02 RN02 — bloquear
            perfil["bloqueado"] = True
            codigo = _gerar_codigo_desbloqueio()
            perfil["codigo_desbloqueio"] = codigo
            print(f"\n  🔒 Conta bloqueada!")
            # RF02 RN04 — simulação de envio do código ao "celular"
            print(f"  📱 Código de desbloqueio enviado ao celular: {codigo}")
        salvar_dados(dados)
        input("  Pressione Enter.")
        return None


def _fluxo_desbloqueio(dados: dict, chave: str, perfil: dict):
    """RF02 RN04 — desbloqueio via código."""
    codigo = input("  Digite o código recebido no celular: ").strip()
    if codigo == str(perfil.get("codigo_desbloqueio")):
        perfil["bloqueado"] = False
        perfil["tentativas_login"] = 0
        perfil["codigo_desbloqueio"] = None
        salvar_dados(dados)
        print("  ✅ Conta desbloqueada! Faça login novamente.")
    else:
        print("  ⚠  Código incorreto.")
    input("  Pressione Enter.")


# ── RF03 — Perfil ─────────────────────────────────────────────────────────────

def editar_perfil_menu(dados: dict, usuario: str):
    """RF03 — edição de preferências cognitivas e sensoriais."""
    while True:
        exibir_cabecalho("MEU PERFIL")
        p = dados[usuario]["preferencias"]
        print(f"  Responsável   : {dados[usuario]['nome']}")
        print(f"  Criança       : {dados[usuario].get('nome_crianca') or '[não informado]'}")
        print(f"  E-mail        : {dados[usuario]['email']}")
        print(f"  Estilo        : {p['estilo_instrucao']}")
        print(f"  Sensorial     : {p['preferencias_sensoriais']}")
        print(f"  Tipo alerta   : {p['tipo_alerta']}")
        print(f"  Lembretes     : {'Ativados' if p['lembretes_ativos'] else 'Desativados'}")
        print(f"  Pontuação     : {dados[usuario].get('pontuacao', 0)} pts\n")
        print("1. Alterar nome da criança")
        print("2. Alterar estilo de instrução")
        print("3. Alterar preferências sensoriais")
        print("4. Alterar tipo de alerta")
        print("5. Ativar/Desativar lembretes")
        print("6. Alterar senha")
        print("7. Voltar")

        op = input("\nOpção: ").strip()

        if op == "1":
            novo_nome = input_obrigatorio("  Novo nome da criança: ")
            dados[usuario]["nome_crianca"] = novo_nome
        elif op == "2":
            print("1. Direto  2. Detalhado")
            p["estilo_instrucao"] = "direto" if input("Opção: ").strip() == "1" else "detalhado"
        elif op == "3":
            print("1. Visual  2. Sonoro  3. Ambos")
            p["preferencias_sensoriais"] = {"1": "visual", "2": "sonoro", "3": "ambos"}.get(input("Opção: ").strip(), "visual")
        elif op == "4":
            print("1. Visual  2. Sonoro  3. Ambos")
            p["tipo_alerta"] = {"1": "visual", "2": "sonoro", "3": "ambos"}.get(input("Opção: ").strip(), "visual")
        elif op == "5":
            p["lembretes_ativos"] = not p["lembretes_ativos"]
            estado = "ativados" if p["lembretes_ativos"] else "desativados"
            print(f"  Lembretes {estado}.")
        elif op == "6":
            while True:
                nova = input("  Nova senha (mín. 6 chars): ").strip()
                if len(nova) >= 6:
                    dados[usuario]["senha"] = _hash_senha(nova)
                    print("  ✅ Senha alterada.")
                    break
                print("  ⚠  Senha muito curta.")
        elif op == "7":
            break

        # RF03 RN02 — salvar mediante confirmação
        if op in ("1", "2", "3", "4", "5", "6"):
            if confirmar("  Salvar alterações?"):
                salvar_dados(dados)
                print("  ✅ Salvo.")
            else:
                # Recarrega dados para descartar mudança
                dados.update(carregar_dados())
            input("  Pressione Enter.")


# ── RF04 / RF07 — Tarefas com checklist e temporizador ───────────────────────

def gerenciar_tarefas_menu(dados: dict, usuario: str, chave: str, titulo: str):
    while True:
        exibir_cabecalho(titulo)
        tarefas = dados[usuario][chave]

        if not tarefas:
            print("  [Nenhuma tarefa cadastrada.]")
        else:
            for idx, t in enumerate(tarefas, 1):
                status = "✅" if t["concluida"] else "⬜"
                horario = f" [{t.get('data','')} {t.get('horario','')}]".strip(" []")
                horario_str = f" ({horario})" if horario else ""
                limite = f" — ⏱ {t.get('tempo_limite_min')} min" if t.get("tempo_limite_min") else ""
                print(f"  {idx}. {status} {t['titulo']}{horario_str}{limite}")
                # RF07 RN02 — checklist dos passos
                for pi, p in enumerate(t.get("passos", []), 1):
                    pstatus = "✅" if p["concluido"] else "○"
                    print(f"       {pi}. {pstatus} {p['texto']}")

        print("\n" + "-" * 50)
        print("  1. Nova tarefa        2. Editar tarefa")
        print("  3. Concluir/Reabrir   4. Marcar passo")
        print("  5. 🤖 Desmembrar IA   6. Definir tempo")
        print("  7. ⏱ Temporizador     8. Excluir tarefa")
        print("  9. Voltar")
        op = input("\n  Opção: ").strip()

        if op == "1":
            _criar_tarefa(dados, usuario, chave)

        elif op == "2" and tarefas:
            try:
                idx = int(input("  Número da tarefa: ")) - 1
                atual = tarefas[idx] if 0 <= idx < len(tarefas) else None
                if atual:
                    titulo = input(f"  Título [{atual['titulo']}]: ").strip() or atual['titulo']
                    data = input(f"  Data [{atual.get('data', '')}]: ").strip() or atual.get('data', '')
                    hora = input(f"  Horário [{atual.get('horario', '')}]: ").strip() or atual.get('horario', '')
                    ok = core_tarefas.atualizar_tarefa(dados, usuario, chave, idx, titulo, hora, data)
                    print("  ✅ Tarefa atualizada." if ok else "  ⚠  Conflito ou título inválido.")
                input("  Pressione Enter.")
            except ValueError:
                pass

        elif op == "3" and tarefas:
            try:
                idx = int(input("  Número da tarefa: ")) - 1
                concluida = core_tarefas.alternar_status_tarefa(dados, usuario, chave, idx)
                if concluida:
                    pts = dados[usuario].get("pontuacao", 0)
                    print(f"  ✅ Tarefa concluída! +10 pts (total: {pts})")
                else:
                    print("  ↩  Tarefa reaberta.")
                input("  Pressione Enter.")
            except ValueError:
                pass

        elif op == "4" and tarefas:
            try:
                idx_t = int(input("  Número da tarefa: ")) - 1
                tarefas_atuais = dados[usuario][chave]
                if 0 <= idx_t < len(tarefas_atuais) and tarefas_atuais[idx_t]["passos"]:
                    idx_p = int(input("  Número do passo: ")) - 1
                    core_tarefas.alternar_passo(dados, usuario, chave, idx_t, idx_p)
                else:
                    print("  ⚠  Tarefa sem passos ou inválida.")
                    input("  Pressione Enter.")
            except ValueError:
                pass

        elif op == "5" and tarefas:
            try:
                idx = int(input("  Número da tarefa para IA desmembrar: ")) - 1
                if 0 <= idx < len(tarefas):
                    passos = ia_service.gerar_passos_tarefa(tarefas[idx]["titulo"])
                    modo = "🌐 Lumi" if ia_service.usar_gemini() else "🤖 Simulado"
                    print(f"\n  {modo} — Passos sugeridos:")
                    for i, p in enumerate(passos, 1):
                        print(f"    {i}. {p}")
                    if confirmar("\n  Aceitar esses passos?"):
                        core_tarefas.injetar_passos_ia(dados, usuario, chave, idx, passos)
                        print("  ✅ Passos salvos.")
                    input("  Pressione Enter.")
            except ValueError:
                pass

        elif op == "6" and tarefas:
            try:
                idx = int(input("  Número da tarefa: ")) - 1
                mins = int(input("  Tempo limite (minutos): "))
                core_tarefas.definir_tempo_limite(dados, usuario, chave, idx, mins)
                print("  ✅ Tempo definido.")
                input("  Pressione Enter.")
            except ValueError:
                pass

        elif op == "7" and tarefas:
            try:
                idx = int(input("  Número da tarefa: ")) - 1
                if 0 <= idx < len(tarefas):
                    mins = tarefas[idx].get("tempo_limite_min") or int(input("  Duração (minutos): "))
                    temporizador(mins, tarefas[idx]["titulo"])
                    input("  Pressione Enter.")
            except ValueError:
                pass

        elif op == "8" and tarefas:
            try:
                idx = int(input("  Número da tarefa a excluir: ")) - 1
                if confirmar("  Confirma exclusão?"):
                    core_tarefas.excluir_tarefa(dados, usuario, chave, idx)
                    print("  ✅ Tarefa excluída.")
                input("  Pressione Enter.")
            except ValueError:
                pass

        elif op == "9":
            break


def _criar_tarefa(dados: dict, usuario: str, chave: str):
    """RF04 — criação com horário, data e validação de conflito."""
    titulo = input_obrigatorio("  Nome da tarefa: ")
    data   = input("  Data (DD/MM/AAAA) ou Enter para pular: ").strip()
    hora   = input("  Horário (HH:MM) ou Enter para pular: ").strip()

    sucesso = core_tarefas.adicionar_tarefa(dados, usuario, chave, titulo, hora, data)
    if sucesso:
        print("  ✅ Tarefa criada.")
    else:
        # RF04 RN02 — conflito de horário
        print("  ⚠  Conflito de horário! Já existe uma tarefa nesse horário e data.")
    input("  Pressione Enter.")


# ── RF05 — Estudos ────────────────────────────────────────────────────────────

def gerenciar_estudos_menu(dados: dict, usuario: str):
    while True:
        exibir_cabecalho("CRONOGRAMA DE ESTUDOS")
        estudos = dados[usuario].get("estudos", [])

        if not estudos:
            print("  [Nenhum estudo cadastrado.]")
        else:
            for idx, e in enumerate(estudos, 1):
                status = "✅" if e["concluido"] else "📖"
                progresso = min(100, int(e["tempo_estudado"] / e["tempo_estimado"] * 100)) if e["tempo_estimado"] else 0
                print(f"  {idx}. {status} [{e['prioridade'].upper()}] {e['materia']}")
                print(f"       Objetivo: {e['objetivo']}")
                print(f"       Progresso: {progresso}% ({e['tempo_estudado']}/{e['tempo_estimado']} min)")

        print("\n" + "-" * 50)
        print("  1. Novo estudo      2. Registrar progresso")
        print("  3. ⏱  Temporizador  4. Voltar")
        op = input("\n  Opção: ").strip()

        if op == "1":
            materia   = input_obrigatorio("  Matéria: ")
            objetivo  = input_obrigatorio("  Objetivo: ")
            try:
                tempo = int(input("  Tempo estimado (minutos): "))
            except ValueError:
                tempo = 0
            print("  Prioridade: 1. Alta  2. Média  3. Baixa")
            p_op = input("  Opção: ").strip()
            prio = {"1": "alta", "2": "media", "3": "baixa"}.get(p_op, "media")

            if core_tarefas.adicionar_estudo(dados, usuario, materia, objetivo, tempo, prio):
                print("  ✅ Estudo adicionado.")
            else:
                print("  ⚠  Verifique matéria e tempo (deve ser > 0).")
            input("  Pressione Enter.")

        elif op == "2" and estudos:
            try:
                idx  = int(input("  Número do estudo: ")) - 1
                mins = int(input("  Minutos estudados agora: "))
                core_tarefas.registrar_progresso_estudo(dados, usuario, idx, mins)
                e = dados[usuario]["estudos"][idx]
                if e["concluido"]:
                    print(f"  🎉 Estudo de {e['materia']} concluído! +15 pts")
                else:
                    prog = min(100, int(e["tempo_estudado"] / e["tempo_estimado"] * 100))
                    print(f"  ✅ Progresso: {prog}%")
                input("  Pressione Enter.")
            except ValueError:
                pass

        elif op == "3":
            try:
                mins = int(input("  Duração do temporizador (minutos): "))
                temporizador(mins)
                input("  Pressione Enter.")
            except ValueError:
                pass

        elif op == "4":
            break


# ── RF06 — Lembretes ──────────────────────────────────────────────────────────

def gerenciar_lembretes_menu(dados: dict, usuario: str):
    while True:
        exibir_cabecalho("LEMBRETES")
        lembretes = dados[usuario].get("lembretes", [])

        if not lembretes:
            print("  [Nenhum lembrete cadastrado.]")
        else:
            for idx, lem in enumerate(lembretes, 1):
                estado = "🔔" if lem["ativo"] else "🔕"
                print(f"  {idx}. {estado} [{lem['horario']}] {lem['mensagem']} ({lem['tipo_alerta']})")

        print("\n" + "-" * 50)
        print("  1. Novo lembrete    2. Editar lembrete")
        print("  3. Ativar/Desativar  4. Voltar")
        op = input("\n  Opção: ").strip()

        if op == "1":
            msg    = input_obrigatorio("  Mensagem: ")
            hora   = input_obrigatorio("  Horário (HH:MM): ")
            tipo_p = dados[usuario]["preferencias"].get("tipo_alerta", "visual")
            print(f"  Tipo de alerta (Enter = {tipo_p}): 1. Visual  2. Sonoro  3. Ambos")
            op_t   = input("  Opção: ").strip()
            tipo   = {"1": "visual", "2": "sonoro", "3": "ambos"}.get(op_t, tipo_p)
            core_tarefas.adicionar_lembrete(dados, usuario, msg, hora, tipo)
            print("  ✅ Lembrete criado.")
            input("  Pressione Enter.")

        elif op == "2" and lembretes:
            try:
                idx = int(input("  Número do lembrete: ")) - 1
                if 0 <= idx < len(lembretes):
                    atual = lembretes[idx]
                    msg = input(f"  Mensagem [{atual['mensagem']}]: ").strip() or atual['mensagem']
                    hora = input(f"  Horário [{atual['horario']}]: ").strip() or atual['horario']
                    print("  Tipo: 1. Visual  2. Sonoro  3. Ambos  (Enter mantém)")
                    op_t = input("  Opção: ").strip()
                    tipo = {"1": "visual", "2": "sonoro", "3": "ambos"}.get(op_t, atual.get("tipo_alerta", "visual"))
                    core_tarefas.atualizar_lembrete(dados, usuario, idx, msg, hora, tipo)
                    print("  ✅ Lembrete atualizado.")
                input("  Pressione Enter.")
            except ValueError:
                pass

        elif op == "3" and lembretes:
            try:
                idx = int(input("  Número do lembrete: ")) - 1
                ativo = core_tarefas.alternar_lembrete(dados, usuario, idx)
                if ativo is not None:
                    print("  🔔 Lembrete ativado." if ativo else "  🔕 Lembrete desativado.")
                input("  Pressione Enter.")
            except ValueError:
                pass

        elif op == "4":
            break


# ── Questionário e rede de apoio ──────────────────────────────────────────────

def questionario_menu(dados, usuario):
    perguntas = [
        ("rotina", "Como está a rotina atual da criança?"),
        ("comunicacao", "Como a criança costuma se comunicar?"),
        ("sensorial", "Quais situações sensoriais exigem mais apoio?"),
        ("interesses", "Quais são os principais interesses da criança?"),
        ("objetivos", "Quais objetivos a família gostaria de priorizar?")
    ]
    exibir_cabecalho("QUESTIONÁRIO INICIAL")
    respostas = dict(dados[usuario].get("questionario", {}).get("respostas", {}))
    print(f"Criança: {dados[usuario].get('nome_crianca') or '[não informado]'}\n")
    for chave, pergunta in perguntas:
        atual = respostas.get(chave, "")
        valor = input(f"{pergunta}\n  Resposta [{atual}]: ").strip()
        respostas[chave] = valor or atual
    dados[usuario]["questionario"] = {"respondido": True, "respostas": respostas, "atualizado_em": datetime.now().strftime("%d/%m/%Y %H:%M")}
    salvar_dados(dados)
    print("\n  ✅ Questionário salvo e vinculado ao perfil da criança.")
    input("  Pressione Enter.")


def _cadastro_contato(dados, usuario, tipo):
    contato = {
        "nome": input_obrigatorio("  Nome: "),
        "relacao": input_obrigatorio("  Relação/função: "),
        "telefone": input("  Telefone ou e-mail: ").strip(),
        "observacoes": input("  Observações: ").strip()
    }
    dados[usuario].setdefault(tipo, []).append(contato)
    salvar_dados(dados)
    print("  ✅ Cadastro salvo.")


def rede_apoio_menu(dados, usuario):
    while True:
        exibir_cabecalho("REDE DE APOIO")
        contatos = dados[usuario].setdefault("rede_apoio", [])
        for i, c in enumerate(contatos, 1):
            print(f"  {i}. {c['nome']} — {c['relacao']} | {c.get('telefone', '')}")
        print("\n  1. Adicionar contato  2. Registrar interação  3. Excluir contato  4. Voltar")
        op = input("  Opção: ").strip()
        if op == "1":
            _cadastro_contato(dados, usuario, "rede_apoio")
        elif op == "2" and contatos:
            try:
                idx = int(input("  Número do contato: ")) - 1
                if 0 <= idx < len(contatos):
                    texto = input_obrigatorio("  Como foi a interação/recado: ")
                    data, hora = datetime.now().strftime("%d/%m/%Y"), datetime.now().strftime("%H:%M")
                    dados[usuario].setdefault("interacoes", []).append({"tipo": "rede_apoio", "pessoa": contatos[idx]["nome"], "texto": texto, "data": data, "hora": hora})
                    salvar_dados(dados)
                    print("  ✅ Interação registrada.")
                input("  Pressione Enter.")
            except ValueError:
                pass
        elif op == "3" and contatos:
            try:
                idx = int(input("  Número do contato: ")) - 1
                if 0 <= idx < len(contatos) and confirmar("  Excluir este contato?"):
                    contatos.pop(idx); salvar_dados(dados)
            except ValueError:
                pass
        elif op == "4":
            break


def profissionais_menu(dados, usuario):
    while True:
        exibir_cabecalho("PROFISSIONAIS")
        profissionais = dados[usuario].setdefault("profissionais", [])
        for i, p in enumerate(profissionais, 1):
            print(f"  {i}. {p['nome']} — {p['relacao']} | {p.get('telefone', '')}")
        print("\n  1. Adicionar profissional  2. Registrar interação  3. Excluir profissional  4. Voltar")
        op = input("  Opção: ").strip()
        if op == "1":
            _cadastro_contato(dados, usuario, "profissionais")
        elif op == "2" and profissionais:
            try:
                idx = int(input("  Número do profissional: ")) - 1
                if 0 <= idx < len(profissionais):
                    texto = input_obrigatorio("  Evolução, orientação ou recado: ")
                    data, hora = datetime.now().strftime("%d/%m/%Y"), datetime.now().strftime("%H:%M")
                    dados[usuario].setdefault("interacoes", []).append({"tipo": "profissional", "pessoa": profissionais[idx]["nome"], "texto": texto, "data": data, "hora": hora})
                    salvar_dados(dados)
                    print("  ✅ Interação registrada.")
                input("  Pressione Enter.")
            except ValueError:
                pass
        elif op == "3" and profissionais:
            try:
                idx = int(input("  Número do profissional: ")) - 1
                if 0 <= idx < len(profissionais) and confirmar("  Excluir este profissional?"):
                    profissionais.pop(idx); salvar_dados(dados)
            except ValueError:
                pass
        elif op == "4":
            break


# ── RF08 — Histórico ──────────────────────────────────────────────────────────

def exibir_historico_menu(dados: dict, usuario: str):
    exibir_cabecalho("HISTÓRICO DE ATIVIDADES")
    historico = dados[usuario].get("historico", [])

    if not historico:
        print("  [Nenhuma atividade registrada ainda.]")
        input("\n  Pressione Enter.")
        return

    print("  Filtrar por data (DD/MM/AAAA) ou Enter para ver tudo:")
    filtro = input("  ").strip()

    registros = historico
    if filtro:
        try:
            data_fmt = datetime.strptime(filtro, "%d/%m/%Y").strftime("%Y-%m-%d")
            registros = [r for r in historico if r.get("data") == data_fmt]
        except ValueError:
            print("  ⚠  Formato inválido. Exibindo todos.")

    if not registros:
        print("  [Nenhuma atividade nessa data.]")
    else:
        print()
        data_atual = ""
        for r in sorted(registros, key=lambda x: (x.get("data",""), x.get("hora",""))):
            if r.get("data") != data_atual:
                data_atual = r.get("data", "")
                try:
                    data_exib = datetime.strptime(data_atual, "%Y-%m-%d").strftime("%d/%m/%Y")
                except ValueError:
                    data_exib = data_atual
                print(f"\n  📅 {data_exib}")
                print("  " + "-" * 40)
            print(f"  {r.get('hora','--:--')}  ✅ {r.get('atividade','')}")

    input("\n  Pressione Enter.")


# ── RF11 — Dashboard ──────────────────────────────────────────────────────────

def exibir_dashboard(dados: dict, usuario: str):
    """RF11 — painel resumido exibido ao fazer login."""
    exibir_cabecalho(f"BEM-VINDO(A), {dados[usuario]['nome'].upper()}!")

    hoje = datetime.now().strftime("%Y-%m-%d")
    hora_atual = datetime.now().strftime("%H:%M")

    # Tarefas do dia (RF11 RN01)
    td = dados[usuario].get("tarefas_diarias", [])
    te = dados[usuario].get("tarefas_educacionais", [])
    todas = td + te

    tarefas_hoje = [t for t in todas if t.get("data") == hoje or not t.get("data")]
    pendentes    = sum(1 for t in tarefas_hoje if not t["concluida"])
    concluidas   = sum(1 for t in tarefas_hoje if t["concluida"])

    # Progresso estudos (RF11 RN02)
    estudos = dados[usuario].get("estudos", [])
    estudos_total     = len(estudos)
    estudos_concluidos = sum(1 for e in estudos if e["concluido"])

    # Notificações pendentes (RF11 RN04)
    lembretes_ativos = [
        l for l in dados[usuario].get("lembretes", [])
        if l.get("ativo") and l.get("horario", "") <= hora_atual
    ]

    print(f"  📅 Hoje: {datetime.now().strftime('%d/%m/%Y')}  |  🕐 {hora_atual}")
    print(f"  🏆 Pontuação: {dados[usuario].get('pontuacao', 0)} pts\n")

    print("  ─── Tarefas do dia ──────────────────────")
    print(f"  ⬜ Pendentes : {pendentes}")
    print(f"  ✅ Concluídas: {concluidas}")

    print("\n  ─── Estudos ─────────────────────────────")
    if estudos_total:
        pct = int(estudos_concluidos / estudos_total * 100)
        barra = ("█" * (pct // 10)).ljust(10, "░")
        print(f"  Progresso: [{barra}] {pct}% ({estudos_concluidos}/{estudos_total})")
    else:
        print("  Nenhum estudo cadastrado.")

    # Histórico recente (RF11 RN03)
    historico = dados[usuario].get("historico", [])
    recentes  = historico[-3:] if historico else []
    if recentes:
        print("\n  ─── Atividades recentes ─────────────────")
        for r in reversed(recentes):
            print(f"  ✅ {r.get('hora','--:--')}  {r.get('atividade','')}")

    # Lembretes pendentes (RF11 RN04)
    if lembretes_ativos:
        print("\n  ─── Lembretes pendentes ─────────────────")
        for l in lembretes_ativos:
            print(f"  🔔 [{l['horario']}] {l['mensagem']}")

    print()
    input("  Pressione Enter para continuar...")


# ── RF10 — Central de IA ──────────────────────────────────────────────────────

def painel_ia_menu(dados: dict, usuario: str):
    exibir_cabecalho("ASSISTENTE DE IA")
    modo = "🌐 Lumi (online)" if ia_service.usar_gemini() else "🤖 Modo simulado (offline)"
    print(f"  Modo: {modo}")
    print("  Peça ajuda para organizar rotinas, simplificar tarefas ou tirar dúvidas.")
    print("  Digite 'sair' para voltar.\n")
    estilo = dados[usuario]["preferencias"]["estilo_instrucao"]

    while True:
        pergunta = input("\n  Você: ").strip()
        if pergunta.lower() == "sair":
            break
        if not pergunta:
            continue
        print("\n  ⏳ Processando...")
        respostas = ia_service.obter_resposta_ia(pergunta, estilo)
        print(f"\n  [Assistente — Modo {estilo.upper()}]")
        for linha in respostas:
            print(f"  • {linha}")
        print("  " + "-" * 46)


# ── Painel principal ──────────────────────────────────────────────────────────

def painel_principal_menu(dados: dict, usuario: str):
    # RF11 — exibe dashboard ao entrar
    dados = carregar_dados()
    exibir_dashboard(dados, usuario)

    # Verifica lembretes pendentes ao entrar
    _verificar_lembretes_pendentes(dados, usuario)

    while True:
        exibir_cabecalho(f"ATÍPICA — {dados[usuario]['nome']}")
        print("  1. Tarefas Diárias")
        print("  2. Tarefas Educacionais")
        print("  3. Cronograma de Estudos")
        print("  4. Lembretes")
        print("  5. Questionário da criança")
        print("  6. Rede de apoio")
        print("  7. Profissionais")
        print("  8. Histórico")
        print("  9. Meu Perfil")
        print("  10. Lumi IA Assistente")
        print("  11. Logout")

        op = input("\n  Opção: ").strip()
        dados = carregar_dados()   # RF11 RN05 — recarrega a cada acesso

        if op == "1":
            gerenciar_tarefas_menu(dados, usuario, "tarefas_diarias", "TAREFAS DIÁRIAS")
        elif op == "2":
            gerenciar_tarefas_menu(dados, usuario, "tarefas_educacionais", "TAREFAS EDUCACIONAIS")
        elif op == "3":
            gerenciar_estudos_menu(dados, usuario)
        elif op == "4":
            gerenciar_lembretes_menu(dados, usuario)
        elif op == "5":
            questionario_menu(dados, usuario)
        elif op == "6":
            rede_apoio_menu(dados, usuario)
        elif op == "7":
            profissionais_menu(dados, usuario)
        elif op == "8":
            exibir_historico_menu(dados, usuario)
        elif op == "9":
            editar_perfil_menu(dados, usuario)
        elif op == "10":
            painel_ia_menu(dados, usuario)
        elif op == "11":
            break
