"""
Camada de regras de urgência (sem IA) do chatbot de orientação sobre DIABETES.

Roda ANTES do modelo de linguagem. Se algum sinal de alerta for detectado,
o chatbot responde com uma mensagem fixa e NÃO consulta a IA.

Níveis:
    4 = Emergência (SAMU 192 / urgência imediata)
    3 = Procurar atendimento hoje (UPA / pronto atendimento / equipe de saúde)

Conteúdo: sinais de alerta gerais (dor no peito, falta de ar, AVC, etc.) e sinais
específicos de diabetes (hipoglicemia, crise de açúcar alto, pé diabético, visão,
"dia de doença" e valores de glicemia digitados).

Princípio de segurança: na dúvida, escalar (preferir sobre-triagem a sub-triagem).
Limitação: busca por padrões de texto; não entende todo contexto. Valide com
casos de teste (ver testar_regras.py) e revise a lista com um profissional de saúde.
"""

import re
import unicodedata
from dataclasses import dataclass

MSG_EMERGENCIA = (
    "🚨 **Os sintomas que você descreveu podem indicar uma situação grave.**\n\n"
    "Não espere: **ligue agora para o SAMU (192)** ou vá imediatamente à unidade "
    "de urgência/UPA mais próxima. Se possível, peça para alguém ficar com você.\n\n"
    "Este chatbot é um protótipo acadêmico sobre diabetes e não substitui atendimento médico."
)

MSG_HOJE = (
    "⚠️ **Procure atendimento hoje.**\n\n"
    "Os sinais descritos merecem avaliação presencial no mesmo dia, em uma UPA ou "
    "unidade de saúde. Se piorar ou surgir falta de ar, desmaio, dor forte ou "
    "sangramento, **ligue para o SAMU (192)**.\n\n"
    "Este chatbot é um protótipo acadêmico sobre diabetes e não substitui atendimento médico."
)

MSG_SAUDE_MENTAL = (
    "💛 Sinto muito que você esteja passando por isso. Você não precisa enfrentar "
    "isso sozinho(a).\n\n"
    "**Ligue para o CVV (188)**, gratuito e disponível 24 horas, ou fale agora com "
    "alguém de confiança. Se houver risco imediato, **ligue para o SAMU (192)** ou "
    "vá à urgência mais próxima."
)

# ---- Mensagens específicas de diabetes ----
MSG_HIPOGLICEMIA_GRAVE = (
    "🚨 **Pode ser uma hipoglicemia grave (açúcar muito baixo no sangue).**\n\n"
    "**Ligue agora para o SAMU (192).**\n\n"
    "- Se a pessoa estiver **inconsciente, convulsionando ou sem conseguir engolir**, "
    "**não** dê comida nem bebida pela boca (risco de engasgo). Deite-a de lado e "
    "aguarde o socorro.\n"
    "- Se estiver acordada e conseguir engolir com segurança, ofereça açúcar ou suco "
    "enquanto o socorro não chega.\n\n"
    "Este chatbot é um protótipo acadêmico sobre diabetes e não substitui atendimento médico."
)

MSG_HIPOGLICEMIA = (
    "⚠️ **Sinais de açúcar baixo no sangue (hipoglicemia).**\n\n"
    "Se você está acordado(a) e consegue engolir com segurança:\n"
    "1. **Meça a glicemia**, se tiver o aparelho.\n"
    "2. Tome cerca de **15 g de açúcar de absorção rápida**: por exemplo, cerca de 150 mL "
    "de suco de fruta ou refrigerante comum (não diet), ou 1 colher de sopa de açúcar ou mel.\n"
    "3. **Meça de novo após 15 minutos.** Se continuar abaixo de 70 mg/dL, repita.\n"
    "4. Quando normalizar, faça um lanche leve se a próxima refeição demorar.\n\n"
    "**Ligue para o SAMU (192)** se não melhorar após 2 tentativas, se houver confusão, "
    "desmaio ou convulsão, ou se não conseguir engolir. Mesmo que melhore, **avise sua "
    "equipe de saúde hoje**: episódios de hipoglicemia precisam de revisão do tratamento.\n\n"
    "Este chatbot é um protótipo acadêmico sobre diabetes e não substitui atendimento médico."
)

MSG_CRISE_DIABETES = (
    "🚨 **Seus sinais podem indicar uma crise de açúcar muito alto (hiperglicemia grave "
    "ou cetoacidose).**\n\n"
    "Isso é uma emergência. **Ligue agora para o SAMU (192)** ou vá imediatamente à "
    "urgência/UPA mais próxima. Não espere melhorar sozinho(a) e não dirija. Leve o aparelho "
    "de medir glicemia e a lista dos seus medicamentos, se possível.\n\n"
    "Este chatbot é um protótipo acadêmico sobre diabetes e não substitui atendimento médico."
)

MSG_HIPERGLICEMIA = (
    "⚠️ **Glicemia muito alta.**\n\n"
    "Procure atendimento **hoje** (UPA ou unidade de saúde) ou fale hoje com sua equipe de "
    "saúde. Beba água e siga o plano combinado com sua equipe; este chatbot não orienta "
    "doses.\n\n"
    "**Vá à urgência ou ligue 192** se surgirem vômitos, dor forte na barriga, respiração "
    "rápida, sonolência ou confusão.\n\n"
    "Este chatbot é um protótipo acadêmico sobre diabetes e não substitui atendimento médico."
)

MSG_PE_DIABETICO = (
    "⚠️ **Ferida no pé de quem tem diabetes precisa de avaliação hoje.**\n\n"
    "Feridas nos pés podem infectar e piorar rápido, mesmo sem dor. Procure atendimento hoje "
    "(UBS, UPA ou ambulatório). Enquanto isso, mantenha a ferida limpa e coberta com curativo "
    "limpo, evite andar descalço(a) e não fure bolhas nem corte calos.\n\n"
    "**Vá à urgência** se houver febre, pele escura ou preta, mau cheiro forte ou vermelhidão "
    "se espalhando.\n\n"
    "Este chatbot é um protótipo acadêmico sobre diabetes e não substitui atendimento médico."
)

MSG_DIA_DOENCA = (
    "⚠️ **Vômitos ou diarreia com diabetes, sem conseguir comer ou beber, precisam de "
    "avaliação hoje.**\n\n"
    "Há risco de desidratação e de descontrole da glicemia. Procure atendimento hoje (UPA ou "
    "unidade de saúde) e **não mude nem suspenda medicamentos ou insulina por conta própria**: "
    "peça orientação à equipe de saúde.\n\n"
    "**Ligue 192** se houver sonolência, confusão, respiração rápida ou dor forte na barriga.\n\n"
    "Este chatbot é um protótipo acadêmico sobre diabetes e não substitui atendimento médico."
)

_DIABETES = (r"diabet", r"insulina", r"glicemia", r"glicose")


@dataclass(frozen=True)
class Regra:
    id: str
    categoria: str
    nivel: int
    padroes: tuple          # basta UM destes casar
    exige: tuple = ()       # se preenchido, ALGUM destes também precisa casar
    tambem: tuple = ()      # se preenchido, ALGUM destes (outro grupo) também precisa casar
    mensagem: str = ""      # vazio = mensagem padrão do nível


REGRAS = (
    # ---- Nível 4: emergência (gerais) ----
    Regra("dor_peito", "cardiovascular", 4, (
        r"dor (\w+ )?(no|do|em) peito", r"aperto (no|do) peito",
        r"pressao (no|do) peito", r"dor (que )?(irradia|vai|desce) (para|pro) (o )?(braco|mandibula|queixo)",
    )),
    Regra("falta_ar", "respiratorio", 4, (
        r"falta de ar", r"dificuldade (para|de|em) respirar",
        r"nao (consigo|estou conseguindo|to conseguindo) respirar",
        r"labios? (roxos?|azulados?)", r"engasg\w+ .{0,30}(nao (consegue|consigo|respira)|roxo|azul)",
    )),
    Regra("neurologico", "neurologico", 4, (
        r"desmai", r"inconsciente", r"perd(i|eu|endo) (a )?consciencia", r"convuls",
        r"rosto (torto|caido)", r"boca torta", r"fala (enrolada|arrastada)",
        r"dificuldade (para|de|em) falar",
        r"(fraqueza|perda de forca|dormencia|formigamento) (em|de|no|na) (um )?(lado|braco|perna)",
        r"pior dor de cabeca da (minha )?vida", r"confusao mental", r"desorientad",
    )),
    Regra("meningite", "neurologico", 4,
          (r"pescoco (rigido|duro)", r"rigidez (no|de) pescoco"),
          exige=(r"febre", r"febril")),
    Regra("hemorragia", "sangramento", 4, (
        r"sangramento (muito )?(intenso|forte|que nao para)", r"hemorragia",
        r"vomit\w* (com )?sangue", r"sangue no vomito", r"tossi\w* (com )?sangue",
    )),
    Regra("gestante_alerta", "gestacao", 4,
          (r"sangramento", r"sangrando", r"dor forte", r"perda de liquido", r"bebe (nao|parou de) (mexe|mexendo|mexer)", r"nao (sinto|esta) (o )?bebe (mexer|mexendo)"),
          exige=(r"gravida", r"gestante", r"gravidez")),
    Regra("trauma_grave", "trauma", 4, (
        r"atropel", r"acidente (grave|de carro|de moto)", r"queda de (altura|laje|telhado)",
        r"traumatismo",
    )),
    Regra("intoxicacao", "intoxicacao", 4, (
        r"envenen", r"overdose", r"intoxica",
        r"(tomei|tomou|engoli|engoliu) (comprimidos|remedios?) demais",
        r"(engoli|engoliu|bebeu|bebi|ingeri|ingeriu) .{0,20}(veneno|soda caustica|agua sanitaria|cloro|produto de limpeza)",
    )),
    Regra("saude_mental", "saude_mental", 4, (
        r"quero (morrer|me matar|sumir)", r"vou me matar", r"me matar", r"suicid",
        r"tirar (a )?minha vida", r"acabar com (a )?minha vida", r"automutila", r"me cortar",
    ), mensagem=MSG_SAUDE_MENTAL),

    # ---- Nível 4: diabetes ----
    Regra("hipoglicemia_grave", "diabetes", 4, (
        r"hipoglicemia", r"(glicemia|glicose|acucar) (esta |ta |estava |ficou |muito )*baix[oa]",
        r"baixou (a )?(glicemia|glicose|o acucar)", r"(glicemia|glicose|acucar) (\w+ )?baixou",
    ), exige=(
        r"desmai", r"inconsciente", r"convuls", r"nao (acorda|responde|consegue (engolir|beber|comer|falar))",
        r"confus", r"desorientad", r"muito sonolent",
    ), mensagem=MSG_HIPOGLICEMIA_GRAVE),
    Regra("cetoacidose", "diabetes", 4, (
        r"cetoacidose", r"cetonas? (altas?|positiv\w*|presentes?)",
        r"halito (cetonico|de maca|frutado|de fruta)",
    ), mensagem=MSG_CRISE_DIABETES),
    Regra("respiracao_rapida_diabetes", "diabetes", 4,
          (r"respiracao (rapida|profunda|ofegante)",),
          exige=_DIABETES, mensagem=MSG_CRISE_DIABETES),
    Regra("hiperglicemia_sintomas", "diabetes", 4, (
        r"(glicemia|glicose|acucar) (muito |esta |ta |estava )?alt[ao]", r"hiperglicemia",
    ), exige=(
        r"vomit", r"nausea", r"enjoo", r"dor (forte |intensa )?(na|de) (barriga|abdomen)",
        r"sonolen", r"confus", r"respiracao (rapida|profunda)",
    ), mensagem=MSG_CRISE_DIABETES),

    # ---- Nível 3: atendimento hoje (gerais) ----
    Regra("dengue_alarme", "sinais_alarme_febre", 3, (
        r"dor (forte|intensa) (na|de) (barriga|abdomen|abdominal)",
        r"dor abdominal (forte|intensa)",
        r"vomit\w* (varias vezes|toda hora|sem parar|persistente\w*|o tempo todo)",
        r"sangramento (no|do) nariz", r"sangramento (na|da|nas) gengiva\w*",
        r"manchas? vermelhas?", r"(muito|muita) (sonolen\w+|sono)", r"muito irritad",
        r"tontura (ao|quando) (levantar|ficar de pe)",
    ), exige=(r"febre", r"febril")),
    Regra("febre_bebe", "pediatria", 3,
          (r"\bbebe\b", r"recem.?nascido", r"\bnenem\b", r"\b\d+ (dias|semanas|meses) de vida"),
          exige=(r"febre", r"febril", r"quentinh\w+")),
    Regra("abdome_agudo", "gastro", 3, (
        r"dor (muito )?forte (na|de) (barriga|abdomen)", r"barriga (dura|rigida)",
        r"fezes pretas", r"sangue (nas|na) fezes",
    )),
    Regra("queimadura", "trauma", 3, (
        r"queimadura (grave|extensa|no rosto|em (uma )?area grande)",
    )),
    Regra("trauma_cabeca", "trauma", 3, (
        r"(batida|pancada|bati) (na|a) cabeca",
    )),

    # ---- Nível 3: diabetes ----
    Regra("hipoglicemia_relatada", "diabetes", 3, (
        r"(?<!nao )(?<!nunca )\b(estou|to|tou|esta|estava|fiquei|ficou|tive|teve|tenho|tem|sinto|sentindo)\b"
        r".{0,30}(hipoglicemia|glicemia baixa|glicose baixa|acucar baixo)",
        r"(?<!nao )(?<!nunca )(glicemia|glicose|acucar) (esta |ta |estava |ficou |muito )+baix[oa]",
    ), mensagem=MSG_HIPOGLICEMIA),
    Regra("hipoglicemia_sintomas", "diabetes", 3, (
        r"tremor", r"tremendo", r"suor frio", r"suando frio", r"suando muito",
        r"fome (de repente|repentina|subita)", r"coracao disparado",
    ), exige=_DIABETES + (r"hipoglicemia",), mensagem=MSG_HIPOGLICEMIA),
    Regra("pe_diabetico", "diabetes", 3, (
        r"(ferida|ulcera|bolha|machucado)\w* .{0,40}\b(pe|pes|dedos?)\b",
        r"\b(pe|pes|dedos?)\b .{0,40}(ferida|ulcera|bolha|machucado)",
    ), exige=(
        r"\bpus\b", r"secrecao", r"vermelh", r"inchad", r"inchaco", r"cheiro", r"febre",
        r"preto", r"escuro", r"roxo", r"nao (cicatriza|sara|melhora)", r"quente",
    ), tambem=_DIABETES, mensagem=MSG_PE_DIABETICO),
    Regra("dia_de_doenca", "diabetes", 3, (
        r"vomit\w*", r"diarreia",
    ), exige=_DIABETES, tambem=(
        r"nao (consigo|consegue|estou conseguindo|to conseguindo) (comer|beber|me alimentar|manter|segurar)",
        r"desidrat", r"boca seca", r"sem conseguir (comer|beber)",
    ), mensagem=MSG_DIA_DOENCA),
    Regra("visao_subita", "diabetes", 3, (
        r"perda (subita|repentina) (da|de) visao",
        r"perd(i|eu|endo) (a )?visao (de repente|subitamente|do nada)",
        r"(cortina|veu|mancha escura) (na|no|em) (minha )?(visao|olho)",
    )),
)

# Negação simples logo antes do termo: "não tenho falta de ar", "sem dor no peito".
# (Não captura "não aguento mais essa dor no peito", que continua disparando.)
_NEGACAO = re.compile(
    r"\b(nao (tenho|sinto|estou com|apresento|tive|tem|ha)|sem|nem|nenhum[a]?|nega|nunca tive)( \w+){0,2} $"
)

# Valores de glicemia digitados (mg/dL): "glicemia 45", "glicose em 320", "250 mg/dl".
_GLIC_APOS_PALAVRA = re.compile(
    r"(glicemia|glicose|glicemico|glicemica|acucar (no|do) sangue|hgt|dextro)\D{0,25}?(\d{2,3})(?!\d)"
)
_GLIC_COM_UNIDADE = re.compile(r"(\d{2,3})\s*(mg ?/ ?dl|mg por dl)")
_NAO_GLICEMIA = re.compile(r"(colesterol|triglic|ldl|hdl|pressao)\D{0,25}$")
_SINTOMAS_CRISE = re.compile(
    r"vomit|nausea|enjoo|dor (forte |intensa )?(na|de) (barriga|abdomen)|sonolen|confus"
    r"|respiracao (rapida|profunda|ofegante)|halito|desidrat"
)


@dataclass(frozen=True)
class Alerta:
    regra_id: str
    categoria: str
    nivel: int
    mensagem: str


def normalizar(texto: str) -> str:
    """Minúsculas, sem acentos, espaços normalizados."""
    texto = unicodedata.normalize("NFD", texto.lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", texto).strip()


def _casa_sem_negacao(padrao: str, texto: str) -> bool:
    for m in re.finditer(padrao, texto):
        antes = texto[max(0, m.start() - 30):m.start()]
        if not _NEGACAO.search(antes):
            return True
    return False


def _valores_glicemia(texto: str) -> list[int]:
    valores = [int(m.group(3)) for m in _GLIC_APOS_PALAVRA.finditer(texto)]
    for m in _GLIC_COM_UNIDADE.finditer(texto):
        if not _NAO_GLICEMIA.search(texto[max(0, m.start() - 30):m.start()]):
            valores.append(int(m.group(1)))
    return [v for v in valores if 20 <= v <= 900]


def _alerta_glicemia(texto: str) -> Alerta | None:
    """Avalia valores de glicemia digitados pela pessoa."""
    valores = _valores_glicemia(texto)
    if not valores:
        return None
    candidatos = []
    if max(valores) >= 300:
        if _SINTOMAS_CRISE.search(texto):
            candidatos.append(Alerta("glicemia_muito_alta_sintomas", "diabetes", 4, MSG_CRISE_DIABETES))
        else:
            candidatos.append(Alerta("glicemia_muito_alta", "diabetes", 3, MSG_HIPERGLICEMIA))
    if min(valores) < 70:
        candidatos.append(Alerta("glicemia_baixa_valor", "diabetes", 3, MSG_HIPOGLICEMIA))
    return max(candidatos, key=lambda a: a.nivel) if candidatos else None


def avaliar_urgencia(mensagens_usuario: list[str]) -> Alerta | None:
    """Recebe TODAS as mensagens do usuário na conversa e devolve o alerta de
    maior nível encontrado (ou None). Usar a conversa inteira permite combinar
    informações (ex.: 'febre' numa mensagem e 'vômitos sem parar' em outra)."""
    texto = normalizar(" . ".join(mensagens_usuario))
    melhor: Alerta | None = None
    for r in REGRAS:
        if not any(_casa_sem_negacao(p, texto) for p in r.padroes):
            continue
        if r.exige and not any(re.search(p, texto) for p in r.exige):
            continue
        if r.tambem and not any(re.search(p, texto) for p in r.tambem):
            continue
        msg = r.mensagem or (MSG_EMERGENCIA if r.nivel == 4 else MSG_HOJE)
        alerta = Alerta(r.id, r.categoria, r.nivel, msg)
        if (melhor is None or alerta.nivel > melhor.nivel
                or (alerta.nivel == melhor.nivel and alerta.categoria == "diabetes"
                    and melhor.categoria != "diabetes")):
            melhor = alerta
    glic = _alerta_glicemia(texto)
    if glic is not None and (melhor is None or glic.nivel > melhor.nivel):
        melhor = glic
    return melhor
