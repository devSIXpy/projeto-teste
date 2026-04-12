import os
import shutil
import subprocess
import shlex
from pathlib import Path

# ---------------------------------------------------------
# UTILIDADES GERAIS
# ---------------------------------------------------------

def _executar_comando(comando: str) -> bool:
    """
    Executa um comando no shell de forma segura.
    Retorna True se o comando terminou com código 0, False caso contrário.
    """
    try:
        # shlex.split garante que espaços e aspas sejam tratados corretamente
        subprocess.run(shlex.split(comando), check=True)
        return True
    except FileNotFoundError:
        print(f"[AÇÃO] Programa não encontrado: {comando}")
    except subprocess.CalledProcessError as e:
        print(f"[AÇÃO] Erro ao executar '{comando}': {e}")
    except Exception as e:
        print(f"[AÇÃO] Exceção inesperada: {e}")
    return False


# ---------------------------------------------------------
# AÇÕES DE SISTEMA
# ---------------------------------------------------------

def abrir_navegador(url: str = "https://www.google.com") -> bool:
    """
    Abre o navegador padrão (Chrome ou Firefox) apontando para a URL informada.
    Se nenhum dos dois estiver instalado, tenta usar `xdg-open` (padrão do Linux).
    """
    # Abir navegador
    for navegador in ["firefox", "chromium-browser", "google-chrome"]:
        if shutil.which(navegador):
            return _executar_comando(f"{navegador} {shlex.quote(url)}")
    # Fallback genérico (abre com o aplicativo padrão do sistema)
    return _executar_comando(f"xdg-open {shlex.quote(url)}")


def pesquisar_google(consulta: str) -> bool:
    """
    Monta a URL de busca do Google e abre no navegador.
    Exemplo: consulta = "youtube" → https://www.google.com/search?q=youtube
    """
    from urllib.parse import quote_plus
    url = f"https://www.google.com/search?q={quote_plus(consulta)}"
    return abrir_navegador(url)


def abrir_pasta(caminho: str) -> bool:
    """
    Abre a pasta indicada no gerenciador de arquivos padrão.
    - Se for caminho relativo, resolve a partir do diretório HOME.
    - Usa `xdg-open` (funciona na maioria das distros Linux).
    """
    # Resolve ~ e caminhos relativos
    caminho_resolvido = os.path.expanduser(caminho)
    caminho_resolvido = os.path.abspath(caminho_resolvido)

    if not Path(caminho_resolvido).is_dir():
        print(f"[AÇÃO] Não é uma pasta válida: {caminho_resolvido}")
        return False

    return _executar_comando(f"xdg-open {shlex.quote(caminho_resolvido)}")