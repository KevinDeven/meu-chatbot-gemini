"""Testes rápidos das regras de urgência: python testar_regras.py"""

from regras_urgencia import avaliar_urgencia

# (mensagens do usuário, nível esperado ou None)
CASOS = [
    (["Estou com dor forte no peito e suor frio"], 4),
    (["Tô com aperto no peito"], 4),
    (["Não consigo respirar direito"], 4),
    (["Tenho falta de ar desde ontem"], 4),
    (["Meu pai desmaiou agora há pouco"], 4),
    (["Minha mãe está com a boca torta e fala arrastada"], 4),
    (["Estou grávida e com sangramento"], 4),
    (["Às vezes penso que quero me matar"], 4),
    (["Tomei comprimidos demais"], 4),
    (["Estou vomitando sangue"], 4),
    (["Estou com febre e pescoço rígido"], 4),
    (["Estou com febre há 3 dias", "e agora começou dor forte na barriga"], 3),
    (["Estou com febre e manchas vermelhas pelo corpo"], 3),
    (["Meu bebê está com febre"], 3),
    (["Levei uma pancada na cabeça ontem"], 3),
    (["Tenho dor de cabeça leve e nariz entupido"], None),
    (["Estou com tosse seca há dois dias"], None),
    (["Estou com febre baixa e dor no corpo"], None),
    (["Não tenho falta de ar, só tosse"], None),
    (["Sem dor no peito, mas estou cansado"], None),
    (["Não aguento mais essa dor no peito"], 4),  # não deve ser tratada como negação
]


def main() -> None:
    erros = 0
    for msgs, esperado in CASOS:
        alerta = avaliar_urgencia(msgs)
        obtido = alerta.nivel if alerta else None
        ok = obtido == esperado
        erros += 0 if ok else 1
        print(f"[{'OK' if ok else 'ERRO'}] esperado={esperado} obtido={obtido} | {msgs}")
    print(f"\n{len(CASOS) - erros}/{len(CASOS)} casos corretos")


if __name__ == "__main__":
    main()
