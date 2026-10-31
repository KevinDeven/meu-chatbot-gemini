"""Diagnóstico da API do Google: descobre quais modelos respondem com a sua chave.

Uso (dentro da pasta do projeto, com o ambiente ativado):
    python testar_api.py                 -> lista e testa modelos "flash" disponíveis
    python testar_api.py NOME1 NOME2     -> testa só os modelos informados

A chave é lida da variável GEMINI_API_KEY ou de .streamlit/secrets.toml.
O script NUNCA exibe a chave.
"""

import os
import re
import sys
import time

from google import genai

MAX_TESTES = 8
IGNORAR = ("image", "tts", "audio", "live", "native", "embedding", "robotics", "computer", "vision")


def ler_chave() -> str | None:
    chave = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if chave:
        return chave
    caminho = os.path.join(".streamlit", "secrets.toml")
    if os.path.exists(caminho):
        with open(caminho, encoding="utf-8") as f:
            achado = re.search(r'GEMINI_API_KEY\s*=\s*"([^"]+)"', f.read())
            if achado:
                return achado.group(1)
    return None


def descobrir_modelos(cliente: genai.Client) -> list[str]:
    nomes = []
    for m in cliente.models.list():
        nome = (m.name or "").replace("models/", "")
        acoes = getattr(m, "supported_actions", None) or []
        if "generateContent" in acoes and "flash" in nome and not any(x in nome for x in IGNORAR):
            nomes.append(nome)
    return sorted(nomes)


def main() -> None:
    chave = ler_chave()
    if not chave:
        print("Chave não encontrada. Configure GEMINI_API_KEY (ver README.txt, passo 2).")
        return
    cliente = genai.Client(api_key=chave)

    if len(sys.argv) > 1:
        candidatos = [n.replace("models/", "") for n in sys.argv[1:]]
    else:
        try:
            candidatos = descobrir_modelos(cliente)
        except Exception as erro:
            print(f"Não consegui listar os modelos: {type(erro).__name__}: {str(erro)[:300]}")
            return
        print(f"Modelos 'flash' disponíveis para a sua chave ({len(candidatos)}):")
        for n in candidatos:
            print(f"  - {n}")
        print()

    funcionam = []
    for nome in candidatos[:MAX_TESTES]:
        try:
            resp = cliente.models.generate_content(model=nome, contents="Responda apenas com a palavra: ok")
            texto = (resp.text or "").strip()[:30]
            print(f"[OK]     {nome}  (resposta: {texto!r})")
            funcionam.append(nome)
        except Exception as erro:
            codigo = getattr(erro, "code", "?")
            print(f"[FALHOU] {nome}  (código {codigo}: {str(erro)[:120]})")
        time.sleep(2)  # evita estourar o limite por minuto do plano gratuito

    print()
    if funcionam:
        print("Copie um dos nomes marcados [OK] para a linha MODELO do app.py.")
    else:
        print("Nenhum modelo respondeu agora. Aguarde alguns minutos e rode de novo;")
        print("se persistir, confira se a chave está ativa no Google AI Studio.")


if __name__ == "__main__":
    main()
