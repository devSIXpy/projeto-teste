import time
import subprocess
from core.memoria import Memoria
from core import acoes


class Cerebro:

    def __init__(self, memoria: Memoria):
        self.memoria = memoria
        self.modelo_ollama = "llama3.2:3b"

        self.prompt_sistema = (
            "Você é Zion (pronuncia-se 'zaion'), assistente pessoal do Brayan. "
            "Sua personalidade é calorosa, curiosa e natural. "
            "Aqui estão suas diretrizes de comportamento:\n\n"

            "TOM DE VOZ:\n"
            "- Fale como uma pessoa real, não como um manual\n"
            "- Use contrações naturais do português: "
            "'tá', 'pra', 'tô', 'né', 'então'\n"
            "- Misture frases curtas com frases um pouco mais longas\n"
            "- Às vezes comece com: 'Ah', 'Olha', 'Então', 'Deixa eu ver'\n\n"

            "ESTRUTURA DAS RESPOSTAS:\n"
            "- Comece sempre com uma reação humana ao que foi dito\n"
            "- Explique de forma simples, como se fosse uma conversa\n"
            "- Quando possível, termine com uma pergunta ou curiosidade\n"
            "- Respostas curtas para perguntas simples\n"
            "- Respostas um pouco mais elaboradas para perguntas complexas\n\n"

            "MEMÓRIA E CONEXÃO:\n"
            "- O usuário ira falar os interesses dele\n"
            "- Sempre que puder, relacione a resposta com algo que ele já sabe\n"
            "- Se não souber algo, diga honestamente\n\n"

            "O QUE EVITAR:\n"
            "- Evite listas com bullet points em toda resposta\n"
            "- Evite linguagem excessivamente formal\n"
            "- Nunca comece com 'Claro!' ou 'Certamente!'\n"
            "- Não repita a pergunta do usuário antes de responder\n"
        )

    # ---------------------------------------------------------
    # MÉTODO PRINCIPAL
    # ---------------------------------------------------------

    def processar(self, entrada_usuario: str) -> str:
        entrada_usuario = (entrada_usuario or "").strip()
        if not entrada_usuario:
            return "Não entendi nada. Pode repetir?"

        conversas_recentes = self.memoria.buscar_conversas_recentes(limite=5)
        contexto_conversa = self._montar_contexto_conversas(conversas_recentes)

        nome = self.memoria.lembrar("nome_usuario") or "Brayan"
        gostos = self.memoria.lembrar("gosta_de") or "IA e aprendizado"

        contexto_conhecimento = (
            f"Informações sobre o usuário:\n"
            f"- Nome: {nome}\n"
            f"- Interesses: {gostos}\n"
        )

        contexto_geral = contexto_conversa + "\n\n" + contexto_conhecimento

        resultado_sistema = self._executar_comando_sistema(entrada_usuario)
        if resultado_sistema is not None:
            self.memoria.salvar_conversa(
                usuario=entrada_usuario,
                assistente=resultado_sistema,
                contexto=contexto_geral
            )
            return resultado_sistema

        resposta = self._processar_ollama(entrada_usuario, contexto_geral)
        resposta = resposta.strip() if resposta else (
            "Tive um problema para responder agora. Tente novamente."
        )

        resposta = self._humanizar_resposta(resposta)

        self.memoria.salvar_conversa(
            usuario=entrada_usuario,
            assistente=resposta,
            contexto=contexto_geral
        )

        self._verificar_aprendizado(entrada_usuario)

        return resposta

    # ---------------------------------------------------------
    # CONTEXTO DA MEMÓRIA
    # ---------------------------------------------------------

    def _montar_contexto_conversas(self, conversas: list[tuple[str, str]]) -> str:
        if not conversas:
            return "Não há conversas anteriores ainda."

        linhas = ["Histórico recente da conversa:"]
        for usuario, assistente in conversas:
            linhas.append(f"Usuário: {usuario}")
            linhas.append(f"Assistente: {assistente}")
        return "\n".join(linhas)

    # ---------------------------------------------------------
    # OLLAMA
    # ---------------------------------------------------------

    def _processar_ollama(self, entrada_usuario: str, contexto: str) -> str:
        prompt = (
            f"{self.prompt_sistema}\n\n"
            f"{contexto}\n\n"
            f"Usuário: {entrada_usuario}\n"
            f"Assistente:"
        )

        try:
            resultado = subprocess.run(
                [
                    "ollama", "run", self.modelo_ollama,
                ],
                input=prompt,
                text=True,
                capture_output=True,
                timeout=self._TIMEOUT_OLLAMA,
            )

            if resultado.returncode != 0:
                print(f"[ERRO] Ollama retornou código {resultado.returncode}")
                print(f"Detalhe: {resultado.stderr}")
                return "Tive um erro ao usar o modelo local."

            saida = resultado.stdout.strip()

            if not saida:
                return "O modelo não retornou nenhuma resposta."

            return saida

        except FileNotFoundError:
            return (
                "Ollama não encontrado no sistema. "
                "Precisamos instalar o Ollama antes de continuar."
            )

        except subprocess.TimeoutExpired:
            return (
                "O modelo demorou demais para responder. "
                "Tente uma pergunta mais curta ou simples."
            )

        except Exception as e:
            return f"Erro inesperado ao chamar o modelo: {e}"

    # ---------------------------------------------------------
    # HUMANIZAR RESPOSTA
    # ---------------------------------------------------------

    def _humanizar_resposta(self, texto: str) -> str:
        texto = texto.replace("**", "")
        texto = texto.replace("*", "")
        texto = texto.replace("###### ", "")
        texto = texto.replace("##### ", "")
        texto = texto.replace("#### ", "")
        texto = texto.replace("### ", "")
        texto = texto.replace("## ", "")
        texto = texto.replace("# ", "")
        texto = texto.replace("`", "")

        linhas = texto.splitlines()
        linhas = [ln[2:] if ln.startswith("- ") else ln for ln in linhas]
        linhas = [ln for ln in linhas if ln.strip() != "---"]
        texto = "\n".join(linhas)

        substituicoes = {
            "Claro!":             "Então,",
            "Certamente!":        "Com certeza,",
            "Com prazer!":        "Boa pergunta,",
            "Posso ajudar?":      "Precisando de mais alguma coisa?",
            "Como posso ajudar?": "O que mais você quer saber?",
            "É importante notar": "Vale lembrar",
            "É fundamental":      "É importante",
            "De acordo com":      "Pelo que entendo,",
            "Além disso,":        "Ah, e também:",
            "Em resumo,":         "Basicamente,",
            "Em conclusão,":      "No fim das contas,",
        }

        for expressao_robotica, versao_humana in substituicoes.items():
            texto = texto.replace(expressao_robotica, versao_humana)

        while "\n\n\n" in texto:
            texto = texto.replace("\n\n\n", "\n\n")

        texto = texto.strip()
        if texto and texto[-1] not in (".", "!", "?", "…"):
            texto += "."

        return texto

    # ---------------------------------------------------------
    # APRENDIZADO AUTOMÁTICO
    # ---------------------------------------------------------

    def _verificar_aprendizado(self, entrada_usuario: str) -> None:
        entrada_lower = entrada_usuario.lower()
        gatilhos = ["lembra que", "guarda que", "salva que", "não esqueça que"]

        for gatilho in gatilhos:
            if gatilho in entrada_lower:
                trecho = entrada_lower.split(gatilho)[-1].strip()

                if "nome" in trecho:
                    valor = trecho.replace("meu nome é", "").replace("nome é", "").strip()
                    self.memoria.aprender("nome_usuario", valor)
                    print(f"[MEMÓRIA] Nome salvo: {valor}")

                elif "gosto de" in trecho or "gosto muito de" in trecho:
                    valor = trecho.replace("eu gosto de", "").replace("gosto de", "").strip()
                    self.memoria.aprender("gosta_de", valor)
                    print(f"[MEMÓRIA] Interesse salvo: {valor}")

                else:
                    chave = f"fato_{int(time.time())}"
                    self.memoria.aprender(chave, trecho)
                    print(f"[MEMÓRIA] Fato salvo: {trecho}")

                break

    # ---------------------------------------------------------
    # DETECÇÃO DE COMANDOS DE SISTEMA
    # ---------------------------------------------------------

    _TIMEOUT_OLLAMA: int = 60

    _GATILHOS_NAVEGADOR: list[str] = [
        "abrir navegador", "abrir o navegador", "abre o navegador",
        "abre navegador", "abra o navegador", "abrir firefox",
        "abre o firefox", "abrir chrome", "abre o chrome",
        "abrir browser", "abra o browser",
    ]

    _GATILHOS_PESQUISA: list[str] = [
        "pesquisar", "pesquisa", "buscar", "busca",
        "procurar", "procura", "pesquise", "busque",
    ]

    _INDICADORES_GOOGLE: list[str] = [
        "no google", "pelo google", "no navegador",
        "na internet", "na web",
    ]

    _GATILHOS_PASTA: list[str] = [
        "abrir pasta", "abrir a pasta", "abre a pasta",
        "abre pasta", "abra a pasta", "abrir diretório",
        "abre o diretório", "mostrar pasta", "mostrar a pasta",
    ]

    _PASTAS_CONHECIDAS: dict[str, str] = {
        "documentos":       "~/Documentos",
        "downloads":        "~/Downloads",
        "imagens":          "~/Imagens",
        "área de trabalho": "~/Área de trabalho",
        "desktop":          "~/Área de trabalho",
        "música":           "~/Música",
        "musica":           "~/Música",
        "vídeos":           "~/Vídeos",
        "videos":           "~/Vídeos",
        "projeto":          "~/minha-ia",
        "minha ia":         "~/minha-ia",
    }

    def _executar_comando_sistema(self, texto: str) -> str | None:
        txt = texto.lower().strip()

        if any(g in txt for g in self._GATILHOS_PESQUISA):
            return self._tentar_pesquisa(txt)

        if any(g in txt for g in self._GATILHOS_NAVEGADOR):
            return self._tentar_navegador()

        if any(g in txt for g in self._GATILHOS_PASTA):
            return self._tentar_pasta(txt)

        return None

    def _tentar_pesquisa(self, txt: str) -> str | None:
        termo = txt

        for g in self._GATILHOS_PESQUISA:
            if termo.startswith(g):
                termo = termo[len(g):].strip()
                break
            if g in termo:
                termo = termo.split(g, 1)[1].strip()
                break

        for ind in self._INDICADORES_GOOGLE:
            if termo.endswith(ind):
                termo = termo[: -len(ind)].strip()
                break
            if ind in termo:
                termo = termo.replace(ind, "").strip()
                break

        for conector in ["sobre", "por", "a respeito de", "acerca de"]:
            if termo.startswith(conector + " "):
                termo = termo[len(conector):].strip()

        if not termo:
            return "Não entendi o que pesquisar. Pode repetir com o termo da busca?"

        if not acoes.pesquisar_google(termo):
            return None

        return f'Pesquisei "{termo}" no Google pra você.'

    def _tentar_navegador(self) -> str | None:
        if not acoes.abrir_navegador():
            return None

        return "Abri o navegador pra você."

    def _tentar_pasta(self, txt: str) -> str | None:
        caminho = txt

        for g in self._GATILHOS_PASTA:
            if g in caminho:
                caminho = caminho.split(g, 1)[1].strip()
                break

        for artigo in ["a ", "o ", "as ", "os ", "da ", "do ", "de "]:
            if caminho.startswith(artigo):
                caminho = caminho[len(artigo):].strip()

        if caminho in self._PASTAS_CONHECIDAS:
            caminho = self._PASTAS_CONHECIDAS[caminho]
        elif not caminho.startswith(("/", "~")):
            caminho = f"~/{caminho}"

        if not acoes.abrir_pasta(caminho):
            return None

        return f"Abri a pasta {caminho} pra você."
