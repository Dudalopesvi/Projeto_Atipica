# Migração do Atípica: JSON → MySQL

## O que muda no seu projeto

Só a pasta `data/`. Nenhum arquivo de `ui/`, `core/` ou `main.py` precisa
ser alterado, porque `carregar_dados()` e `salvar_dados(dados)` continuam
recebendo/devolvendo o mesmo formato de dicionário Python de antes —
só que agora por trás delas tem MySQL, não mais `tpac_users.json`.

## Passo a passo

1. **Instalar dependência**
   ```
   pip install -r requirements.txt
   ```

2. **Criar o banco e as tabelas**
   Com o MySQL rodando, execute o `schema.sql`:
   ```
   mysql -u root -p < schema.sql
   ```
   Isso cria o banco `atipica` e as tabelas `usuarios`, `tarefas`,
   `passos`, `estudos`, `lembretes` e `historico`.

3. **Configurar a conexão**
   Edite `data/db_config.py` (ou defina variáveis de ambiente
   `ATIPICA_DB_HOST`, `ATIPICA_DB_USER`, `ATIPICA_DB_PASSWORD`,
   `ATIPICA_DB_NAME`) com as credenciais do seu MySQL.

4. **Substituir o arquivo antigo**
   Copie `data/data_manager.py` e `data/db_config.py` deste pacote
   para dentro de `Atipica/data/` do seu projeto, substituindo o
   `data_manager.py` original.

5. **(Opcional) Importar os dados que já existem no JSON**
   ```
   cd Atipica
   python ../migrar_json_para_mysql.py tpac_users.json
   ```
   Isso lê seus usuários de teste (Matheus, Rafa) e grava no banco.

6. **Rodar normalmente**
   ```
   python main.py
   ```
   O sistema vai funcionar exatamente igual, só que lendo/gravando no
   MySQL. O `tpac_users.json` pode ficar guardado como backup ou ser
   removido — ele não é mais usado.

## Por que essa abordagem

O código original inteiro (`tarefas.py`, `menus.py`) trabalha em cima
de um dicionário `dados` carregado uma vez e salvo por completo a cada
alteração — nunca faz UPDATE pontual. Duas formas de migrar:

- **A que fiz aqui:** manter esse contrato, trocando só o "motor" de
  carregar/salvar por dentro. Zero mudança nas regras de negócio,
  schema relacional de verdade (tabelas normalizadas, chaves
  estrangeiras, sem gambiarra de JSON dentro de coluna).
- **Alternativa mais "correta" a longo prazo:** reescrever cada função
  de `tarefas.py`/`menus.py` para fazer `INSERT`/`UPDATE`/`DELETE`
  pontuais no banco (sem recarregar e regravar tudo a cada ação).
  Mais eficiente, mas exige tocar em bem mais arquivos.

Para um projeto do porte do Atípica (poucos usuários, uso local), a
diferença de performance entre as duas é irrelevante, e a primeira
te dá o MySQL "de verdade" gastando muito menos esforço de reescrita.
Se depois você quiser evoluir para updates pontuais, me chama que a
gente refatora função por função.

## Observação de segurança

O projeto já guarda a senha como hash SHA-256 (não em texto puro) —
isso não muda com a migração. Vale como boa prática igual antes.
