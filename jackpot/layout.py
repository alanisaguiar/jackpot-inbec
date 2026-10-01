"""Posições e tamanhos de tudo na tela, calculados a partir do tamanho da janela.

O jogo é desenhado numa "tela base" com 700 de altura cuja largura acompanha a
proporção da janela (no mínimo BASE_L_MIN). Por isso ele sempre ocupa a largura
toda: os rolos ficam no centro e as colunas laterais absorvem o espaço que sobra.
As barras do topo e da base vão de ponta a ponta da janela.
"""

import pygame

from .config import N_ROLETAS

BASE_A = 700
BASE_L_MIN = 1100

# barra do topo e placa "JACKPOT" (que desce um pouco além da barra)
TOPO_A = 92
PLACA_L, PLACA_A = 440, 106
SELO_LOGO = 60

# janela dos rolos
JANELA_L = 900
JANELA_Y, JANELA_A = 112, 456
PAD_JANELA = 14
ESPACO_ROLETAS = 14
CARD_A = 282
CARD_PAD_X = 12
ESPACO_CARDS = 16

# barra de controles (base)
BASE_Y = 588
BOTAO_L, BOTAO_A = 280, 80
DISPLAY_A = 76
ESPACO_BOTAO = 20

# colunas tech das laterais
COLUNA_L_MAX = 150
COLUNA_L_MIN = 26                     # abaixo disso não há espaço nem para uma coluna fininha
GAP_COLUNA = 24


class Layout:
    def __init__(self, tamanho):
        self.largura, self.altura = tamanho
        base_l = max(BASE_L_MIN, BASE_A * self.largura / self.altura)
        self.escala = min(self.largura / base_l, self.altura / BASE_A)
        self.ox = (self.largura - base_l * self.escala) / 2
        self.oy = (self.altura - BASE_A * self.escala) / 2
        self.centro_x = self.largura // 2
        cx = base_l / 2

        # topo (de ponta a ponta)
        self.barra_topo = pygame.Rect(0, 0, self.largura, self.y(TOPO_A))
        self.placa = self.rect(cx - PLACA_L / 2, 0, PLACA_L, PLACA_A)
        self.placa.top = 0
        self.placa.height = self.y(PLACA_A)
        self.selo_logo = self.rect(26, (TOPO_A - SELO_LOGO) / 2, SELO_LOGO, SELO_LOGO)

        # rolos
        jx = cx - JANELA_L / 2
        self.janela = self.rect(jx, JANELA_Y, JANELA_L, JANELA_A)
        roleta_l = (JANELA_L - 2 * PAD_JANELA - (N_ROLETAS - 1) * ESPACO_ROLETAS) / N_ROLETAS
        roleta_a = JANELA_A - 2 * PAD_JANELA
        self.roletas = [
            self.rect(jx + PAD_JANELA + i * (roleta_l + ESPACO_ROLETAS), JANELA_Y + PAD_JANELA, roleta_l, roleta_a)
            for i in range(N_ROLETAS)
        ]
        self.tamanho_roleta = self.roletas[0].size
        self.tamanho_card = (self.px(roleta_l - 2 * CARD_PAD_X), self.px(CARD_A))
        self.passo_simbolo = (CARD_A + ESPACO_CARDS) * self.escala   # distância entre centros de cards

        # base (de ponta a ponta): painel de mensagem à esquerda, botão GIRAR à direita
        self.barra_base = pygame.Rect(0, self.y(BASE_Y), self.largura, self.altura - self.y(BASE_Y))
        centro_base = (BASE_Y + BASE_A) / 2
        self.botao = self.rect(jx + JANELA_L - BOTAO_L, centro_base - BOTAO_A / 2, BOTAO_L, BOTAO_A)
        self.display = self.rect(jx, centro_base - DISPLAY_A / 2, JANELA_L - BOTAO_L - ESPACO_BOTAO, DISPLAY_A)

        # colunas laterais, centralizadas no espaço livre de cada lado dos rolos
        livre = jx - GAP_COLUNA
        coluna_l = min(COLUNA_L_MAX, livre - 48)   # pelo menos 24 de folga de cada lado da coluna
        self.colunas = []
        if coluna_l >= COLUNA_L_MIN:
            for centro in (livre / 2, base_l - livre / 2):
                self.colunas.append(self.rect(centro - coluna_l / 2, JANELA_Y, coluna_l, JANELA_A))

        self.margem = self.px(14)

    def card_central(self, roleta):
        """Retângulo do card que está na linha de prêmio de uma roleta."""
        l, a = self.tamanho_card
        return pygame.Rect(0, 0, l, a).move(roleta.centerx - l // 2, roleta.centery - a // 2)

    # conversão da tela base para a janela

    def px(self, valor):
        """Converte um tamanho da tela base para pixels da janela."""
        return max(1, round(valor * self.escala))

    def x(self, valor):
        return round(self.ox + valor * self.escala)

    def y(self, valor):
        return round(self.oy + valor * self.escala)

    def rect(self, x, y, l, a):
        return pygame.Rect(self.x(x), self.y(y), self.px(l), self.px(a))
