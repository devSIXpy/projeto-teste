# Zion — Assistente Pessoal Local

Zion (pronuncia-se "zaion") é um assistente pessoal de linha de comando rodando 100% localmente no Linux. Usa Ollama como motor de linguagem e SQLite para memória persistente. Toda interação é por texto no terminal.

**Princípios do projeto:**
- Leveza: sem dependências pesadas, sem serviços em nuvem
- Segurança: nenhuma ação modificadora ocorre sem confirmação explícita do usuário
- Performance: contexto enxuto, respostas rápidas, sem processamento desnecessário
- Confiabilidade: falhas silenciosas e recuperáveis — o loop principal nunca trava

---

## Modelo de Linguagem

- **Modelo atual:** `llama3.2:3b` — leve, roda bem em hardware comum
- **Modelos alternativos testados:**
  - `phi3.5:mini` — mais preciso, tamanho similar
  - `gemma2:2b` — mais leve, bom em português
- Para trocar o modelo: alterar `self.modelo_ollama` em `core/cerebro.py`

---

## Escopo

**Agora (estável):**
- Abrir pastas e navegador
- Pesquisa no Google
- Memória de conversas e preferências do usuário

**Futuro (quando houver confiança suficiente no sistema):**
- Controle de aplicativos específicos (ex: VS Code, Spotify)
- Ações online (redes sociais, e-mail, etc.)
- Qualquer expansão só ocorre após o Brayan sentir segurança no comportamento do Zion

---

## Comandos

```bash
# Rodar o assistente
python -m core.main

# Verificar modelos disponíveis no Ollama
ollama list
```

---

## Debug

```bash
# Ver memória salva
sqlite3 data/memoria.db "SELECT * FROM conhecimento;"

# Ver histórico de conversas
sqlite3 data/memoria.db "SELECT timestamp, usuario, assistente FROM conversas ORDER BY id DESC LIMIT 10;"
```
