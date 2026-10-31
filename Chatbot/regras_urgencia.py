"""
Camada de regras de urgência (sem IA).

Roda ANTES do modelo de linguagem. Se algum sinal de alerta for detectado,
o chatbot responde com uma mensagem fixa e NÃO consulta a IA.

Níveis:
    4 = Emergência (SAMU 192 / urgência imediata)
    3 = Procurar atendimento hoje (UPA / pronto atendimento)

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
    "Este chatbot é um protótipo acadêmico e não substitui atendimento médico."
)

MSG_HOJE = (
    "⚠️ **Procure atendimento hoje.**\n\n"
    "Os sinais descritos merecem avaliação presencial no mesmo dia, em uma UPA ou "
    "unidade de saúde. Se piorar ou surgir falta de ar, desmaio, dor forte ou "
    "sangramento, **ligue para o SAMU (192)**.\n\n"
    "Este chatbot é um protótipo acadêmico e não substitui atendimento médico."
)

MSG_SAUDE_MENTAL = (
    "💛 Sinto muito que você esteja passando por isso. Você não precisa enfrentar "
    "isso sozinho(a).\n\n"
    "**Ligue para o CVV (188)**, gratuito e disponível 24 horas, ou fale agora com "
    "alguém de confiança. Se houver risco imediato, **ligue para o SAMU (192)** ou "
    "vá à urgência mais próxima."
)


@dataclass(frozen=True)
class Regra:
    id: str
    categoria: str
    nivel: int
    padroes: tuple          # basta UM destes casar
    exige: tuple = ()       # se preenchido, ALGUM destes também precisa casar
    mensagem: str = ""      # vazio = mensagem padrão do nível


REGRAS = (
    # ---- Nível 4: emergência ----
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
        r"desmai", r"perd(i|eu|endo) (a )?consciencia", r"convuls",
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
          (r"sangramento", r"sangrando", r"dor forte", r"perda de liquido", r"bebe (nao )?(mexe|mexendo)"),
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

    # ---- Nível 3: atendimento hoje ----
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
)

# Negação simples logo antes do termo: "não tenho falta de ar", "sem dor no peito".
# (Não captura "não aguento mais essa dor no peito", que continua disparando.)
_NEGACAO = re.compile(
    r"\b(nao (tenho|sinto|estou com|apresento|tive|tem|ha)|sem|nenhum[a]?|nega|nunca tive)( \w+){0,2} $"
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
        msg = r.mensagem or (MSG_EMERGENCIA if r.nivel == 4 else MSG_HOJE)
        alerta = Alerta(r.id, r.categoria, r.nivel, msg)
        if melhor is None or alerta.nivel > melhor.nivel:
            melhor = alerta
    return melhor
