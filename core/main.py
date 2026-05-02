import sys
import os
import time

# Garante que o Python encontre a pasta src mesmo quando rodarmos fora dela
sys.path.insert(0, os.path.expanduser("~/testesnaAlura"))

from core.memoria import Memoria
from core.cerebro import Cerebro

def __init__(self, db_path="data/memoria.db"):
    self.db_path = db_path
    os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

def main():
    print("Iniciando Zion...\n")

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