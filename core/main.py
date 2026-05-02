from core.memoria import Memoria
from core.cerebro import Cerebro


def main() -> None:
    print("Iniciando Zion (llama3.2:3b)...\n")

    memoria = Memoria()
    cerebro = Cerebro(memoria)

    while True:
        try:
            entrada = input("Você: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nEncerrando. Até mais!")
            break

        if not entrada:
            continue

        if entrada.lower() in {"sair", "exit", "quit"}:
            print("Encerrando. Até mais!")
            break

        try:
            resposta = cerebro.processar(entrada)
        except Exception as e:
            print(f"\n[ERRO] Algo deu errado nessa resposta: {e}\n")
            continue

        print(f"\nZion: {resposta}\n")


if __name__ == "__main__":
    main()
