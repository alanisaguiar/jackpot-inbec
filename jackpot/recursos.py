import os
from functools import lru_cache
import pygame
from .config import LOGO, NA_WEB, PASTA_FONTES, PASTA_IMAGENS, PASTA_SONS, SIMBOLOS, SONS, VOLUME


# FONTES
@lru_cache(maxsize=None)
def fonte(tamanho, peso=800):
    tamanho = max(8, int(tamanho))
    caminho = os.path.join(PASTA_FONTES, f"Exo2-{peso}.ttf")
    if os.path.exists(caminho):
        return pygame.font.Font(caminho, tamanho)
    return pygame.font.SysFont("segoeui,arial", tamanho, bold=peso >= 700)


class Fontes:
    def __init__(self, layout):
        px = layout.px
        self.letreiro = fonte(px(50), 900)
        self.subtitulo = fonte(px(15), 700)
        self.mensagem = fonte(px(26), 800)
        self.mensagem2 = fonte(px(15), 600)
        self.contador = fonte(px(30), 800)
        self.rotulo = fonte(max(9, px(11)), 700)
        self.dica = fonte(max(11, px(13)), 600)


# IMAGENS

def remover_fundo_claro(img, tolerancia=40):
    mascara = pygame.mask.from_threshold(img, (255, 255, 255, 255), (tolerancia, tolerancia, tolerancia, 255))
    # pinta de transparente só os pixels marcados, sobre uma cópia com canal alfa
    # (usar unsetsurface falha no navegador, onde o formato de pixel é diferente;
    # e não usa convert_alpha para funcionar também sem janela aberta, no script do site)
    resultado = pygame.Surface(img.get_size(), pygame.SRCALPHA)
    resultado.blit(img, (0, 0))
    mascara.to_surface(resultado, setcolor=(0, 0, 0, 0), unsetcolor=None)
    return resultado


def carregar_imagem(arquivo, sem_fundo=False):
    caminho = os.path.join(PASTA_IMAGENS, arquivo)
    if not os.path.exists(caminho):
        print(f"Imagem não encontrada: {caminho}")
        return None
    try:
        img = pygame.image.load(caminho).convert_alpha()
    except pygame.error as erro:
        print(f"Não foi possível carregar {caminho}: {erro}")
        return None
    if sem_fundo:
        img = remover_fundo_claro(img).convert_alpha()
    return img.subsurface(img.get_bounding_rect()).copy()


def ajustar(img, tamanho):
    escala = min(tamanho[0] / img.get_width(), tamanho[1] / img.get_height())
    novo = (max(1, int(img.get_width() * escala)), max(1, int(img.get_height() * escala)))
    if escala > 1:
        # ampliar com "vizinho mais próximo" mantém nítida a logo (desenho em blocos)
        return pygame.transform.scale(img, novo)
    return pygame.transform.smoothscale(img, novo)


class Imagens:
    def __init__(self):
        self.logo = carregar_imagem(LOGO, sem_fundo=True)
        self.simbolos = {chave: self.logo if s.arquivo == LOGO else carregar_imagem(s.arquivo)
                         for chave, s in SIMBOLOS.items()}


# SONS

class Sons:

    def __init__(self):
        self.sons = {}
        for evento, arquivos in SONS.items():
            carregados = [s for s in (self._carregar(a) for a in arquivos) if s]
            for s in carregados:
                s.set_volume(VOLUME.get(evento, 1.0))
            self.sons[evento] = carregados

    @staticmethod
    def _carregar(arquivo):
        if NA_WEB:
            # o navegador não toca MP3 pelo pygbag; o script do site converte para OGG
            arquivo = os.path.splitext(arquivo)[0] + ".ogg"
        caminho = os.path.join(PASTA_SONS, arquivo)
        if not os.path.exists(caminho):
            print(f"Som não encontrado: {caminho}")
            return None
        if not pygame.mixer.get_init():
            return None
        try:
            return pygame.mixer.Sound(caminho)
        except pygame.error as erro:
            print(f"Não foi possível carregar {caminho}: {erro}")
            return None

    def tocar(self, evento):
        for som in self.sons.get(evento, []):
            som.play()

    def parar(self, evento, fade_ms=0):
        for som in self.sons.get(evento, []):
            som.fadeout(fade_ms) if fade_ms else som.stop()

    def parar_todos(self):
        if pygame.mixer.get_init():
            pygame.mixer.stop()
