import os
import subprocess
import shlex
from core.memoria import Memoria
from core import acoes


class Cerebro:

    def __init__(self, memoria: Memoria):
        self.memoria = memoria
        self.modelo_ollama = "llama3.2:3b"

        self.prompt_sistema = (
            "Você é Jarvis, assistente pessoal do Brayan. "
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

        if self._executar_comando_sistema(entrada_usuario):
            self.memoria.salvar_conversa(
                usuario=entrada_usuario,
                assistente="[COMANDO DE SISTEMA EXECUTADO]",
                contexto=contexto_geral
            )
            return "Comando executado."

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

    def _montar_contexto_conversas(self, conversas: list) -> str:
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
                timeout=60,
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
        texto = texto.replace("# ", "")
        texto = texto.replace("## ", "")
        texto = texto.replace("### ", "")
        texto = texto.replace("`", "")

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

    def _verificar_aprendizado(self, entrada_usuario: str):
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
                    chave = f"fato_{len(trecho)}"
                    self.memoria.aprender(chave, trecho)
                    print(f"[MEMÓRIA] Fato salvo: {trecho}")

                break

    # ---------------------------------------------------------
    # DETECÇÃO DE COMANDOS DE SISTEMA
    # ---------------------------------------------------------

    def _executar_comando_sistema(self, texto: str) -> bool:
        txt = texto.lower().strip()

        gatilhos_navegador = [
            "abrir navegador", "abrir o navegador", "abre o navegador",
            "abre navegador", "abra o navegador", "abrir firefox",
            "abre o firefox", "abrir chrome", "abre o chrome",
            "abrir browser", "abra o browser",
        ]

        gatilhos_pesquisa = [
            "pesquisar", "pesquisa", "buscar", "busca",
            "procurar", "procura", "pesquise", "busque",
        ]

        indicadores_google = [
            "no google", "pelo google", "no navegador",
            "na internet", "na web",
        ]

        gatilhos_pasta = [
            "abrir pasta", "abrir a pasta", "abre a pasta",
            "abre pasta", "abra a pasta", "abrir diretório",
            "abre o diretório", "mostrar pasta", "mostrar a pasta",
        ]

        pastas_conhecidas = {
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

        tem_gatilho_pesquisa = any(g in txt for g in gatilhos_pesquisa)

        if tem_gatilho_pesquisa:
            termo = txt

            for g in gatilhos_pesquisa:
                if termo.startswith(g):
                    termo = termo[len(g):].strip()
                    break
                if g in termo:
                    termo = termo.split(g, 1)[1].strip()
                    break

            for ind in indicadores_google:
                if termo.endswith(ind):
                    termo = termo[: -len(ind)].strip()
                    break
                if ind in termo:
                    termo = termo.replace(ind, "").strip()
                    break

            for conector in ["sobre", "por", "a respeito de", "acerca de"]:
                if termo.startswith(conector + " "):
                    termo = termo[len(conector):].strip()

            if termo:
                acoes.pesquisar_google(termo)
                print(f"[AÇÃO] Pesquisa executada: {termo}")
                return True

        if any(g in txt for g in gatilhos_navegador):
            acoes.abrir_navegador()
            print("[AÇÃO] Navegador aberto.")
            return True

        if any(g in txt for g in gatilhos_pasta):
            caminho = txt
            for g in gatilhos_pasta:
                if g in caminho:
                    caminho = caminho.split(g, 1)[1].strip()
                    break

            for artigo in ["a ", "o ", "as ", "os ", "da ", "do ", "de "]:
                if caminho.startswith(artigo):
                    caminho = caminho[len(artigo):].strip()

            if caminho in pastas_conhecidas:
                caminho = pastas_conhecidas[caminho]
            elif not caminho.startswith(("/", "~")):
                caminho = f"~/{caminho}"

            acoes.abrir_pasta(caminho)
            print(f"[AÇÃO] Pasta aberta: {caminho}")
            return True

        return False
