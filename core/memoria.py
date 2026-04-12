import sqlite3
from datetime import datetime
import os

class Memoria:
    """
    Sistema de memória da IA:
    - Guarda histórico de conversas
    - Guarda conhecimentos específicos (preferências, dados do usuário, etc.)
    - Usa SQLite (arquivo .db local, leve e simples)
    """

    def __init__(self, db_path="data/memoria.db"):
        # Caminho do arquivo do banco de dados
        self.db_path = db_path
        # Garante que a pasta 'data' exista
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        # Cria as tabelas, se ainda não existirem
        self._criar_tabelas()

    def _conectar(self):
        """
        Cria e retorna uma conexão com o banco de dados.
        Cada chamada abre e depois vamos fechar (boa prática).
        """
        return sqlite3.connect(self.db_path)

    def _criar_tabelas(self):
        """
        Cria as tabelas necessárias para a memória:
        - conversas: histórico de diálogos
        - conhecimento: fatos importantes que a IA aprende
        """
        conn = self._conectar()
        cursor = conn.cursor()

        # Tabela de conversas (histórico)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                usuario TEXT,
                assistente TEXT,
                contexto TEXT
            )
        """)

        # Tabela de conhecimento (fatos que a IA deve lembrar)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conhecimento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chave TEXT UNIQUE,
                valor TEXT,
                timestamp TEXT
            )
        """)

        conn.commit()
        conn.close()

    # ---------------------------------------------------------
    # HISTÓRICO DE CONVERSAS
    # ---------------------------------------------------------

    def salvar_conversa(self, usuario, assistente, contexto=""):
        """
        Salva uma interação entre você e a IA.

        - usuario: texto que você falou/escreveu
        - assistente: texto que a IA respondeu
        - contexto: qualquer informação extra relevante (opcional)
        """
        conn = self._conectar()
        cursor = conn.cursor()

        timestamp = datetime.now().isoformat(timespec="seconds")

        cursor.execute("""
            INSERT INTO conversas (timestamp, usuario, assistente, contexto)
            VALUES (?, ?, ?, ?)
        """, (timestamp, usuario, assistente, contexto))

        conn.commit()
        conn.close()

    def buscar_conversas_recentes(self, limite=5):
        """
        Retorna as últimas N conversas (por padrão 5), em ordem cronológica.

        Retorno: lista de tuplas (usuario, assistente)
        """
        conn = self._conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT usuario, assistente
            FROM conversas
            ORDER BY id DESC
            LIMIT ?
        """, (limite,))

        resultados = cursor.fetchall()
        conn.close()

        # fetchall retorna do mais recente para o mais antigo.
        # Vamos inverter para ficar na ordem em que aconteceram.
        return list(reversed(resultados))

    # ---------------------------------------------------------
    # CONHECIMENTO (MEMÓRIA DE LONGO PRAZO)
    # ---------------------------------------------------------

    def aprender(self, chave, valor):
        """
        Salva ou atualiza um conhecimento específico.

        Exemplos de chave:
        - 'nome_usuario'
        - 'gosta_de_musica'
        - 'horario_preferido_estudo'

        Se a chave já existir, o valor é atualizado.
        """
        conn = self._conectar()
        cursor = conn.cursor()

        timestamp = datetime.now().isoformat(timespec="seconds")

        cursor.execute("""
            INSERT INTO conhecimento (chave, valor, timestamp)
            VALUES (?, ?, ?)
            ON CONFLICT(chave) DO UPDATE SET
                valor = excluded.valor,
                timestamp = excluded.timestamp
        """, (chave, valor, timestamp))

        conn.commit()
        conn.close()

    def lembrar(self, chave):
        """
        Recupera o valor associado a uma chave de conhecimento.

        Retorno:
        - valor (string), se existir
        - None, se não existir
        """
        conn = self._conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT valor FROM conhecimento
            WHERE chave = ?
        """, (chave,))

        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            return resultado[0]
        return None

    def listar_conhecimentos(self):
        """
        Lista tudo o que a IA já "aprendeu" (todas as chaves/valores).
        Útil para depuração e curiosidade.

        Retorno: lista de dicionários
        """
        conn = self._conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT chave, valor, timestamp
            FROM conhecimento
            ORDER BY id DESC
        """)

        linhas = cursor.fetchall()
        conn.close()

        return [
            {"chave": chave, "valor": valor, "timestamp": timestamp}
            for (chave, valor, timestamp) in linhas
        ]
