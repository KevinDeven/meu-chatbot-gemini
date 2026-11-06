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
    # ---- Diabetes ----
    (["Tenho diabetes e minha glicemia está 45"], 3),
    (["Minha glicemia deu 62 e estou suando frio e tremendo"], 3),
    (["Meu pai é diabético, está inconsciente e a glicemia baixou"], 4),
    (["Tenho diabetes e meu pai desmaiou"], 4),
    (["Minha glicemia está 350 e estou vomitando"], 4),
    (["Minha glicemia está 350 e estou com muita sonolência"], 4),
    (["Glicemia deu 320, sem sintomas, estou bem"], 3),
    (["Sou diabético e estou com hálito de maçã"], 4),
    (["Sou diabético e estou com respiração rápida e profunda"], 4),
    (["Estou com glicemia alta e muita sonolência"], 4),
    (["Tenho diabetes e uma ferida no pé com pus"], 3),
    (["Tenho diabetes e estou vomitando, não consigo beber nada"], 3),
    (["Tenho diabetes e perdi a visão de repente de um olho"], 3),
    (["Estou com hipoglicemia"], 3),
    (["Estou tremendo e suando frio, uso insulina"], 3),
    (["O que é hipoglicemia?"], None),
    (["Tenho diabetes tipo 2 e quero saber que alimentos posso comer"], None),
    (["Tenho muita sede e urino demais há semanas"], None),
    (["Minha glicemia em jejum foi 110"], None),
    (["Meu colesterol deu 250 mg/dl e a glicemia 130"], None),
    (["Meu filho de 8 anos tem diabetes e está com febre"], None),
    (["Não estou com hipoglicemia, só queria saber como cuidar melhor do meu diabetes"], None),
    (["Não tenho dor no peito nem falta de ar, só tosse"], None),
    (["Estou grávida e o bebê está mexendo normalmente"], None),
    (["Estou grávida e o bebê parou de mexer"], 4),
    (["A minha glicemia está baixa"], 3),
    (["Meu açúcar está baixo"], 3),
    (["Minha glicemia está baixa e estou confuso"], 4),
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
