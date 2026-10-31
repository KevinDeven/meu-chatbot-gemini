CHATBOT DE ORIENTAÇÃO INICIAL EM SAÚDE (PROTÓTIPO DE TCC)
=========================================================


ARQUIVOS DA PASTA
-----------------
regras_urgencia.py  -> Regras de alerta em código (sem IA). Rodam antes do modelo.
prompt_sistema.py   -> Prompt do sistema (versionado).
app.py              -> Interface web (Streamlit) que junta regras + IA (Google Gemini).
testar_regras.py    -> Testes das regras de urgência.
requirements.txt    -> Lista das bibliotecas necessárias.
.gitignore          -> Impede subir a chave e arquivos temporários para o GitHub.
README.txt          -> Este guia.


PASSO 1: INSTALAR
-----------------
Abra o terminal (ou prompt de comando) dentro da pasta do projeto e rode,
um comando por vez:

  python -m venv .venv

  Ativar o ambiente:
    Windows:      .venv\Scripts\activate
    Mac / Linux:  source .venv/bin/activate

  pip install -r requirements.txt

  python testar_regras.py

O último comando confere as regras de urgência e não precisa de chave.
Resultado esperado: "21/21 casos corretos".


PASSO 2: COLOCAR A CHAVE DA API (ESCOLHA UMA FORMA)
---------------------------------------------------
FORMA A: arquivo de segredos (mais fácil, funciona em qualquer sistema)

  1. Dentro da pasta do projeto, crie uma pasta chamada .streamlit
  2. Dentro dela, crie um arquivo chamado secrets.toml
  3. Escreva nele, trocando pela sua chave (mantenha as aspas):

     GEMINI_API_KEY = "COLE_SUA_CHAVE_AQUI"

FORMA B: variável de ambiente

  Windows (PowerShell):
     $env:GEMINI_API_KEY="COLE_SUA_CHAVE_AQUI"

  Mac / Linux:
     export GEMINI_API_KEY="COLE_SUA_CHAVE_AQUI"

ATENÇÃO:
  - Nunca escreva a chave dentro do app.py.
  - Nunca envie a chave para o GitHub.
  - Nunca cole a chave em chats, e-mails ou prints.
  - Se ela vazar, apague-a no Google AI Studio e crie outra.


PASSO 3: ESCOLHER O MODELO
--------------------------
No app.py existe esta linha:

  MODELO = os.getenv("MODELO_LLM", "gemini-2.5-flash")

O nome entre aspas define qual modelo de IA será usado.
Os nomes mudam com o tempo e nem todo modelo é gratuito. Por isso:

  1. Abra o Google AI Studio.
  2. Escolha um modelo disponível no plano gratuito.
  3. Copie o nome exato e cole no lugar de "gemini-2.5-flash".

Se aparecer a mensagem "Modelo não encontrado", o problema é este passo.

Para trocar sem editar o código, use a variável de ambiente MODELO_LLM
(mesmo método da Forma B do passo 2).


PASSO 4: RODAR
--------------
Com o ambiente ativado, na pasta do projeto:

  streamlit run app.py

O navegador abre sozinho. Se não abrir, acesse o endereço mostrado no
terminal (normalmente http://localhost:8501).

Teste rápido:
  - Digite "estou com tosse seca há dois dias": deve responder com a IA.
  - Digite "dor forte no peito": deve mostrar o alerta fixo do SAMU (192),
    sem usar a IA.


PASSO 5: PUBLICAR COM LINK (OPCIONAL)
-------------------------------------
  1. Suba a pasta para um repositório no GitHub (o .gitignore já protege
     a chave).
  2. Em um serviço de hospedagem de apps Streamlit (por exemplo, o
     Streamlit Community Cloud), conecte o repositório e cadastre
     GEMINI_API_KEY na área de "Secrets".
  3. Teste o link no celular antes de divulgar.


PROBLEMAS COMUNS
----------------
Mensagem: "Configuração pendente: chave da API não encontrada"
  Causa: chave não configurada (passo 2) ou arquivo no lugar errado.
         Confira se a pasta se chama .streamlit (com o ponto) e se o arquivo
         se chama secrets.toml.

Mensagem: "Modelo não encontrado"
  Causa: nome do modelo desatualizado (passo 3).

Mensagem: "O limite gratuito de uso foi atingido"
  Causa: muitas requisições em pouco tempo. Aguarde 1 minuto e tente de novo.

Mensagem: "Não consegui gerar uma resposta"
  Causa: resposta bloqueada ou vazia. Reformule a mensagem.

Erro "streamlit não é reconhecido" ou "ModuleNotFoundError"
  Causa: o ambiente não está ativado ou as bibliotecas não foram instaladas.
         Repita o passo 1.


LIMITAÇÕES (CITE NO ARTIGO)
---------------------------
  - No plano gratuito, o conteúdo enviado pode ser usado pelo Google para
    melhorar seus produtos. Use apenas CENÁRIOS FICTÍCIOS e informe isso no
    TCLE.
  - Os limites do plano gratuito podem deixar o chatbot lento ou indisponível
    com muitos acessos ao mesmo tempo.
  - As regras de urgência usam padrões de texto: podem errar com gírias, erros
    de digitação ou frases ambíguas. A negação é tratada de forma simples.
  - A lista de sinais de alerta deve ser REVISADA POR UM PROFISSIONAL DE SAÚDE
    e referenciada em protocolo reconhecido.
  - O modelo de IA pode errar; por isso, a urgência grave é decidida por
    regra fixa.
  - O app NÃO grava conversas.
  - Registre o modelo usado, a versão do prompt (VERSAO_PROMPT) e das regras
    a cada mudança.
