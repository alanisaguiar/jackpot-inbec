import math
import random
import pygame
from .config import Cor


def ease_out(t, potencia=3):
    return 1 - (1 - t) ** potencia


def suave(t):
    return t * t * (3 - 2 * t)


def misturar(c1, c2, k):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * k) for i in range(3))


def gradiente_vertical(tamanho, cor_topo, cor_base):
    l, a = tamanho
    surf = pygame.Surface((max(1, l), max(1, a)))
    for y in range(a):
        pygame.draw.line(surf, misturar(cor_topo, cor_base, y / max(1, a - 1)), (0, y), (l, y))
    return surf


def forma_com_gradiente(tamanho, cor_topo, cor_base, raio, **cantos):
    surf = gradiente_vertical(tamanho, cor_topo, cor_base).convert_alpha()
    mascara = pygame.Surface(tamanho, pygame.SRCALPHA)
    pygame.draw.rect(mascara, (255, 255, 255, 255), mascara.get_rect(), border_radius=raio, **cantos)
    surf.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return surf


def brilho_radial(raio, cor, alpha_max=150):
    raio = max(2, raio)
    surf = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
    passos = 40
    for i in range(passos, 0, -1):
        k = i / passos
        a = int(alpha_max * (1 - k) ** 1.6)
        pygame.draw.circle(surf, (*cor, a), (raio, raio), int(raio * k))
    return surf


def desfocar(surf, raio):
    raio = max(1, int(raio))
    maior = pygame.Surface((surf.get_width() + raio * 4, surf.get_height() + raio * 4), pygame.SRCALPHA)
    maior.blit(surf, (raio * 2, raio * 2))
    return pygame.transform.gaussian_blur(maior, raio)


def sombra_suave(tamanho, raio_borda, desfoque, alpha=90):
    f = 4
    pequeno = (max(1, tamanho[0] // f), max(1, tamanho[1] // f))
    base = pygame.Surface(pequeno, pygame.SRCALPHA)
    pygame.draw.rect(base, (10, 17, 40, alpha), base.get_rect(), border_radius=max(1, raio_borda // f))
    borrada = desfocar(base, max(1, desfoque // f))
    return pygame.transform.smoothscale(borrada, (borrada.get_width() * f, borrada.get_height() * f))


def texto_com_brilho(fonte, texto, cor, cor_brilho, raio):
    s = fonte.render(texto, True, cor)
    halo = desfocar(fonte.render(texto, True, cor_brilho), raio)
    resultado = halo.copy()
    resultado.blit(halo, (0, 0))   # reforça o halo
    resultado.blit(s, s.get_rect(center=resultado.get_rect().center))
    return resultado


def desfoque_vertical(surf, forca=6):
    l, a = surf.get_size()
    pequeno = pygame.transform.smoothscale(surf, (l, max(1, a // forca)))
    return pygame.transform.smoothscale(pequeno, (l, a))



def sombra_cilindro(tamanho):
    l, a = tamanho
    surf = pygame.Surface(tamanho, pygame.SRCALPHA)
    for y in range(a):
        d = abs(y - a / 2) / (a / 2)
        pygame.draw.line(surf, (*Cor.AZUL_NOITE, int(235 * d ** 2.2)), (0, y), (l, y))
    return surf


def texto_centralizado(tela, fonte, texto, centro, cor, largura_max=None):
    s = fonte.render(texto, True, cor)
    if largura_max and s.get_width() > largura_max:
        k = largura_max / s.get_width()
        s = pygame.transform.smoothscale(s, (int(s.get_width() * k), int(s.get_height() * k)))
    tela.blit(s, s.get_rect(center=centro))


class Confetes:
    def __init__(self):
        self.particulas = []

    def soltar(self, largura, altura, quantidade=220):
        for _ in range(quantidade):
            self.particulas.append([
                random.uniform(0, largura), random.uniform(-altura, 0),
                random.uniform(-60, 60), random.uniform(0.2, 0.5) * altura,
                random.choice(Cor.CONFETES), random.uniform(0, math.tau),
            ])

    def limpar(self):
        self.particulas.clear()

    def atualizar(self, dt, altura):
        for p in self.particulas:
            p[0] += p[2] * dt
            p[1] += p[3] * dt
            p[5] += dt * 6
        self.particulas = [p for p in self.particulas if p[1] < altura + 20]

    def desenhar(self, tela, escala=1.0):
        for x, y, _, _, cor, ang in self.particulas:
            l = (abs(math.cos(ang)) * 10 + 2) * escala
            pygame.draw.rect(tela, cor, (x, y, max(1, l), max(1, 5 * escala)))
