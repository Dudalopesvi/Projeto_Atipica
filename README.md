[Projeto_Atipica-README.md](https://github.com/user-attachments/files/30866520/Projeto_Atipica-README.md)
<div align="center">

# 🧩 Atípica

### Assistente de organização pessoal para pessoas com TEA

[![Python](https://img.shields.io/badge/Python-3.13%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Gemini API](https://img.shields.io/badge/Gemini%20API-opcional-8E75B2?logo=googlegemini&logoColor=white)](https://ai.google.dev/)

</div>

---

## ✨ Sobre o projeto

**Atípica** é um sistema de linha de comando (CLI) pensado para reduzir a carga cognitiva de pessoas com **TEA (Transtorno do Espectro Autista)**, ajudando na organização de tarefas diárias, estudos e lembretes. A comunicação do sistema — inclusive as respostas de IA — segue regras específicas de acessibilidade: frases curtas, linguagem direta, sem ambiguidade, ironia ou metáforas.

O projeto nasceu com armazenamento em JSON e foi **migrado para MySQL**, mantendo a mesma lógica de negócio: as funções `carregar_dados()` e `salvar_dados()` continuam recebendo e devolvendo o mesmo formato de dados de antes, só que agora persistem em um banco relacional de verdade.

## 🚀 Funcionalidades

| Recurso | Descrição |
|---|---|
| 👤 **Perfis de usuário** | Cadastro e login com senha protegida por hash SHA-256 |
| 🔒 **Bloqueio por tentativas** | Bloqueia o acesso após tentativas de login inválidas, com código de desbloqueio |
| ✅ **Tarefas diárias e educacionais** | Criação, conclusão e organização de tarefas, com validação de conflito de horário |
| 🪜 **Passos guiados** | Cada tarefa pode ser dividida em passos menores (checklist) |
| 🤖 **Assistente de IA (opcional)** | Integração com a API do Gemini para sugerir passos e planos de ação, com respostas adaptadas ao estilo de comunicação do usuário (direto ou por etapas) |
| 📚 **Estudos** | Registro de matérias, objetivos, tempo estimado e progresso |
| ⏰ **Lembretes** | Lembretes configuráveis com tipo de alerta (visual, sonoro, etc.) |
| 📜 **Histórico de atividades** | Acompanhamento do que foi feito, por categoria e status |
| 🎯 **Pontuação** | Sistema de pontos como reforço positivo ao concluir tarefas |
| ⚙️ **Preferências personalizadas** | Estilo de instrução, preferências sensoriais e tipo de alerta configuráveis por usuário |

## 🛠️ Tecnologias

- [Python](https://www.python.org/) 3.13+
- [MySQL](https://www.mysql.com/) — persistência dos dados (usuários, tarefas, passos, estudos, lembretes e histórico)
- [Google Gemini API](https://ai.google.dev/) (`google-genai`) — geração de sugestões de IA, com **fallback simulado** caso nenhuma chave de API esteja configurada

## 📂 Estrutura do projeto

```
Atipica/
├─ main.py                # Ponto de entrada: menu inicial (entrar / criar perfil / sair)
├─ schema.sql               # Schema MySQL (usuarios, tarefas, passos, estudos, lembretes, historico)
├─ data/
│  ├─ db_config.py            # Configuração de conexão com o MySQL (via variáveis de ambiente)
│  └─ data_manager.py           # Camada de acesso a dados (carregar/salvar)
├─ core/
│  ├─ tarefas.py               # Regras de negócio: criação, conclusão e validação de tarefas
│  └─ ia_service.py             # Integração com a API do Gemini + respostas simuladas de fallback
├─ ui/
│  ├─ menus.py                  # Menus interativos do terminal (cadastro, login, painel principal)
│  └─ utils.py                    # Funções auxiliares de exibição (cabeçalhos, alertas, temporizador)
└─ LEIA-ME.md                      # Guia detalhado da migração JSON → MySQL
```

## ⚙️ Pré-requisitos

- [Python](https://www.python.org/) 3.13 ou superior
- [MySQL](https://www.mysql.com/) instalado e em execução
- (Opcional) uma chave de API do [Google Gemini](https://ai.google.dev/) para habilitar as sugestões de IA reais

## 📦 Instalação

```bash
git clone https://github.com/Dudalopesvi/Projeto_Atipica.git
cd Projeto_Atipica/Atipica
pip install -r requirements.txt
```

## 🗄️ Configurando o banco de dados

1. Com o MySQL em execução, crie o banco e as tabelas a partir do schema pronto:

```bash
mysql -u root -p < schema.sql
```

Isso cria o banco `atipica` e as tabelas `usuarios`, `tarefas`, `passos`, `estudos`, `lembretes` e `historico`.

2. As credenciais de conexão podem ser configuradas por variáveis de ambiente (opcional — por padrão usa `localhost` / `root`):

```bash
export ATIPICA_DB_HOST=localhost
export ATIPICA_DB_USER=root
export ATIPICA_DB_PASSWORD=sua_senha
export ATIPICA_DB_NAME=atipica
```

3. (Opcional) Para habilitar as sugestões reais de IA, defina a chave da API do Gemini:

```bash
export GEMINI_API_KEY=sua_chave_aqui
```

> Sem essa variável configurada, o sistema continua funcionando normalmente — apenas usa respostas de IA **simuladas** como fallback.

## ▶️ Executando o projeto

```bash
python main.py
```

O sistema abre um menu no terminal para **entrar**, **criar um novo perfil** ou **encerrar**.

## 🔒 Segurança

- Senhas nunca são armazenadas em texto puro — são protegidas com hash SHA-256.
- As credenciais do banco não ficam fixas no código: são lidas de variáveis de ambiente, com valores padrão apenas para desenvolvimento local.


## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch (`git checkout -b feature/minha-feature`)
3. Commit suas mudanças (`git commit -m 'feat: minha feature'`)
4. Push para a branch (`git push origin feature/minha-feature`)
5. Abra um Pull Request

---

<div align="center">
Feito por <a href="https://github.com/Dudalopesvi">Eduarda Lopes Vieira</a>
</div>
