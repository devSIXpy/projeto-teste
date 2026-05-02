import os
import shutil
import subprocess
from pathlib import Path
from urllib.parse import quote_plus


# ---------------------------------------------------------
# PERMISSÕES
# ---------------------------------------------------------

def _solicitar_permissao(tipo: str, descricao: str) -> bool:
    """
    tipo: 'leitura' | 'abertura' | 'busca' | 'modificacao' | 'critica'
    Ações automáticas retornam True sem perguntar.
    Ações modificadoras/críticas pedem confirmação ao usuário.
    """
    if tipo in ("leitura", "abertura", "busca"):
        return True

    if tipo == "critica":
        aviso = f"[!! AÇÃO CRÍTICA !!] {descricao}"
        mensagem_cancelamento = "[!! CANCELADO] Ação crítica interrompida pelo usuário."
    else:
        aviso = f"[CONFIRMAÇÃO] {descricao}"
        mensagem_cancelamento = "[CANCELADO] Ação não executada."

    resposta = input(f"{aviso}\nConfirma? (s/n): ").strip().lower()

    if resposta in ("s", "sim"):
        return True

    print(mensagem_cancelamento)
    return False


# ---------------------------------------------------------
# EXECUÇÃO SEGURA
# ---------------------------------------------------------

def _executar_comando(args: list[str]) -> bool:
    try:
        subprocess.run(args, check=True, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print(f"[AÇÃO] Programa não encontrado: {args[0]}")
        return False
    except subprocess.CalledProcessError as e:
        print(f"[AÇÃO] Erro ao executar {args[0]}: código {e.returncode}")
        return False
    except Exception as e:
        print(f"[AÇÃO] Erro inesperado ao executar {args[0]}: {e}")
        return False
    return True


# ---------------------------------------------------------
# AÇÕES DE SISTEMA
# ---------------------------------------------------------

def _abrir_url(url: str) -> bool:
    for navegador in ["firefox", "chromium-browser", "google-chrome"]:
        if shutil.which(navegador):
            return _executar_comando([navegador, url])
    return _executar_comando(["xdg-open", url])


def abrir_navegador(url: str = "https://www.google.com") -> bool:
    if not _solicitar_permissao("abertura", f"Abrir navegador em: {url}"):
        return False
    return _abrir_url(url)


def pesquisar_google(consulta: str) -> bool:
    if not _solicitar_permissao("busca", f"Pesquisar no Google: {consulta}"):
        return False
    url = f"https://www.google.com/search?q={quote_plus(consulta)}"
    return _abrir_url(url)


def abrir_pasta(caminho: str) -> bool:
    caminho_resolvido = str(Path(os.path.expanduser(caminho)).resolve())

    if not Path(caminho_resolvido).is_dir():
        print(f"[AÇÃO] Não é uma pasta válida: {caminho_resolvido}")
        return False

    if not _solicitar_permissao("abertura", f"Abrir pasta: {caminho_resolvido}"):
        return False

    return _executar_comando(["xdg-open", caminho_resolvido])
