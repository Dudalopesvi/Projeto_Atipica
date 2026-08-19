<div align="center">

# Atípica

### Organização, previsibilidade e apoio para cada rotina

Uma aplicação criada para apoiar responsáveis, crianças, pessoas com TEA, rede de apoio e profissionais na construção de rotinas mais claras, acolhedoras e personalizadas.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)[![React](https://img.shields.io/badge/Frontend-React-61DAFB?logo=react&logoColor=111111)](https://react.dev/)[![Vite](https://img.shields.io/badge/Build-Vite-646CFF?logo=vite&logoColor=white)](https://vitejs.dev/)[![Acessibilidade](https://img.shields.io/badge/Foco-WCAG%202.2-6A1B9A)](https://www.w3.org/TR/WCAG22/)

</div>

---

## Sobre o projeto

A **Atípica** é uma aplicação de apoio à organização da rotina de crianças e pessoas com Transtorno do Espectro Autista (TEA). O sistema permite que cada família informe suas próprias necessidades, cadastre o nome e as informações da criança e organize tarefas, lembretes, contatos e atividades de forma personalizada.

> **Atenção:** a Atípica é uma ferramenta de organização e apoio. Ela não substitui diagnóstico, avaliação ou orientação de profissionais de saúde, educação ou assistência social.

## O que a Atípica oferece

| Recurso | Como ajuda |
| --- | --- |
| **Perfil da criança** | Permite cadastrar o nome e as informações fornecidas pelo responsável ou pela própria pessoa. |
| **Rotina visual** | Organiza horários, tarefas e lembretes em uma apresentação simples. |
| **Tarefas editáveis** | Permite criar, atualizar, concluir e reorganizar atividades. |
| **Lembretes** | Ajuda a registrar compromissos e avisos importantes. |
| **Rede de apoio** | Centraliza contatos de familiares, cuidadores, escola e profissionais. |
| **Interações** | Registra observações e comunicações com pessoas da rede de apoio. |
| **Biblioteca** | Pesquisa materiais sobre TEA, incluindo artigos, livros, séries e filmes. |
| **Assistente de IA** | Oferece apoio para organizar situações e dividir atividades em passos menores. |
| **Impressão da rotina** | Gera uma versão limpa e adequada para imprimir e usar no dia a dia. |
| **Acessibilidade** | Prioriza contraste, foco visível, textos claros e navegação por teclado. |

## Navegação rápida

- [Como o projeto funciona](#como-o-projeto-funciona)

- [Instalação rápida](#instala%C3%A7%C3%A3o-r%C3%A1pida)

- [Configurar a inteligência artificial](#configurar-a-intelig%C3%AAncia-artificial)

- [Iniciar o sistema](#iniciar-o-sistema)

- [Estrutura das pastas](#estrutura-das-pastas)

- [Solução de problemas](#solu%C3%A7%C3%A3o-de-problemas)

- [Segurança](#seguran%C3%A7a)

## Como o projeto funciona

A Atípica possui duas partes principais:

```
┌─────────────────────────────┐       ┌──────────────────────────────┐
│        Front-end             │       │          Back-end             │
│      React + Vite            │ ◄───► │       Python + FastAPI         │
│      localhost:5173          │       │       127.0.0.1:8000          │
└─────────────────────────────┘       └──────────────────────────────┘
                                                    │
                                                    ▼
                                      Dados locais e serviço de IA
```

O **front-end** é a interface visual aberta no navegador. O **back-end** processa os dados, disponibiliza a API e conversa com o serviço de IA quando a chave está configurada.

## Instalação rápida

Este passo a passo é para Ubuntu/Linux.

### 1. Instale os programas necessários

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip nodejs npm
```

Confira as versões:

```bash
git --version
python3 --version
node --version
npm --version
```

### 2. Baixe o projeto

```bash
mkdir -p ~/Documentos
cd ~/Documentos
git clone https://github.com/Dudalopesvi/Projeto_Atipica.git Projeto_Atipica
cd ~/Documentos/Projeto_Atipica
```

### 3. Crie o ambiente Python

```bash
python3 -m venv .venv-atipica
source .venv-atipica/bin/activate
```

Quando o ambiente estiver ativo, o terminal exibirá algo parecido com:

```
(.venv-atipica )
```

### 4. Instale as dependências

```bash
python -m pip install --upgrade pip
python -m pip install fastapi uvicorn pydantic google-genai python-dotenv
```

## Configurar a inteligência artificial

A chave deve ficar **somente no back-end**. Nunca coloque a chave no front-end, no README, em screenshots ou em commits.

Crie o arquivo local `Atipica/.env`:

```bash
cd ~/Documentos/Projeto_Atipica/Atipica
nano .env
```

Cole uma única linha, trocando o valor pela sua chave real:

```
GEMINI_API_KEY=SUA_CHAVE_REAL
```

No editor `nano`, salve com:

```
Ctrl + O
Enter
Ctrl + X
```

Teste a configuração sem exibir a chave:

```bash
../.venv-atipica/bin/python -c "from core.ia_service import usar_gemini; print('IA online:', usar_gemini())"
```

Resultado esperado:

```
IA online: True
```

Se aparecer `False`, verifique se o arquivo está exatamente em:

```
Projeto_Atipica/Atipica/.env
```

## Iniciar o sistema

É necessário usar **dois terminais**.

### Terminal 1 — API e back-end

```bash
cd ~/Documentos/Projeto_Atipica
source .venv-atipica/bin/activate
cd Atipica
../.venv-atipica/bin/python -m uvicorn api:app --reload
```

Quando funcionar, aparecerá:

```
Uvicorn running on http://127.0.0.1:8000
Application startup complete.
```

Documentação da API:

```
http://127.0.0.1:8000/docs
```

### Terminal 2 — front-end

Abra outro terminal e execute:

```bash
cd ~/Documentos/Projeto_Atipica/atipica-frontend
npm install
npm run dev
```

Abra no navegador:

```
http://localhost:5173
```

> Mantenha os dois terminais abertos enquanto estiver usando a aplicação.

## Estrutura das pastas

```
Projeto_Atipica/
├── Atipica/                      # Back-end Python e API
│   ├── api.py                    # Endpoints FastAPI
│   ├── main.py                   # Aplicação de terminal
│   ├── core/
│   │   ├── ia_service.py         # IA online e fallback offline
│   │   └── tarefas.py             # Regras de tarefas e lembretes
│   ├── data/
│   │   ├── data_manager.py       # Dados, perfil e biblioteca
│   │   └── db_config.py
│   ├── ui/                       # Menus do aplicativo de terminal
│   ├── schema.sql
│   ├── migracao_biblioteca_rede.sql
│   └── .env                      # Local; não versionar
│
├── atipica-frontend/             # Interface React/Vite
│   ├── src/
│   │   ├── AtipicaApp.jsx
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── .venv-atipica/                # Ambiente local; não versionar
└── README.md
```

## Impressão da rotina

Na tela de rotina, use o botão **Imprimir**. A versão de impressão foi planejada para:

- remover menus e controles que não são necessários no papel;

- manter o nome da criança, data, horários, atividades e lembretes;

- apresentar textos legíveis e alto contraste;

- indicar tarefas concluídas e pendentes também por texto, não somente por cor;

- facilitar a impressão em papel A4.

Antes de confirmar, confira a prévia de impressão do navegador.

## Acessibilidade e usabilidade

A interface segue princípios das [WCAG 2.2](https://www.w3.org/TR/WCAG22/) e utiliza como referência o [eMAG](https://www.gov.br/governodigital/pt-br/acessibilidade-e-usuario/acessibilidade-digital/modelo-de-acessibilidade).

Entre as decisões adotadas estão:

- linguagem direta e instruções curtas;

- labels explícitos nos formulários;

- foco visível para navegação por teclado;

- contraste adequado;

- mensagens textuais para estados da rotina;

- áreas de interação confortáveis;

- layout responsivo para diferentes tamanhos de tela;

- impressão sem elementos desnecessários.

## Solução de problemas

### `ModuleNotFoundError: No module named 'fastapi'`

Ative o ambiente correto e instale as dependências:

```bash
cd ~/Documentos/Projeto_Atipica
source .venv-atipica/bin/activate
python -m pip install fastapi uvicorn pydantic google-genai python-dotenv
```

### `Address already in use`

A API provavelmente já está funcionando. Verifique:

```bash
curl -I http://127.0.0.1:8000/docs
```

Se aparecer `HTTP/1.1 200 OK`, não inicie outra API.

### `npm ERR! package.json not found`

O npm foi executado na pasta errada. Use:

```bash
cd ~/Documentos/Projeto_Atipica/atipica-frontend
npm run dev
```

Não execute `npm` dentro da pasta `Atipica`.

### A IA aparece como offline

Confirme a chave:

```bash
cd ~/Documentos/Projeto_Atipica/Atipica
../.venv-atipica/bin/python -c "from core.ia_service import usar_gemini; print('IA online:', usar_gemini( ))"
```

Depois de alterar `.env`, reinicie a API.

### A tela fica branca

Atualize a página com `Ctrl+Shift+R`. Se persistir, pressione `F12`, abra **Console** e procure mensagens em vermelho. Também valide o front-end:

```bash
cd ~/Documentos/Projeto_Atipica/atipica-frontend
npm run build
```

## Segurança

Nunca versione estes arquivos ou pastas:

```
.env
.venv/
.venv-atipica/
**/venv/
**/__pycache__/
*.pyc
node_modules/
dist/
Backup/
tpac_users.json
```

Confira antes de fazer um commit:

```bash
git status
git diff --cached --check
```

Se uma chave for exposta, revogue-a imediatamente e gere uma nova no serviço da IA.

## Validação do projeto

### Validar o back-end

```bash
cd Atipica
../.venv-atipica/bin/python -m py_compile api.py data/data_manager.py core/ia_service.py
```

### Validar o front-end

```bash
cd atipica-frontend
npm run build
```

## Responsabilidade de uso

Conteúdos da biblioteca e respostas da IA devem ser analisados criticamente. A aplicação não substitui acompanhamento profissional individualizado, diagnóstico ou tratamento.

<div align="center">

### Atípica

**Uma rotina mais clara começa com informação, acolhimento e participação.**

</div>
