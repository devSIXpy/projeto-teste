# CLAUDE.md — Zion

## Arquitetura

```
core/
  main.py      — Loop de entrada/saída no terminal
  cerebro.py   — Orquestrador: monta contexto, chama Ollama, humaniza resposta
  memoria.py   — Persistência SQLite (conversas + conhecimentos chave/valor)
  acoes.py     — Ações no sistema operacional (navegador, pastas, pesquisa)
data/
  memoria.db   — Banco SQLite (não versionar — está no .gitignore)
src/
  teste.py     — Rascunhos e experimentos
```

---

## Modelo de Linguagem

- **Plataforma:** Ollama (local, sem internet)
- **Modelo atual:** `llama3.2:3b`
- **Idioma:** sempre português. Qualquer mudança de idioma será combinada explicitamente.

---

## Modelo de Segurança (Regra Central)

Toda ação que modifica o sistema exige confirmação do usuário antes de executar. Isso é inegociável e deve estar presente em qualquer nova ação adicionada ao projeto.

| Tipo                | Exemplos                                  | Permissão                 |
|---------------------|-------------------------------------------|---------------------------|
| Leitura             | Listar arquivos, ler conteúdo             | Automática                |
| Abertura            | Abrir navegador, pasta, app               | Automática                |
| Busca               | Pesquisa Google, busca local              | Automática                |
| Modificação leve    | Criar arquivo, mover pasta                | Confirmar antes           |
| Modificação crítica | Deletar, instalar, alterar configurações  | Confirmar com aviso claro |

---

## Segurança de Input

Input do usuário nunca deve ser interpolado em comandos shell.

```python
# Correto
subprocess.run(['xdg-open', caminho])

# Proibido
subprocess.run(f'xdg-open {caminho}', shell=True)
```

Usar sempre `subprocess` com lista de argumentos, nunca string com `shell=True`.

---

## Regras de Desenvolvimento

- Nunca executar ações modificadoras sem passar por `_solicitar_permissao()` primeiro
- Novas ações em `acoes.py` sempre recebem um tipo (`leitura`, `modificacao`, `critica`) para o sistema de permissão saber como agir
- `Cerebro` não acessa o sistema de arquivos diretamente — toda ação vai por `acoes.py`
- Contexto passado ao Ollama: máximo 5 conversas recentes + conhecimentos relevantes
- Respostas do modelo passam sempre por `_humanizar_resposta()` antes de chegar ao usuário

---

## Padrões de Código Python

- Python 3.10+, tipagem explícita em toda função nova
- `snake_case` para tudo — sem abreviações ambíguas
- Funções pequenas com responsabilidade única
- Erros sempre capturados explicitamente — zero `except: pass`
- Zero dependências externas sem aprovação explícita do Brayan

---

## O que NÃO fazer

- Não usar APIs externas (tudo local)
- Não armazenar dados sensíveis em texto plano no banco
- Não executar comandos shell montados dinamicamente a partir do input do usuário
- Não aumentar o contexto do Ollama sem medir impacto na performance
- Não expandir o escopo de ações sem combinar com o Brayan antes
