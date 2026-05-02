import sys
import os

# Garante que o Python encontre a pasta src mesmo quando rodarmos fora dela
sys.path.insert(0, os.path.expanduser("~/testesnaAlura"))

from core.memoria import Memoria
from core.cerebro import Cerebro

def main():
    print("Iniciando Zion...\n")

    os.makedirs("data", exist_ok=True)
    memoria = Memoria(db_path="data/memoria.db")
    cerebro = Cerebro(memoria)

    while True:
        entrada = input("Você: ").strip()

        if not entrada:
            continue

        if entrada.lower() in {"sair", "exit", "quit"}:
            print("Encerrando. Até mais!")
            break

        resposta = cerebro.processar(entrada)
        print(f"\nIA: {resposta}\n")

if __name__ == "__main__":
    main()