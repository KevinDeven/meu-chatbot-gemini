# Chatbot de orientação inicial em saúde (protótipo de TCC)

## Arquivos
| Arquivo | Função |
|---|---|
| `regras_urgencia.py` | Regras de alerta em código (sem IA). Rodam antes do modelo. |
| `prompt_sistema.py` | Prompt do sistema (versionado). |
| `app.py` | Interface web (Streamlit) que junta regras + IA (Google Gemini). |
| `testar_regras.py` | Testes das regras de urgência. |
| `.gitignore` | Impede subir a chave e arquivos temporários para o GitHub. |

## 1. Instalar
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python testar_regras.py          # confere as regras (não precisa de chave)
```

## 2. Colocar a chave da API (escolha UMA forma)

**Forma A: arquivo de segredos (mais fácil, funciona em qualquer sistema)**
1. Crie a pasta `.streamlit` dentro da pasta do projeto.
2. Dentro dela, crie o arquivo `secrets.toml` com este conteúdo (troque pela sua chave):
```toml
GEMINI_API_KEY = "COLE_SUA_CHAVE_AQUI"
```

**Forma B: variável de ambiente**
```bash
export GEMINI_API_KEY="COLE_SUA_CHAVE_AQUI"      # Windows (PowerShell): $env:GEMINI_API_KEY="COLE_SUA_CHAVE_AQUI"
```

Nunca escreva a chave dentro do `app.py`, nunca envie para o GitHub e nunca cole em chats ou prints.

## 3. Escolher o modelo
No `app.py`, a linha `MODELO = os.getenv("MODELO_LLM", "gemini-2.5-flash")` define o modelo.
Os nomes mudam com o tempo e nem todo modelo é gratuito: abra o Google AI Studio, escolha um modelo
disponível no plano gratuito e copie o nome exato. Se aparecer "Modelo não encontrado", é este ponto.
Para trocar sem editar o código: `export MODELO_LLM="nome-do-modelo"`.

## 4. Rodar
```bash
streamlit run app.py
```

## 5. Publicar com link (opcional)
1. Suba a pasta para um repositório no GitHub (o `.gitignore` já protege a chave).
2. Em um serviço de hospedagem de apps Streamlit (ex.: Streamlit Community Cloud), conecte o repositório e cadastre `GEMINI_API_KEY` em *Secrets*.
3. Teste o link no celular antes de divulgar.

## Problemas comuns
| Mensagem | Causa provável |
|---|---|
| "Configuração pendente: chave da API não encontrada" | Chave não configurada (passo 2) ou arquivo no lugar errado. |
| "Modelo não encontrado" | Nome do modelo desatualizado (passo 3). |
| "Limite gratuito de uso atingido" | Muitas requisições em pouco tempo; aguarde 1 minuto. |
| "Não consegui gerar uma resposta" | Resposta bloqueada ou vazia; reformule a mensagem. |

## Limitações (cite no artigo)
- No plano gratuito, o conteúdo enviado pode ser usado pelo Google para melhorar seus produtos; use apenas **cenários fictícios** e informe isso no TCLE.
- Limites de uso do plano gratuito podem deixar o chatbot lento ou indisponível com muitos acessos simultâneos.
- As regras usam padrões de texto: podem errar com gírias, erros de digitação ou frases ambíguas. A negação é tratada de forma simples.
- A lista de sinais de alerta deve ser **revisada por um profissional de saúde** e referenciada em protocolo reconhecido.
- O modelo de IA pode errar; por isso a urgência grave é decidida por regra fixa.
- O app **não grava conversas**.
- Registre o modelo usado, a versão do prompt (`VERSAO_PROMPT`) e das regras a cada mudança.
