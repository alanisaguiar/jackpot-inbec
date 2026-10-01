"""Aparência da tela do jogo no estilo "cassino moderno".

Barra do topo com a placa JACKPOT, janela dos rolos no centro, colunas tech
nas laterais e barra de controles embaixo (painel de mensagem + botão GIRAR).

Tudo o que é estático é desenhado uma única vez por tamanho de janela (em
`Maquina.fundo`); a cada quadro só são desenhadas as partes animadas.
"""

import math
import random

import pygame

from .config import NA_WEB, SUBTITULO, TITULO, Cor
from .efeitos import (brilho_radial, desfocar, forma_com_gradiente, gradiente_vertical, misturar,
                      sombra_suave, texto_com_brilho)
from .recursos import ajustar


def texto_espacado(fonte, texto, cor, espaco):
    """Texto com espaçamento extra entre as letras (visual mais "tech")."""
    letras = [fonte.render(c, True, cor) for c in texto]
    largura = sum(s.get_width() for s in letras) + espaco * (len(letras) - 1)
    surf = pygame.Surface((max(1, largura), fonte.get_height()), pygame.SRCALPHA)
    x = 0
    for s in letras:
        surf.blit(s, (x, 0))
        x += s.get_width() + espaco
    return surf


class BotaoGirar:
    """Animação do botão GIRAR: afunda quando a jogada começa e volta."""

    DURACAO = 0.35

    def __init__(self):
        self.afundado = 0.0    # 0 = solto, 1 = totalmente apertado
        self._t = None

    def apertar(self):
        self._t = 0.0

    def atualizar(self, dt):
        if self._t is None:
            return
        self._t += dt
        k = self._t / self.DURACAO
        self.afundado = math.sin(min(1.0, k) * math.pi)
        if k >= 1:
            self._t = None
            self.afundado = 0.0


class Maquina:
    def __init__(self, layout, fontes, imagens):
        self.lay = layout
        self.fontes = fontes
        self.leds_colunas = []      # retângulos dos LEDs das colunas (preenchido ao desenhar as colunas)
        self.fundo = self._construir_fundo(imagens.logo)
        self.vidro = self._construir_vidro()
        self.brilho_vitoria = self._construir_brilho_vitoria()
        self.setas = self._construir_setas()
        self.botoes = self._construir_botoes()
        self.leds_placa, self.leds_barra = self._posicoes_leds()

    # =====================================================================
    # partes estáticas (desenhadas uma vez)
    # =====================================================================

    def _construir_fundo(self, logo):
        lay = self.lay
        tela = self._cenario().convert()
        for coluna in lay.colunas:
            self._desenhar_coluna(tela, coluna, logo)
        self._desenhar_janela(tela)
        self._desenhar_barra_topo(tela, logo)
        self._desenhar_barra_base(tela)
        return tela

    def _cenario(self):
        """Fundo da tela inteira: azul profundo, grade tech sutil e brilho atrás dos rolos."""
        lay, px = self.lay, self.lay.px
        tela = gradiente_vertical((lay.largura, lay.altura), (16, 28, 66), Cor.AZUL_NOITE)

        grade = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
        passo = max(12, px(44))
        for x in range(lay.centro_x % passo, lay.largura, passo):
            pygame.draw.line(grade, (*Cor.CIANO, 14), (x, 0), (x, lay.altura))
        for y in range(0, lay.altura, passo):
            pygame.draw.line(grade, (*Cor.CIANO, 14), (0, y), (lay.largura, y))
        tela.blit(grade, (0, 0))

        brilho = brilho_radial(int(lay.janela.width * 0.75), Cor.CIANO, 55)
        tela.blit(brilho, brilho.get_rect(center=lay.janela.center))
        brilho = brilho_radial(int(lay.janela.width * 0.5), Cor.AZUL_CLARO, 120)
        tela.blit(brilho, brilho.get_rect(center=lay.janela.center))
        return tela

    def _desenhar_coluna(self, tela, r, logo):
        """Coluna futurista: moldura prateada, interior escuro com circuitos, faixas de LED e a logo."""
        px = self.lay.px
        sombra = sombra_suave(r.size, px(16), px(14), 120)
        tela.blit(sombra, sombra.get_rect(center=(r.centerx, r.centery + px(8))))

        tela.blit(forma_com_gradiente(r.size, Cor.PRATA_CLARO, Cor.PRATA_ESCURO, px(16)), r)
        dentro = r.inflate(-px(8), -px(8))
        tela.blit(forma_com_gradiente(dentro.size, Cor.AZUL, Cor.AZUL_NOITE, px(12)), dentro)

        # capitéis (topo e base) um pouco mais largos, como colunas de verdade
        for y in (r.top - px(6), r.bottom - px(18)):
            capitel = pygame.Rect(0, 0, r.width + px(14), px(24))
            capitel.midtop = (r.centerx, y)
            tela.blit(forma_com_gradiente(capitel.size, Cor.PRATA_CLARO, Cor.PRATA_ESCURO, px(8)), capitel)
            pygame.draw.line(tela, Cor.VERMELHO, (capitel.left + px(8), capitel.centery),
                             (capitel.right - px(8), capitel.centery), max(1, px(2)))

        # trilhas de circuito (sempre as mesmas: sorteio com semente fixa)
        circuito = pygame.Surface(dentro.size, pygame.SRCALPHA)
        sorte = random.Random(7)
        l, a = dentro.size
        for _ in range(max(3, l // px(14))):
            x = sorte.randint(px(14), max(px(15), l - px(14)))
            y1 = sorte.randint(px(30), a // 2)
            y2 = sorte.randint(a // 2, a - px(30))
            pygame.draw.line(circuito, (*Cor.CIANO, 45), (x, y1), (x, y2), max(1, px(2)))
            for y in (y1, y2):
                pygame.draw.circle(circuito, (*Cor.CIANO, 90), (x, y), max(2, px(3)))
        tela.blit(circuito, dentro)

        # faixas de LED nas bordas internas (desenhadas a cada quadro em desenhar_leds)
        seg_l, seg_a, seg_passo = max(2, px(5)), px(12), px(18)
        xs = [dentro.left + px(8), dentro.right - px(8) - seg_l] if r.width >= px(70) else [dentro.centerx - seg_l // 2]
        for x in xs:
            self.leds_colunas.append([pygame.Rect(x, y, seg_l, seg_a)
                                      for y in range(dentro.top + px(30), dentro.bottom - px(30) - seg_a, seg_passo)])

        # medalhão com a logo no meio da coluna
        if logo is not None and r.width >= px(80):
            lado = int(min(r.width * 0.62, px(84)))
            selo = pygame.Rect(0, 0, lado, lado)
            selo.center = dentro.center
            halo = brilho_radial(int(lado * 0.95), Cor.CIANO, 80)
            tela.blit(halo, halo.get_rect(center=selo.center))
            pygame.draw.rect(tela, Cor.BRANCO, selo, border_radius=px(14))
            pygame.draw.rect(tela, Cor.CIANO, selo, max(1, px(2)), border_radius=px(14))
            img = ajustar(logo, (int(lado * 0.72), int(lado * 0.72)))
            tela.blit(img, img.get_rect(center=selo.center))

    def _desenhar_janela(self, tela):
        lay, px = self.lay, self.lay.px
        j = lay.janela
        sombra = sombra_suave(j.size, px(22), px(20), 160)
        tela.blit(sombra, sombra.get_rect(center=(j.centerx, j.centery + px(10))))
        tela.blit(forma_com_gradiente(j.size, Cor.PRATA_CLARO, Cor.PRATA_ESCURO, px(20)), j)
        interna = j.inflate(-px(8), -px(8))
        pygame.draw.rect(tela, Cor.AZUL_NOITE, interna, border_radius=px(16))
        for r in lay.roletas:
            tela.blit(forma_com_gradiente(r.size, Cor.AZUL_ESCURO, Cor.AZUL_NOITE, px(10)), r)
            pygame.draw.rect(tela, misturar(Cor.AZUL_CLARO, Cor.AZUL_NOITE, 0.3), r.inflate(px(4), px(4)),
                             px(1), border_radius=px(11))

    def _desenhar_barra_topo(self, tela, logo):
        lay, px, f = self.lay, self.lay.px, self.fontes
        b = lay.barra_topo
        tela.blit(gradiente_vertical(b.size, Cor.AZUL_CLARO, Cor.AZUL), b)
        listras = pygame.Surface(b.size, pygame.SRCALPHA)
        for x in range(-b.height, b.width, px(26)):
            pygame.draw.line(listras, (255, 255, 255, 10), (x, b.height), (x + b.height, 0), px(8))
        tela.blit(listras, b)
        pygame.draw.rect(tela, Cor.PRATA, (0, b.bottom - px(5), b.width, px(5)))
        pygame.draw.rect(tela, Cor.VERMELHO, (0, b.bottom, b.width, px(3)))

        # selo com a logo à esquerda
        if logo is not None:
            s = lay.selo_logo
            pygame.draw.rect(tela, Cor.BRANCO, s, border_radius=px(12))
            pygame.draw.rect(tela, Cor.CIANO, s, max(1, px(2)), border_radius=px(12))
            img = ajustar(logo, (int(s.width * 0.72), int(s.height * 0.72)))
            tela.blit(img, img.get_rect(center=s.center))

        # placa JACKPOT no centro, descendo além da barra
        p = lay.placa
        sombra = sombra_suave(p.size, px(24), px(14), 150)
        tela.blit(sombra, sombra.get_rect(center=(p.centerx, p.centery + px(8))))
        cantos = dict(border_bottom_left_radius=px(28), border_bottom_right_radius=px(28))
        tela.blit(forma_com_gradiente(p.size, Cor.PRATA_CLARO, Cor.PRATA_ESCURO, 0, **cantos), p)
        dentro = p.inflate(-px(12), -px(12))
        dentro.top = p.top
        dentro.height = p.height - px(6)
        cantos = dict(border_bottom_left_radius=px(23), border_bottom_right_radius=px(23))
        tela.blit(forma_com_gradiente(dentro.size, Cor.AZUL_CLARO, Cor.AZUL_NOITE, 0, **cantos), dentro)

        titulo = texto_com_brilho(f.letreiro, TITULO, Cor.BRANCO, Cor.CIANO, px(7))
        tela.blit(titulo, titulo.get_rect(center=(p.centerx, p.bottom - px(64))))
        antes, _, depois = SUBTITULO.rpartition(" ")
        esp = px(4)
        partes = [texto_espacado(f.subtitulo, antes, Cor.PRATA, esp),
                  texto_espacado(f.subtitulo, depois, Cor.VERMELHO_CLARO, esp)]
        vao = esp * 4
        x = p.centerx - (sum(s.get_width() for s in partes) + vao) // 2
        for s in partes:
            tela.blit(s, s.get_rect(midleft=(x, p.bottom - px(28))))
            x += s.get_width() + vao

    def _desenhar_barra_base(self, tela):
        lay, px = self.lay, self.lay.px
        b = lay.barra_base
        tela.blit(gradiente_vertical(b.size, Cor.AZUL, Cor.AZUL_NOITE), b)
        pygame.draw.rect(tela, Cor.VERMELHO, (0, b.top - px(3), b.width, px(3)))
        pygame.draw.rect(tela, Cor.PRATA, (0, b.top, b.width, px(5)))

        # painel de mensagem (estilo LCD)
        d = lay.display
        tela.blit(forma_com_gradiente(d.size, Cor.AZUL_NOITE, (8, 14, 34), px(16)), d)
        pygame.draw.rect(tela, Cor.AZUL_CLARO, d, px(2), border_radius=px(16))
        linhas = pygame.Surface(d.size, pygame.SRCALPHA)
        for y in range(0, d.height, 3):
            pygame.draw.line(linhas, (0, 0, 0, 40), (0, y), (d.width, y))
        tela.blit(linhas, d)

        # "berço" onde o botão GIRAR fica encaixado
        berco = lay.botao.inflate(px(14), px(16))
        berco.top += px(4)
        pygame.draw.rect(tela, Cor.AZUL_NOITE, berco, border_radius=berco.height // 2)
        pygame.draw.rect(tela, Cor.PRATA_ESCURO, berco, max(1, px(2)), border_radius=berco.height // 2)

    def _construir_botoes(self):
        """Botão GIRAR em dois estados (pronto e girando), com borda 3D embaixo, e o halo pulsante."""
        lay, px = self.lay, self.lay.px
        l, a = lay.botao.size
        borda = px(8)

        def botao(topo, base, lateral, texto, cor_texto):
            surf = pygame.Surface((l, a + borda), pygame.SRCALPHA)
            pygame.draw.rect(surf, lateral, (0, borda, l, a), border_radius=a // 2)
            surf.blit(forma_com_gradiente((l, a), topo, base, a // 2), (0, 0))
            brilho = pygame.Surface((l, a), pygame.SRCALPHA)
            pygame.draw.ellipse(brilho, (255, 255, 255, 34), (l * 0.12, a * 0.07, l * 0.76, a * 0.34))
            surf.blit(brilho, (0, 0))
            fonte = self.fontes.botao
            s = fonte.render(texto, True, cor_texto)
            sombra = fonte.render(texto, True, misturar(base, Cor.PRETO, 0.5))
            if s.get_width() > l * 0.84:
                s = ajustar(s, (int(l * 0.84), s.get_height()))
                sombra = ajustar(sombra, (int(l * 0.84), sombra.get_height()))
            r = s.get_rect(center=(l // 2, a // 2))
            surf.blit(sombra, r.move(0, px(3)))
            surf.blit(s, r)
            return surf

        pronto = botao(Cor.VERMELHO_CLARO, Cor.VERMELHO, Cor.VERMELHO_ESCURO, "GIRAR", Cor.BRANCO)
        girando = botao(Cor.AZUL_CLARO, Cor.AZUL, Cor.AZUL_NOITE, "GIRANDO...", Cor.TEXTO_LCD)
        halo_base = pygame.Surface((l + px(10), a + px(10)), pygame.SRCALPHA)
        pygame.draw.rect(halo_base, (*Cor.VERMELHO_CLARO, 255), halo_base.get_rect(), border_radius=a // 2)
        halo = desfocar(halo_base, px(14))
        return {"pronto": pronto, "girando": girando, "halo": halo, "borda": borda}

    def _construir_vidro(self):
        """Reflexo diagonal por cima dos rolos, como um vidro."""
        j = self.lay.janela.inflate(-self.lay.px(8), -self.lay.px(8))
        vidro = pygame.Surface(j.size, pygame.SRCALPHA)
        l, a = j.size
        pygame.draw.polygon(vidro, (255, 255, 255, 18), [(l * 0.05, 0), (l * 0.32, 0), (l * 0.12, a), (-l * 0.15, a)])
        pygame.draw.polygon(vidro, (255, 255, 255, 10), [(l * 0.38, 0), (l * 0.45, 0), (l * 0.25, a), (l * 0.18, a)])
        return vidro

    def _construir_brilho_vitoria(self):
        l, a = self.lay.tamanho_card
        px = self.lay.px
        moldura = pygame.Surface((l + px(8), a + px(8)), pygame.SRCALPHA)
        pygame.draw.rect(moldura, (*Cor.DOURADO, 255), moldura.get_rect(), px(5), border_radius=px(20))
        return desfocar(moldura, px(10))

    def _construir_setas(self):
        px = self.lay.px
        a, c = px(16), px(16)
        seta = pygame.Surface((c + 2, a * 2 + 2), pygame.SRCALPHA)
        pygame.draw.polygon(seta, Cor.VERMELHO_CLARO, [(0, 0), (0, a * 2), (c, a)])
        brilho = desfocar(seta, px(6))
        brilho.blit(brilho, (0, 0))
        brilho.blit(seta, seta.get_rect(center=brilho.get_rect().center))
        return brilho, pygame.transform.flip(brilho, True, False)

    def _posicoes_leds(self):
        """Pontos de LED: contorno de baixo da placa e uma fileira ao longo da barra do topo."""
        lay, px = self.lay, self.lay.px
        p = lay.placa.inflate(-px(26), 0)
        placa = [(x, p.bottom - px(14)) for x in range(p.left + px(20), p.right - px(20), px(20))]
        placa += [(x, lay.placa.top + px(10)) for x in range(p.left + px(20), p.right - px(20), px(20))]
        y = lay.barra_topo.bottom - px(14)
        barra = [(x, y) for x in range(px(110), lay.largura - px(110), px(26))
                 if not lay.placa.left - px(10) < x < lay.placa.right + px(10)]
        return placa, barra

    # =====================================================================
    # partes animadas (desenhadas a cada quadro)
    # =====================================================================

    def desenhar_vidro(self, tela):
        tela.blit(self.vidro, self.lay.janela.inflate(-self.lay.px(8), -self.lay.px(8)))

    def desenhar_leds(self, tela, tempo, girando, vitoria):
        px = self.lay.px
        fase = tempo * (22 if girando or vitoria else 5)

        def cor_led(i):
            if vitoria:
                return Cor.DOURADO if (i + int(tempo * 8)) % 2 else Cor.VERMELHO_CLARO
            brilho = (math.sin(i * 0.55 - fase) + 1) / 2
            return misturar(Cor.CIANO_APAGADO, Cor.CIANO, brilho ** 3)

        raio = max(1, px(2))
        for i, ponto in enumerate(self.leds_placa):
            pygame.draw.circle(tela, cor_led(i), ponto, raio)
        for i, ponto in enumerate(self.leds_barra):
            pygame.draw.circle(tela, cor_led(i), ponto, raio)
        for faixa in self.leds_colunas:
            for n, seg in enumerate(faixa):
                pygame.draw.rect(tela, cor_led(n), seg, border_radius=seg.width // 2)

    def desenhar_marcadores(self, tela, tempo, vitoria):
        lay, px = self.lay, self.lay.px
        esq, dir_ = self.setas
        y = lay.janela.centery
        tela.blit(esq, esq.get_rect(midleft=(lay.janela.left - px(4), y)))
        tela.blit(dir_, dir_.get_rect(midright=(lay.janela.right + px(4), y)))
        if vitoria:
            self.brilho_vitoria.set_alpha(int(150 + 105 * (math.sin(tempo * 9) + 1) / 2))
            for r in lay.roletas:
                tela.blit(self.brilho_vitoria, self.brilho_vitoria.get_rect(center=lay.card_central(r).center))
            for r in lay.roletas:
                pygame.draw.rect(tela, Cor.DOURADO, lay.card_central(r).inflate(px(6), px(6)), px(3),
                                 border_radius=px(18))

    def desenhar_display(self, tela, linha1, linha2, cor1):
        lay, px, f = self.lay, self.lay.px, self.fontes
        d = lay.display
        largura_max = d.width - px(40)
        y1 = d.top + int(d.height * (0.36 if linha2 else 0.5))
        self._texto(tela, f.mensagem, linha1, cor1, (d.centerx, y1), largura_max)
        if linha2:
            self._texto(tela, f.mensagem2, linha2, Cor.PRATA, (d.centerx, d.top + int(d.height * 0.72)), largura_max)

    def desenhar_botao(self, tela, girando, afundado, tempo):
        b = self.lay.botao
        borda = self.botoes["borda"]
        if not girando:
            halo = self.botoes["halo"]
            halo.set_alpha(int(90 + 110 * (math.sin(tempo * 3) + 1) / 2))
            tela.blit(halo, halo.get_rect(center=b.center))
        superficie = self.botoes["girando" if girando else "pronto"]
        descida = int(borda * (1.0 if girando else afundado * 0.9))
        # ao afundar, a borda 3D de baixo "some" sob a face do botão
        face = superficie.subsurface((0, 0, b.width, b.height + borda - descida))
        tela.blit(face, (b.left, b.top + descida))

    @staticmethod
    def _texto(tela, fonte, texto, cor, centro, largura_max):
        s = fonte.render(texto, True, cor)
        if s.get_width() > largura_max:
            s = ajustar(s, (int(largura_max), s.get_height()))
        tela.blit(s, s.get_rect(center=centro))

    def desenhar_dica(self, tela):
        if NA_WEB:
            return   # no site não existe F11/ESC do jogo
        s = self.fontes.dica.render("F11  tela cheia   ·   ESC  sair", True, Cor.TEXTO_DICA)
        tela.blit(s, s.get_rect(midright=(self.lay.largura - self.lay.margem, self.lay.barra_topo.centery)))
