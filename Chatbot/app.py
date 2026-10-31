"""Chatbot de orientação inicial em saúde (protótipo acadêmico).

Executar:  streamlit run app.py
Fluxo:     mensagem -> regras de urgência (código) -> se não houver alerta -> IA (Google Gemini)
"""

import os
import re
import time

import streamlit as st
from google import genai
from google.genai import types

from prompt_sistema import SYSTEM_PROMPT, VERSAO_PROMPT
from regras_urgencia import avaliar_urgencia

# Copie o nome EXATO de um modelo gratuito na tela do Google AI Studio.
# Para trocar sem mexer no código: variável de ambiente MODELO_LLM.
MODELO = os.getenv("MODELO_LLM", "gemini-3.6-flash")
MAX_MENSAGENS_USUARIO = 12
TENTATIVAS = 3  # tentativas automáticas se o servidor do Google estiver instável
PADRAO_NIVEL = re.compile(r"\[\[NIVEL:\s*([1-4])\s*\]\]")
ROTULOS = {
    1: "Nível 1: autocuidado e observação",
    2: "Nível 2: marcar consulta nos próximos dias",
    3: "Nível 3: procurar atendimento hoje",
    4: "Nível 4: emergência (SAMU 192)",
}

st.set_page_config(page_title="Orientação inicial em saúde", page_icon="🩺")


@st.cache_resource
def obter_cliente() -> genai.Client | None:
    """Lê a chave de: variável de ambiente ou .streamlit/secrets.toml."""
    chave = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not chave:
        try:
            chave = st.secrets["GEMINI_API_KEY"]
        except Exception:
            chave = None
    return genai.Client(api_key=chave) if chave else None


def perguntar_ia(historico: list[dict]) -> tuple[str, int | None]:
    cliente = obter_cliente()
    if cliente is None:
        return "Configuração pendente: chave da API não encontrada.", None

    conteudo = [
        types.Content(
            role="user" if m["role"] == "user" else "model",
            parts=[types.Part(text=m["content"])],
        )
        for m in historico
    ]
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        temperature=0.2,         # baixo = respostas mais estáveis (útil para avaliação)
        max_output_tokens=2048,  # folga: alguns modelos gastam tokens "pensando"
    )

    texto = ""
    for tentativa in range(1, TENTATIVAS + 1):
        try:
            resp = cliente.models.generate_content(model=MODELO, contents=conteudo, config=config)
            texto = resp.text or ""
            break
        except Exception as erro:  # rede, chave inválida, limite de uso, servidor instável...
            detalhe = str(erro)
            codigo = getattr(erro, "code", None)
            instavel = (isinstance(codigo, int) and codigo >= 500) or "UNAVAILABLE" in detalhe or "overloaded" in detalhe

            if codigo == 429 or "RESOURCE_EXHAUSTED" in detalhe:
                return "O limite gratuito de uso foi atingido agora. Aguarde um minuto e tente de novo.", None
            if codigo == 404 or "NOT_FOUND" in detalhe:
                return "Modelo não encontrado. Confira o ID do modelo (MODELO_LLM) no Google AI Studio.", None
            if "API_KEY_INVALID" in detalhe or "PERMISSION_DENIED" in detalhe or "UNAUTHENTICATED" in detalhe:
                return "A chave da API foi recusada. Confira se foi copiada completa e se está ativa no Google AI Studio.", None
            if instavel and tentativa < TENTATIVAS:
                time.sleep(2 * tentativa)  # espera 2s, depois 4s, e tenta de novo
                continue
            if instavel:
                return (
                    "O serviço de IA do Google está instável ou sobrecarregado agora. "
                    "Aguarde alguns instantes e tente de novo. Se persistir, teste outro modelo (MODELO_LLM)."
                ), None
            return f"Não consegui responder agora. (detalhe técnico: {type(erro).__name__}: {detalhe[:300]})", None

    if not texto.strip():
        return "Não consegui gerar uma resposta. Tente descrever a situação de outra forma.", None
    achado = PADRAO_NIVEL.search(texto)
    nivel = int(achado.group(1)) if achado else None
    return PADRAO_NIVEL.sub("", texto).strip(), nivel


def mostrar_nivel(nivel: int | None) -> None:
    if nivel is None:
        return
    {1: st.success, 2: st.info, 3: st.warning, 4: st.error}[nivel](ROTULOS[nivel])


# ---------- Interface ----------
st.title("🩺 Orientação inicial em saúde")
st.caption(
    "Protótipo acadêmico de pesquisa (TCC). **Não faz diagnóstico, não indica medicamentos e "
    "não substitui atendimento médico.** Em emergência, ligue **192 (SAMU)**. "
    "Não informe dados pessoais nem seus sintomas reais: use apenas a situação fictícia proposta. "
    "As mensagens são processadas por um serviço de IA de terceiros (Google)."
)

with st.sidebar:
    st.markdown(f"**Versão do prompt:** {VERSAO_PROMPT}")
    st.markdown(f"**Modelo:** {MODELO}")
    if st.button("Nova conversa"):
        st.session_state.mensagens = []
        st.rerun()

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

for m in st.session_state.mensagens:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        mostrar_nivel(m.get("nivel"))

entrada = st.chat_input("Descreva a situação (fictícia)...")

if entrada:
    st.session_state.mensagens.append({"role": "user", "content": entrada})
    with st.chat_message("user"):
        st.markdown(entrada)

    falas_usuario = [m["content"] for m in st.session_state.mensagens if m["role"] == "user"]

    with st.chat_message("assistant"):
        if len(falas_usuario) > MAX_MENSAGENS_USUARIO:
            resposta, nivel = "Esta conversa ficou longa. Clique em **Nova conversa** para recomeçar.", None
        elif (alerta := avaliar_urgencia(falas_usuario)) is not None:
            resposta, nivel = alerta.mensagem, alerta.nivel  # regra fixa, sem IA
        else:
            with st.spinner("Pensando..."):
                resposta, nivel = perguntar_ia(st.session_state.mensagens)
        st.markdown(resposta)
        mostrar_nivel(nivel)

    st.session_state.mensagens.append({"role": "assistant", "content": resposta, "nivel": nivel})
