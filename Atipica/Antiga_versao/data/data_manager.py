"""
Camada de persistência do Atípica — versão MySQL.

Mantém EXATAMENTE a mesma interface do data_manager.py original
baseado em JSON:

    dados = carregar_dados()      # -> dict {email: {perfil...}}
    salvar_dados(dados)           # grava o dict inteiro de volta
    perfil_padrao(...)            # monta a estrutura de um novo usuário

Por isso, nenhum outro arquivo do projeto (main.py, ui/menus.py,
core/tarefas.py) precisa ser alterado: eles continuam enxergando
um dicionário Python normal, só que agora ele é montado/persistido
a partir de tabelas do MySQL em vez de um arquivo .json.
"""

import mysql.connector
from mysql.connector import Error
from data.db_config import DB_CONFIG


def _conectar():
    return mysql.connector.connect(**DB_CONFIG)


# ── Leitura: reconstrói o dicionário a partir das tabelas ─────────────────

def carregar_dados() -> dict:
    conn = _conectar()
    dados = {}
    try:
        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT * FROM usuarios")
        usuarios = cur.fetchall()

        for u in usuarios:
            email = u["email"]
            dados[email] = {
                "nome": u["nome"],
                "email": u["email"],
                "senha": u["senha"],
                "tentativas_login": u["tentativas_login"],
                "bloqueado": bool(u["bloqueado"]),
                "codigo_desbloqueio": u["codigo_desbloqueio"],
                "preferencias": {
                    "estilo_instrucao": u["estilo_instrucao"],
                    "preferencias_sensoriais": u["preferencias_sensoriais"],
                    "tipo_alerta": u["tipo_alerta"],
                    "lembretes_ativos": bool(u["lembretes_ativos"]),
                },
                "pontuacao": u["pontuacao"],
                "tarefas_diarias": [],
                "tarefas_educacionais": [],
                "estudos": [],
                "lembretes": [],
                "historico": [],
            }

        # tarefas (diárias + educacionais) e seus passos
        cur.execute("SELECT * FROM tarefas ORDER BY usuario_email, tipo, ordem")
        tarefas = cur.fetchall()

        cur.execute("SELECT * FROM passos ORDER BY tarefa_id, ordem")
        passos_por_tarefa = {}
        for p in cur.fetchall():
            passos_por_tarefa.setdefault(p["tarefa_id"], []).append({
                "texto": p["texto"],
                "concluido": bool(p["concluido"]),
            })

        for t in tarefas:
            if t["usuario_email"] not in dados:
                continue
            dados[t["usuario_email"]][t["tipo"]].append({
                "titulo": t["titulo"],
                "horario": t["horario"],
                "data": t["data"],
                "concluida": bool(t["concluida"]),
                "passos": passos_por_tarefa.get(t["id"], []),
                "tempo_limite_min": t["tempo_limite_min"],
            })

        cur.execute("SELECT * FROM estudos ORDER BY usuario_email, ordem")
        for e in cur.fetchall():
            if e["usuario_email"] not in dados:
                continue
            dados[e["usuario_email"]]["estudos"].append({
                "materia": e["materia"],
                "objetivo": e["objetivo"],
                "tempo_estimado": e["tempo_estimado"],
                "tempo_estudado": e["tempo_estudado"],
                "prioridade": e["prioridade"],
                "concluido": bool(e["concluido"]),
            })

        cur.execute("SELECT * FROM lembretes ORDER BY usuario_email, ordem")
        for l in cur.fetchall():
            if l["usuario_email"] not in dados:
                continue
            dados[l["usuario_email"]]["lembretes"].append({
                "mensagem": l["mensagem"],
                "horario": l["horario"],
                "tipo_alerta": l["tipo_alerta"],
                "ativo": bool(l["ativo"]),
            })

        cur.execute("SELECT * FROM historico ORDER BY usuario_email, ordem")
        for h in cur.fetchall():
            if h["usuario_email"] not in dados:
                continue
            dados[h["usuario_email"]]["historico"].append({
                "atividade": h["atividade"],
                "categoria": h["categoria"],
                "data": h["data"],
                "hora": h["hora"],
                "status": h["status"],
            })

        cur.close()
        return dados
    except Error as e:
        print(f"  ⚠ Erro ao carregar dados do MySQL: {e}")
        return {}
    finally:
        conn.close()


# ── Escrita: sincroniza o dicionário inteiro de volta pro banco ───────────
#
# O restante do sistema chama salvar_dados(dados) toda vez que muda
# QUALQUER coisa, sempre passando o dicionário completo (igual fazia
# com o JSON). Para manter esse contrato sem reescrever tarefas.py e
# menus.py, aqui fazemos um "sync" completo: apagamos as linhas-filhas
# de cada usuário e reinserimos a partir do dict. Para o volume de
# dados de um app como esse, isso é simples e seguro (evita ficar
# calculando diffs), mas fica o registro: numa evolução futura vale
# trocar por updates pontuais por operação.

def salvar_dados(dados: dict):
    conn = _conectar()
    try:
        cur = conn.cursor()

        for email, perfil in dados.items():
            prefs = perfil.get("preferencias", {})
            cur.execute("""
                INSERT INTO usuarios
                    (email, nome, senha, tentativas_login, bloqueado,
                     codigo_desbloqueio, estilo_instrucao,
                     preferencias_sensoriais, tipo_alerta,
                     lembretes_ativos, pontuacao)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE
                    nome=VALUES(nome), senha=VALUES(senha),
                    tentativas_login=VALUES(tentativas_login),
                    bloqueado=VALUES(bloqueado),
                    codigo_desbloqueio=VALUES(codigo_desbloqueio),
                    estilo_instrucao=VALUES(estilo_instrucao),
                    preferencias_sensoriais=VALUES(preferencias_sensoriais),
                    tipo_alerta=VALUES(tipo_alerta),
                    lembretes_ativos=VALUES(lembretes_ativos),
                    pontuacao=VALUES(pontuacao)
            """, (
                email, perfil["nome"], perfil["senha"],
                perfil.get("tentativas_login", 0),
                perfil.get("bloqueado", False),
                perfil.get("codigo_desbloqueio"),
                prefs.get("estilo_instrucao", "direto"),
                prefs.get("preferencias_sensoriais", "visual"),
                prefs.get("tipo_alerta", "visual"),
                prefs.get("lembretes_ativos", True),
                perfil.get("pontuacao", 0),
            ))

            # Limpa as tabelas-filhas do usuário e reinsere do zero
            cur.execute("DELETE FROM tarefas WHERE usuario_email=%s", (email,))
            cur.execute("DELETE FROM estudos WHERE usuario_email=%s", (email,))
            cur.execute("DELETE FROM lembretes WHERE usuario_email=%s", (email,))
            cur.execute("DELETE FROM historico WHERE usuario_email=%s", (email,))

            for tipo in ("tarefas_diarias", "tarefas_educacionais"):
                for ordem, t in enumerate(perfil.get(tipo, [])):
                    cur.execute("""
                        INSERT INTO tarefas
                            (usuario_email, tipo, titulo, horario, data,
                             concluida, tempo_limite_min, ordem)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    """, (
                        email, tipo, t["titulo"], t.get("horario", ""),
                        t.get("data", ""), t.get("concluida", False),
                        t.get("tempo_limite_min", 0), ordem,
                    ))
                    tarefa_id = cur.lastrowid
                    for p_ordem, p in enumerate(t.get("passos", [])):
                        cur.execute("""
                            INSERT INTO passos (tarefa_id, texto, concluido, ordem)
                            VALUES (%s,%s,%s,%s)
                        """, (tarefa_id, p["texto"], p.get("concluido", False), p_ordem))

            for ordem, e in enumerate(perfil.get("estudos", [])):
                cur.execute("""
                    INSERT INTO estudos
                        (usuario_email, materia, objetivo, tempo_estimado,
                         tempo_estudado, prioridade, concluido, ordem)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    email, e["materia"], e.get("objetivo", ""),
                    e["tempo_estimado"], e.get("tempo_estudado", 0),
                    e["prioridade"], e.get("concluido", False), ordem,
                ))

            for ordem, l in enumerate(perfil.get("lembretes", [])):
                cur.execute("""
                    INSERT INTO lembretes
                        (usuario_email, mensagem, horario, tipo_alerta, ativo, ordem)
                    VALUES (%s,%s,%s,%s,%s,%s)
                """, (
                    email, l["mensagem"], l.get("horario", ""),
                    l["tipo_alerta"], l.get("ativo", True), ordem,
                ))

            for ordem, h in enumerate(perfil.get("historico", [])):
                cur.execute("""
                    INSERT INTO historico
                        (usuario_email, atividade, categoria, data, hora, status, ordem)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                """, (
                    email, h["atividade"], h["categoria"], h["data"],
                    h["hora"], h["status"], ordem,
                ))

        conn.commit()
        cur.close()
    except Error as e:
        conn.rollback()
        print(f"  ⚠ Erro ao salvar dados no MySQL: {e}")
    finally:
        conn.close()


def perfil_padrao(nome: str, email: str, senha_hash: str, estilo: str,
                  preferencias_sensoriais: str, tipo_alerta: str) -> dict:
    """Retorna a estrutura completa de um novo usuário. (Sem alteração —
    continua sendo só um dict Python em memória.)"""
    return {
        "nome": nome,
        "email": email,
        "senha": senha_hash,
        "tentativas_login": 0,
        "bloqueado": False,
        "codigo_desbloqueio": None,
        "preferencias": {
            "estilo_instrucao": estilo,
            "preferencias_sensoriais": preferencias_sensoriais,
            "tipo_alerta": tipo_alerta,
            "lembretes_ativos": True
        },
        "pontuacao": 0,
        "tarefas_diarias": [],
        "tarefas_educacionais": [],
        "estudos": [],
        "lembretes": [],
        "historico": []
    }
