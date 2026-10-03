import os
import time

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')


def exibir_cabecalho(titulo: str):
    limpar_tela()
    print("=" * 60)
    print(f"{titulo.center(60)}")
    print("=" * 60 + "\n")


def temporizador(minutos: int, titulo: str = ""):
    """
    RF07 RN03 / RF04 RN05 — Temporizador visual no terminal.
    Exibe contagem regressiva segundo a segundo.
    """
    total_seg = minutos * 60
    label = f"  ⏱  {titulo} — " if titulo else "  ⏱  "
    print(f"\n{label}Temporizador iniciado: {minutos} minuto(s)")
    print("  Pressione Ctrl+C para interromper.\n")
    try:
        for restante in range(total_seg, 0, -1):
            mins, segs = divmod(restante, 60)
            print(f"\r  Tempo restante: {mins:02d}:{segs:02d}  ", end="", flush=True)
            time.sleep(1)
        print("\r  ✅ Tempo concluído!                    ")
    except KeyboardInterrupt:
        print("\r  ⏹  Temporizador interrompido.           ")


def exibir_alerta(mensagem: str, tipo: str = "visual"):
    """
    RF06 RN01 / RF09 RN02 — exibe alerta adaptado à preferência do usuário.
    tipo: "visual" | "sonoro" | "ambos"
    """
    if tipo in ("sonoro", "ambos"):
        print("\a", end="", flush=True)   # beep do terminal
    if tipo in ("visual", "ambos"):
        print("\n" + "!" * 60)
        print(f"  🔔 LEMBRETE: {mensagem}")
        print("!" * 60 + "\n")
    else:
        print(f"\n  🔔 {mensagem}\n")


def input_obrigatorio(prompt: str) -> str:
    """Solicita entrada e não aceita string vazia."""
    while True:
        valor = input(prompt).strip()
        if valor:
            return valor
        print("  ⚠  Campo obrigatório. Tente novamente.")


def confirmar(pergunta: str) -> bool:
    return input(f"{pergunta} (s/n): ").strip().lower() == "s"
