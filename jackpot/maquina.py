import math
import pygame
from .config import SUBTITULO, TITULO, Cor
from .efeitos import (brilho_radial, desfocar, forma_com_gradiente, fundo_grade,
                      gradiente_vertical, misturar, sombra_suave, texto_com_brilho)
from .recursos import ajustar


def texto_espacado(fonte, texto, cor, espaco):
    letras = [fonte.render(c, True, cor) for c in texto]
    largura = sum(s.get_width() for s in letras) + espaco * (len(letras) - 1)
    surf = pygame.Surface((max(1, largura), fonte.get_height()), pygame.SRCALPHA)
    x = 0
    for s in letras:
        surf.blit(s, (x, 0))
        x += s.get_width() + espaco
    return surf


class Alavanca:
    DURACAO = 0.5

    def __init__(self):
        self.posicao = 0.0    # 0 = em cima, 1 = puxada
        self._t = None

    def puxar(self):
        self._t = 0.0

    def atualizar(self, dt):
        if self._t is None:
            return
        self._t += dt
        k = self._t / self.DURACAO
        self.posicao = math.sin(min(1.0, k) * math.pi)
        if k >= 1:
            self._t = None
            self.posicao = 0.0


class Maquina:
    def __init__(self, layout, fontes, imagens):
        self.lay = layout
        self.fontes = fontes
        self.fundo = self._construir_fundo(imagens.logo)
        self.vidro = self._construir_vidro()
        self.brilho_vitoria = self._construir_brilho_vitoria()
        self.setas = self._construir_setas()
        self.bola = self._construir_bola()

    # partes estáticas (desenhadas uma vez)

    def _construir_fundo(self, logo):
        lay, px = self.lay, self.lay.px
        tela = fundo_grade((lay.largura, lay.altura), px(32)).convert()

        # sombra do gabinete no chão
        sombra = sombra_suave(lay.maquina.size, px(34), px(18), 110)
        tela.blit(sombra, sombra.get_rect(center=(lay.maquina.centerx, lay.maquina.centery + px(14))))

        # gabinete: casca prateada + corpo azul
        tela.blit(forma_com_gradiente(lay.maquina.size, Cor.PRATA_CLARO, Cor.PRATA_ESCURO, px(34)), lay.maquina)
        corpo = lay.maquina.inflate(-px(10), -px(10))
        tela.blit(forma_com_gradiente(corpo.size, Cor.AZUL, Cor.AZUL_ESCURO, px(30)), corpo)
        for x in (corpo.left + px(20), corpo.right - px(20)):
            for y in (lay.janela.top + px(8), lay.display.bottom - px(8)):
                self._parafuso(tela, (x, y), px(5))

        self._desenhar_letreiro(tela, logo)
        self._desenhar_janela(tela)
        self._desenhar_display(tela)
        self._desenhar_base_alavanca(tela)
        return tela

    @staticmethod
    def _parafuso(tela, centro, raio):
        pygame.draw.circle(tela, Cor.PRATA_ESCURO, centro, raio + 1)
        pygame.draw.circle(tela, Cor.PRATA, centro, raio)
        pygame.draw.line(tela, Cor.PRATA_ESCURO, (centro[0] - raio + 2, centro[1] + raio - 2),
                         (centro[0] + raio - 2, centro[1] - raio + 2), 2)

    def _desenhar_letreiro(self, tela, logo):
        lay, px, f = self.lay, self.lay.px, self.fontes
        r = lay.letreiro
        tela.blit(forma_com_gradiente(r.size, Cor.AZUL_CLARO, Cor.AZUL_NOITE, px(20)), r)
        pygame.draw.rect(tela, misturar(Cor.CIANO, Cor.AZUL, 0.3), r, px(2), border_radius=px(20))
        pygame.draw.line(tela, Cor.VERMELHO, (r.left + px(40), r.bottom - px(3)), (r.right - px(40), r.bottom - px(3)), px(2))

        titulo = texto_com_brilho(f.letreiro, TITULO, Cor.BRANCO, Cor.CIANO, px(7))
        tela.blit(titulo, titulo.get_rect(center=(r.centerx, r.top + int(r.height * 0.40))))

        antes, _, depois = SUBTITULO.rpartition(" ")
        esp = px(4)
        partes = [texto_espacado(f.subtitulo, antes, Cor.PRATA, esp),
                  texto_espacado(f.subtitulo, depois, Cor.VERMELHO_CLARO, esp)]
        vao = esp * 4
        largura = sum(p.get_width() for p in partes) + vao
        x = r.centerx - largura // 2
        y = r.top + int(r.height * 0.78)
        for p in partes:
            tela.blit(p, p.get_rect(midleft=(x, y)))
            x += p.get_width() + vao

        # selos com a logo nas duas pontas do letreiro
        if logo is not None:
            lado = int(r.height * 0.66)
            for cx in (r.left + px(30) + lado // 2, r.right - px(30) - lado // 2):
                selo = pygame.Rect(0, 0, lado, lado)
                selo.center = (cx, r.centery)
                brilho = brilho_radial(int(lado * 0.9), Cor.CIANO, 70)
                tela.blit(brilho, brilho.get_rect(center=selo.center))
                pygame.draw.rect(tela, Cor.BRANCO, selo, border_radius=px(12))
                pygame.draw.rect(tela, Cor.CIANO, selo, px(2), border_radius=px(12))
                img = ajustar(logo, (int(lado * 0.72), int(lado * 0.72)))
                tela.blit(img, img.get_rect(center=selo.center))

    def _desenhar_janela(self, tela):
        lay, px = self.lay, self.lay.px
        j = lay.janela
        tela.blit(forma_com_gradiente(j.size, Cor.PRATA_CLARO, Cor.PRATA_ESCURO, px(18)), j)
        interna = j.inflate(-px(8), -px(8))
        pygame.draw.rect(tela, Cor.AZUL_NOITE, interna, border_radius=px(14))
        for r in lay.roletas:
            tela.blit(forma_com_gradiente(r.size, Cor.AZUL_ESCURO, Cor.AZUL_NOITE, px(10)), r)
            pygame.draw.rect(tela, misturar(Cor.AZUL_CLARO, Cor.AZUL_NOITE, 0.3), r.inflate(px(4), px(4)),
                             px(1), border_radius=px(11))

    def _desenhar_display(self, tela):
        lay, px = self.lay, self.lay.px
        d = lay.display
        tela.blit(forma_com_gradiente(d.size, Cor.AZUL_NOITE, (8, 14, 34), px(16)), d)
        pygame.draw.rect(tela, Cor.AZUL_CLARO, d, px(2), border_radius=px(16))

        linhas = pygame.Surface(d.size, pygame.SRCALPHA)
        for y in range(0, d.height, 3):
            pygame.draw.line(linhas, (0, 0, 0, 40), (0, y), (d.width, y))
        tela.blit(linhas, d)

    def _desenhar_base_alavanca(self, tela):
        lay, px = self.lay, self.lay.px
        b = lay.alavanca_base
        suporte = pygame.Rect(lay.maquina.right - px(6), b.top + px(20), b.left - lay.maquina.right + px(12), b.height - px(40))
        tela.blit(gradiente_vertical(suporte.size, Cor.PRATA, Cor.PRATA_ESCURO), suporte)
        tela.blit(forma_com_gradiente(b.size, Cor.PRATA_CLARO, Cor.PRATA_ESCURO, px(12)), b)
        fenda = pygame.Rect(0, 0, px(8), b.height - px(26))
        fenda.center = b.center
        pygame.draw.rect(tela, Cor.AZUL_NOITE, fenda, border_radius=px(4))

    def _construir_vidro(self):
        """Reflexo diagonal por cima das roletas, como um vidro."""
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

    def _construir_bola(self):
        raio = self.lay.px(24)
        bola = pygame.Surface((raio * 2 + 2, raio * 2 + 2), pygame.SRCALPHA)
        for i in range(raio, 0, -1):
            k = i / raio
            deslocamento = (1 - k) * raio * 0.35
            pygame.draw.circle(bola, misturar(Cor.VERMELHO_CLARO, Cor.VERMELHO_ESCURO, k ** 1.4),
                               (raio + 1 - deslocamento, raio + 1 - deslocamento), i)
        brilho = pygame.Surface(bola.get_size(), pygame.SRCALPHA)
        pygame.draw.ellipse(brilho, (255, 255, 255, 150),
                            (raio * 0.45, raio * 0.3, raio * 0.6, raio * 0.4))
        bola.blit(brilho, (0, 0))
        return bola

    # partes animadas (desenhadas a cada quadro)

    def desenhar_vidro(self, tela):
        tela.blit(self.vidro, self.lay.janela.inflate(-self.lay.px(8), -self.lay.px(8)))

    def desenhar_leds(self, tela, tempo, girando, vitoria):
        """LEDs no contorno do letreiro e faixas de luz nas laterais do gabinete."""
        lay, px = self.lay, self.lay.px
        fase = tempo * (22 if girando or vitoria else 5)

        def cor_led(i):
            if vitoria:
                return Cor.DOURADO if (i + int(tempo * 8)) % 2 else Cor.VERMELHO_CLARO
            brilho = (math.sin(i * 0.55 - fase) + 1) / 2
            return misturar(Cor.CIANO_APAGADO, Cor.CIANO, brilho ** 3)

        r = lay.letreiro.inflate(-px(14), -px(10))
        passo = px(22)
        i = 0
        for y in (r.top, r.bottom - px(2)):
            for x in range(r.left + px(30), r.right - px(30), passo):
                pygame.draw.circle(tela, cor_led(i), (x, y), max(1, px(2)))
                i += 1

        # faixas laterais segmentadas
        topo, fundo = lay.janela.top + px(24), lay.display.bottom - px(24)
        seg_a, seg_passo, seg_l = px(10), px(16), px(4)
        for x in (lay.maquina.left + px(11), lay.maquina.right - px(11) - seg_l):
            for n, y in enumerate(range(topo, fundo - seg_a, seg_passo)):
                pygame.draw.rect(tela, cor_led(n), (x, y, seg_l, seg_a), border_radius=seg_l // 2)

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
        largura_max = d.width - px(60)
        centro_x = d.centerx
        y1 = d.top + int(d.height * (0.38 if linha2 else 0.5))
        self._texto(tela, f.mensagem, linha1, cor1, (centro_x, y1), largura_max)
        if linha2:
            self._texto(tela, f.mensagem2, linha2, Cor.PRATA, (centro_x, d.top + int(d.height * 0.72)), largura_max)

    @staticmethod
    def _texto(tela, fonte, texto, cor, centro, largura_max):
        s = fonte.render(texto, True, cor)
        if s.get_width() > largura_max:
            s = ajustar(s, (int(largura_max), s.get_height()))
        tela.blit(s, s.get_rect(center=centro))

    def desenhar_alavanca(self, tela, posicao):
        lay, px = self.lay, self.lay.px
        b = lay.alavanca_base
        piv = (b.centerx, b.centery)
        y = int(lay.alavanca_topo_y + (lay.alavanca_fundo_y - lay.alavanca_topo_y) * posicao)
        haste = pygame.Rect(0, 0, px(10), abs(piv[1] - y))
        haste.midbottom = (piv[0], piv[1]) if y < piv[1] else (piv[0], y)
        if haste.height:
            tela.blit(gradiente_vertical(haste.size, Cor.PRATA_CLARO, Cor.PRATA), haste)
            pygame.draw.line(tela, Cor.BRANCO, (haste.left + px(2), haste.top), (haste.left + px(2), haste.bottom), px(2))
            pygame.draw.line(tela, Cor.PRATA_ESCURO, (haste.right - 1, haste.top), (haste.right - 1, haste.bottom), px(2))
        pygame.draw.circle(tela, Cor.PRATA_ESCURO, piv, px(11))
        pygame.draw.circle(tela, Cor.PRATA_CLARO, piv, px(8))
        tela.blit(self.bola, self.bola.get_rect(center=(piv[0], y)))

    def desenhar_dica(self, tela):
        s = self.fontes.dica.render("F11  tela cheia   ·   ESC  sair", True, Cor.TEXTO_DICA)
        tela.blit(s, s.get_rect(topright=(self.lay.largura - self.lay.margem, self.lay.margem // 2)))
