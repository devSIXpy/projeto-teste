import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

_DB_PADRAO = Path(__file__).parent.parent / "data" / "memoria.db"


class Memoria:
    """
    Sistema de memória da IA:
    - Guarda histórico de conversas
    - Guarda conhecimentos específicos (preferências, dados do usuário, etc.)
    - Usa SQLite (arquivo .db local, leve e simples)
    """

    def __init__(self, db_path: Path | str = _DB_PADRAO) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._criar_tabelas()

    def _criar_tabelas(self) -> None:
        """
        Cria as tabelas necessárias para a memória:
        - conversas: histórico de diálogos
        - conhecimento: fatos importantes que a IA aprende
        """
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                with conn:
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
        except sqlite3.Error as e:
            print(f"[MEMÓRIA] Erro ao criar tabelas: {e}")

    # ---------------------------------------------------------
    # HISTÓRICO DE CONVERSAS
    # ---------------------------------------------------------

    def salvar_conversa(self, usuario: str, assistente: str, contexto: str = "") -> None:
        """
        Salva uma interação entre você e a IA.

        - usuario: texto que você falou/escreveu
        - assistente: texto que a IA respondeu
        - contexto: qualquer informação extra relevante (opcional)
        """
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                with conn:
                    cursor = conn.cursor()

                    timestamp = datetime.now().isoformat(timespec="seconds")

                    cursor.execute("""
                        INSERT INTO conversas (timestamp, usuario, assistente, contexto)
                        VALUES (?, ?, ?, ?)
                    """, (timestamp, usuario, assistente, contexto))
        except sqlite3.Error as e:
            print(f"[MEMÓRIA] Erro ao salvar conversa: {e}")

    def buscar_conversas_recentes(self, limite: int = 5) -> list[tuple[str, str]]:
        """
        Retorna as últimas N conversas (por padrão 5), em ordem cronológica.

        Retorno: lista de tuplas (usuario, assistente)
        """
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                with conn:
                    cursor = conn.cursor()

                    cursor.execute("""
                        SELECT usuario, assistente
                        FROM conversas
                        ORDER BY id DESC
                        LIMIT ?
                    """, (limite,))

                    resultados = cursor.fetchall()

            # fetchall retorna do mais recente para o mais antigo.
            # Vamos inverter para ficar na ordem em que aconteceram.
            return list(reversed(resultados))
        except sqlite3.Error as e:
            print(f"[MEMÓRIA] Erro ao buscar conversas recentes: {e}")
            return []

    # ---------------------------------------------------------
    # CONHECIMENTO (MEMÓRIA DE LONGO PRAZO)
    # ---------------------------------------------------------

    def aprender(self, chave: str, valor: str) -> None:
        """
        Salva ou atualiza um conhecimento específico.

        Exemplos de chave:
        - 'nome_usuario'
        - 'gosta_de_musica'
        - 'horario_preferido_estudo'

        Se a chave já existir, o valor é atualizado.
        """
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                with conn:
                    cursor = conn.cursor()

                    timestamp = datetime.now().isoformat(timespec="seconds")

                    cursor.execute("""
                        INSERT INTO conhecimento (chave, valor, timestamp)
                        VALUES (?, ?, ?)
                        ON CONFLICT(chave) DO UPDATE SET
                            valor = excluded.valor,
                            timestamp = excluded.timestamp
                    """, (chave, valor, timestamp))
        except sqlite3.Error as e:
            print(f"[MEMÓRIA] Erro ao aprender '{chave}': {e}")

    def lembrar(self, chave: str) -> str | None:
        """
        Recupera o valor associado a uma chave de conhecimento.

        Retorno:
        - valor (string), se existir
        - None, se não existir
        """
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                with conn:
                    cursor = conn.cursor()

                    cursor.execute("""
                        SELECT valor FROM conhecimento
                        WHERE chave = ?
                    """, (chave,))

                    resultado = cursor.fetchone()

            if resultado:
                return resultado[0]
            return None
        except sqlite3.Error as e:
            print(f"[MEMÓRIA] Erro ao lembrar '{chave}': {e}")
            return None

    def listar_conhecimentos(self) -> list[dict[str, str]]:
        """
        Lista tudo o que a IA já "aprendeu" (todas as chaves/valores).
        Útil para depuração e curiosidade.

        Retorno: lista de dicionários
        """
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                with conn:
                    cursor = conn.cursor()

                    cursor.execute("""
                        SELECT chave, valor, timestamp
                        FROM conhecimento
                        ORDER BY id DESC
                    """)

                    linhas = cursor.fetchall()

            return [
                {"chave": chave, "valor": valor, "timestamp": timestamp}
                for (chave, valor, timestamp) in linhas
            ]
        except sqlite3.Error as e:
            print(f"[MEMÓRIA] Erro ao listar conhecimentos: {e}")
            return []

    def esquecer(self, chave: str) -> None:
        """Remove um conhecimento do banco pelo nome da chave."""
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                with conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        DELETE FROM conhecimento WHERE chave = ?
                    """, (chave,))
        except sqlite3.Error as e:
            print(f"[MEMÓRIA] Erro ao esquecer '{chave}': {e}")

    def limpar_conversas_antigas(self, manter: int = 100) -> None:
        """Mantém apenas as últimas N conversas, deletando as mais antigas."""
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                with conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        DELETE FROM conversas
                        WHERE id NOT IN (
                            SELECT id FROM conversas
                            ORDER BY id DESC
                            LIMIT ?
                        )
                    """, (manter,))
        except sqlite3.Error as e:
            print(f"[MEMÓRIA] Erro ao limpar conversas antigas: {e}")
