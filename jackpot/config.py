import os
import sys
from dataclasses import dataclass

NA_WEB = sys.platform == "emscripten"   # True quando roda no navegador (versão site, via pygbag)

@dataclass(frozen=True)
class Simbolo:
    chave: str
    nome: str       # texto na etiqueta do card
    arquivo: str    # nome do arquivo dentro da pasta "imagens"
    cor: tuple      # cor de destaque do card
    premio: str     # texto exibido quando saem 3 iguais


AZUL_INBEC = (27, 42, 90)
VERMELHO_INBEC = (180, 28, 40)
CINZA_CLARO = (226, 231, 239)
LOGO = "logo_faculdade_2.png"   # usada no card especial, no letreiro e no canto dos cards

CHAVE_LOGO = "logo"
SIMBOLOS = {s.chave: s for s in [
    Simbolo("civil",    "ENG. CIVIL",    "engenheiro_civil_boneco.png",    AZUL_INBEC,     "Brinde Engenharia Civil"),
    Simbolo("software", "ENG. SOFTWARE", "engenheiro_software_boneco.png", VERMELHO_INBEC, "Brinde Engenharia de Software"),
    Simbolo("ads",      "ADS",           "ads_boneco.png",                 AZUL_INBEC,     "Brinde ADS"),
    Simbolo("direito",  "DIREITO",       "direito_boneco.png",             VERMELHO_INBEC, "Brinde Direito"),
    Simbolo("rh",       "RH",            "rh_boneca.png",                  AZUL_INBEC,     "Brinde RH"),
    Simbolo(CHAVE_LOGO, "",              LOGO,                             CINZA_CLARO,    "PRÊMIO ESPECIAL!"),
]}

# Chances por jogada (0.025 = 2,5%). Todos os cursos têm a mesma chance;
# a logo deve ser menor que a de um curso para continuar sendo o prêmio mais difícil.
CHANCE_POR_CURSO = 0.025    # 3 iguais de um curso específico (5 cursos -> 12,5% no total)
CHANCE_LOGO = 0.01          # 3 logos

TITULO = "JACKPOT"
SUBTITULO = "FACULDADE INBEC"
FPS = 60
TAMANHO_INICIAL = (1100, 700)
TAMANHO_WEB = (1280, 720)          # no site, o navegador escala essa tela para caber na página
TAMANHO_MINIMO = (640, 420)

# Roletas
N_ROLETAS = 3
DURACOES = [2.4, 3.2, 4.0]   # segundos até cada roleta parar
VOLTAS_MIN = [3, 4, 5]       # voltas completas antes de parar
REPETICOES_NA_FITA = 3       # quantas vezes cada símbolo aparece em cada roleta

# Pastas
PASTA_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_IMAGENS = os.path.join(PASTA_PROJETO, "imagens")
PASTA_FONTES = os.path.join(PASTA_PROJETO, "fontes")  # Exo 2 (Google Fonts, licença OFL)
PASTA_SONS = os.path.join(PASTA_PROJETO, "sons")

# Efeitos sonoros: evento -> arquivos da pasta "sons" (os da mesma lista tocam juntos).
# Se um arquivo não existir, o jogo simplesmente fica em silêncio naquele evento.
SONS = {
    "girar":   ["roleta-normal.mp3"],
    "vitoria": ["som-criancas-yay.mp3", "winner.mp3"],
    "derrota": ["you_lose.mp3"],
}
VOLUME = {"girar": 0.7, "vitoria": 1.0, "derrota": 0.9}   # de 0.0 a 1.0
FADE_ROLETA_MS = 250    # o som da roleta some suavemente quando a última roleta para


class Cor:
    # identidade INBEC
    AZUL = (27, 42, 90)
    AZUL_CLARO = (44, 66, 132)
    AZUL_ESCURO = (10, 17, 40)
    AZUL_NOITE = (5, 9, 22)
    VERMELHO = (200, 30, 48)
    VERMELHO_CLARO = (240, 70, 88)
    VERMELHO_ESCURO = (110, 10, 22)
    # destaques
    CIANO = (0, 200, 240)
    CIANO_APAGADO = (22, 48, 82)
    DOURADO = (255, 196, 60)
    # metal / neutros
    PRATA_CLARO = (245, 247, 251)
    PRATA = (196, 204, 218)
    PRATA_ESCURO = (120, 130, 150)
    BRANCO = (255, 255, 255)
    PRETO = (0, 0, 0)
    CINZA_CARD = CINZA_CLARO
    FUNDO = (255, 255, 255)
    GRADE = (234, 239, 247)
    GRADE_PONTO = (205, 214, 230)
    TEXTO_LCD = (150, 225, 255)
    TEXTO_DICA = (160, 170, 190)
    CONFETES = [(27, 42, 90), (200, 30, 48), (0, 200, 240), (255, 196, 60), (236, 112, 30)]
