"""Posições e tamanhos de tudo na tela, calculados a partir do tamanho da janela.

O desenho é feito numa "tela base" com 700 de altura. A largura dessa tela base
acompanha a proporção da janela (entre BASE_L_MIN e BASE_L_MAX), então em
janelas mais largas a máquina também fica mais larga e ocupa as laterais.
A tela base é escalada para caber na janela e centralizada.
"""

import pygame

from .config import N_ROLETAS

BASE_A = 700
BASE_L_MIN, BASE_L_MAX = 1100, 1500   # limite para a máquina não esticar demais em telas ultralargas

# máquina (corpo principal)
MAQ_A = 672
MAQ_Y = 14
MARGEM_LATERAL = 70                    # espaço livre entre a máquina e as bordas da tela
LARGURA_ALAVANCA = 90
MARGEM_INTERNA = 22

# partes da máquina, de cima para baixo
LETREIRO_A = 104
JANELA_Y, JANELA_A = 128, 428      # relativo ao topo da máquina
DISPLAY_Y, DISPLAY_A = 570, 84

# roletas e cards
PAD_JANELA = 14
ESPACO_ROLETAS = 14
CARD_A = 258
CARD_PAD_X = 12
ESPACO_CARDS = 16


class Layout:
    def __init__(self, tamanho):
        self.largura, self.altura = tamanho
        base_l = min(BASE_L_MAX, max(BASE_L_MIN, BASE_A * self.largura / self.altura))
        self.escala = min(self.largura / base_l, self.altura / BASE_A)
        self.ox = (self.largura - base_l * self.escala) / 2
        self.oy = (self.altura - BASE_A * self.escala) / 2
        self.centro_x = self.largura // 2

        maq_l = base_l - 2 * MARGEM_LATERAL - LARGURA_ALAVANCA
        mx = MARGEM_LATERAL
        my = MAQ_Y
        interno_l = maq_l - 2 * MARGEM_INTERNA
        self.maquina = self.rect(mx, my, maq_l, MAQ_A)
        self.letreiro = self.rect(mx + MARGEM_INTERNA, my + 14, interno_l, LETREIRO_A - 14)
        self.janela = self.rect(mx + MARGEM_INTERNA, my + JANELA_Y, interno_l, JANELA_A)
        self.display = self.rect(mx + MARGEM_INTERNA, my + DISPLAY_Y, interno_l, DISPLAY_A)

        roleta_l = (interno_l - 2 * PAD_JANELA - (N_ROLETAS - 1) * ESPACO_ROLETAS) / N_ROLETAS
        roleta_a = JANELA_A - 2 * PAD_JANELA
        self.roletas = [
            self.rect(mx + MARGEM_INTERNA + PAD_JANELA + i * (roleta_l + ESPACO_ROLETAS),
                      my + JANELA_Y + PAD_JANELA, roleta_l, roleta_a)
            for i in range(N_ROLETAS)
        ]
        self.tamanho_roleta = self.roletas[0].size
        self.tamanho_card = (self.px(roleta_l - 2 * CARD_PAD_X), self.px(CARD_A))
        self.passo_simbolo = (CARD_A + ESPACO_CARDS) * self.escala   # distância entre centros de cards

        base_x = mx + maq_l + 14
        centro_y = my + JANELA_Y + JANELA_A / 2
        self.alavanca_base = self.rect(base_x, centro_y - 55, 36, 110)
        self.alavanca_topo_y = self.y(my + JANELA_Y - 20)
        self.alavanca_fundo_y = self.y(my + JANELA_Y + JANELA_A - 30)

        self.margem = self.px(14)

    def card_central(self, roleta):
        """Retângulo do card que está na linha de prêmio de uma roleta."""
        l, a = self.tamanho_card
        return pygame.Rect(0, 0, l, a).move(roleta.centerx - l // 2, roleta.centery - a // 2)

    # --- conversão da tela base para a janela ---------------------------------

    def px(self, valor):
        """Converte um tamanho da tela base para pixels da janela."""
        return max(1, round(valor * self.escala))

    def x(self, valor):
        return round(self.ox + valor * self.escala)

    def y(self, valor):
        return round(self.oy + valor * self.escala)

    def rect(self, x, y, l, a):
        return pygame.Rect(self.x(x), self.y(y), self.px(l), self.px(a))
