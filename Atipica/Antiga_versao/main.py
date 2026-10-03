from data.data_manager import carregar_dados
from ui.menus import criar_usuario_menu, login_menu, painel_principal_menu
from ui.utils import exibir_cabecalho


def executar_sistema():
    while True:
        dados = carregar_dados()
        exibir_cabecalho("ATÍPICA — ASSISTENTE PARA TEA")
        print("  1. Entrar")
        print("  2. Criar novo perfil")
        print("  3. Encerrar")

        opcao = input("\n  Escolha uma opção: ").strip()

        if opcao == "1":
            if not dados:
                input("\n  Nenhum perfil cadastrado. Crie um primeiro! (Enter)")
                continue
            usuario = login_menu(dados)
            if usuario:
                dados = carregar_dados()   # recarrega após login
                painel_principal_menu(dados, usuario)

        elif opcao == "2":
            criar_usuario_menu(dados)

        elif opcao == "3":
            print("\n  Até logo! 👋")
            break


if __name__ == "__main__":
    executar_sistema()
