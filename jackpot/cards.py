"""Montagem dos cards dos cursos (e da logo) que aparecem nas roletas."""

import pygame

from .config import CHAVE_LOGO, SIMBOLOS, Cor
from .efeitos import brilho_radial, desfoque_vertical, gradiente_vertical, misturar
from .recursos import ajustar, fonte

BORRAO = 6   # intensidade do borrão de movimento


def criar_cards(imagens, tamanho):
    """Retorna dois dicionários chave -> card: o normal e o borrado (para o giro rápido)."""
    normais = {chave: criar_card(s, imagens.simbolos[chave], imagens.logo, tamanho)
               for chave, s in SIMBOLOS.items()}
    borrados = {chave: desfoque_vertical(card, BORRAO) for chave, card in normais.items()}
    return normais, borrados


def criar_card(simbolo, imagem, logo, tamanho):
    if simbolo.chave == CHAVE_LOGO:
        return _card_logo(imagem, tamanho)
    return _card_curso(simbolo, imagem, logo, tamanho)


def _card_curso(simbolo, imagem, logo, tamanho):
    """Card de curso: boneco sobre fundo claro e etiqueta com o nome."""
    l, a = tamanho
    cor = simbolo.cor
    etiqueta_a = int(a * 0.17)
    area = pygame.Rect(0, 0, l, a - etiqueta_a).inflate(-int(l * 0.08), -int(a * 0.05))
    centro = (area.centerx, area.centery - int(a * 0.02))

    card = gradiente_vertical(tamanho, misturar(Cor.BRANCO, cor, 0.14), Cor.BRANCO).convert_alpha()
    _decorar_fundo(card, centro, [cor])

    if imagem is not None:
        sombra = pygame.Surface(tamanho, pygame.SRCALPHA)
        pe = pygame.Rect(0, 0, int(area.width * 0.55), max(4, int(a * 0.04)))
        pe.center = (area.centerx, area.bottom)
        pygame.draw.ellipse(sombra, (0, 0, 0, 55), pe)
        card.blit(sombra, (0, 0))
        img = ajustar(imagem, area.size)
        card.blit(img, img.get_rect(midbottom=area.midbottom))

    if logo is not None:
        mini = ajustar(logo, (int(a * 0.09), int(a * 0.09)))
        card.blit(mini, mini.get_rect(topright=(l - int(l * 0.05), int(l * 0.05))))

    _brilho_vidro(card)
    _desenhar_etiqueta(card, simbolo.nome, cor, pygame.Rect(0, a - etiqueta_a, l, etiqueta_a))
    return _finalizar(card, cor)


def _card_logo(imagem, tamanho):
    """Card especial: só a logo INBEC, grande, sobre branco e cinza claro."""
    l, a = tamanho
    centro = (l // 2, a // 2)
    card = gradiente_vertical(tamanho, Cor.BRANCO, Cor.CINZA_CARD).convert_alpha()
    _decorar_fundo(card, centro, [Cor.AZUL, Cor.VERMELHO])
    if imagem is not None:
        img = ajustar(imagem, (int(l * 0.66), int(a * 0.66)))
        card.blit(img, img.get_rect(center=centro))
    _brilho_vidro(card)
    return _finalizar(card, Cor.AZUL)


def _decorar_fundo(card, centro, cores):
    """Listras diagonais sutis, halo de luz e anéis finos atrás da imagem."""
    l, a = card.get_size()
    principal = cores[0]
    camada = pygame.Surface((l, a), pygame.SRCALPHA)
    for x in range(-a, l, max(6, l // 9)):
        pygame.draw.line(camada, (*principal, 14), (x, 0), (x + a, a), max(1, l // 70))
    card.blit(camada, (0, 0))

    # medida de referência: em cards largos, os círculos seguem a altura para não vazar
    ref = min(l, int(a * 0.84))
    halo = brilho_radial(int(ref * 0.48), principal, 90)
    card.blit(halo, halo.get_rect(center=centro))

    camada = pygame.Surface((l, a), pygame.SRCALPHA)
    segunda = cores[-1]
    pygame.draw.circle(camada, (*principal, 80), centro, int(ref * 0.36), max(1, ref // 90))
    pygame.draw.circle(camada, (*segunda, 50), centro, int(ref * 0.43), max(1, ref // 150))
    card.blit(camada, (0, 0))


def _brilho_vidro(card):
    l, a = card.get_size()
    camada = pygame.Surface((l, a), pygame.SRCALPHA)
    pygame.draw.polygon(camada, (255, 255, 255, 45), [(0, 0), (int(l * 0.55), 0), (0, int(a * 0.4))])
    card.blit(camada, (0, 0))


def _desenhar_etiqueta(card, texto, cor, rect):
    faixa = gradiente_vertical(rect.size, misturar(cor, Cor.BRANCO, 0.15), misturar(cor, Cor.PRETO, 0.3))
    card.blit(faixa, rect.topleft)
    pygame.draw.line(card, misturar(cor, Cor.BRANCO, 0.5), rect.topleft, (rect.right, rect.top),
                     max(1, rect.height // 18))

    f = fonte(rect.height * 0.5, 800)
    s = f.render(texto, True, Cor.BRANCO)
    sombra = f.render(texto, True, misturar(cor, Cor.PRETO, 0.6))
    largura_max = rect.width * 0.9
    if s.get_width() > largura_max:
        s = ajustar(s, (int(largura_max), s.get_height()))
        sombra = ajustar(sombra, (int(largura_max), sombra.get_height()))
    r = s.get_rect(center=rect.center)
    card.blit(sombra, r.move(0, max(1, rect.height // 20)))
    card.blit(s, r)


def _finalizar(card, cor_borda):
    """Recorta os cantos arredondados e desenha as bordas."""
    l, a = card.get_size()
    raio = max(4, int(l * 0.08))
    mascara = pygame.Surface((l, a), pygame.SRCALPHA)
    pygame.draw.rect(mascara, (255, 255, 255, 255), mascara.get_rect(), border_radius=raio)
    card.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    borda = max(2, l // 70)
    pygame.draw.rect(card, cor_borda, card.get_rect(), borda, border_radius=raio)
    pygame.draw.rect(card, Cor.BRANCO, card.get_rect().inflate(-2 * borda, -2 * borda), 1,
                     border_radius=max(1, raio - borda))
    return card
