"""Classe principal: janela, eventos, estados do jogo e ordem de desenho da tela."""

import asyncio
import math
import random
import time

import pygame

from . import regras
from .cards import criar_cards
from .config import (DURACOES, FADE_ROLETA_MS, FPS, N_ROLETAS, NA_WEB, SUBTITULO, TAMANHO_INICIAL, TAMANHO_MINIMO,
                     TAMANHO_WEB, TITULO, VOLTAS_MIN, Cor)
from .efeitos import Confetes, misturar, sombra_cilindro
from .layout import Layout
from .maquina import Alavanca, Maquina
from .recursos import Fontes, Imagens, Sons
from .roleta import Roleta

PARADO, GIRANDO, RESULTADO = "parado", "girando", "resultado"
ESPERA_INICIAL_WEB_MS = 1500   # no site, cliques logo após abrir são o "clique para começar" da página


class Jogo:
    def __init__(self):
        if NA_WEB:
            # no navegador o Python começa sempre com a mesma semente aleatória:
            # sem isso, todo visitante veria exatamente a mesma sequência de resultados
            random.seed(time.time_ns())
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        pygame.display.set_caption(f"{TITULO} {SUBTITULO}")
        if NA_WEB:
            self.tela = pygame.display.set_mode(TAMANHO_WEB)
        else:
            self.tela = pygame.display.set_mode(TAMANHO_INICIAL, pygame.RESIZABLE)
            self._definir_tamanho_minimo()
        self.relogio = pygame.time.Clock()
        self.tela_cheia = False
        self.tamanho_janela = TAMANHO_INICIAL

        self.imagens = Imagens()
        self.sons = Sons()
        self.roletas = [Roleta() for _ in range(N_ROLETAS)]
        self.alavanca = Alavanca()
        self.confetes = Confetes()

        self.estado = PARADO
        self.premio = None
        self.tempo = 0.0
        self.jogadas = 0
        self.vitorias = 0
        self.inicio_ms = 0   # redefinido quando o laço principal começa

        self.aplicar_layout(self.tela.get_size())

    @staticmethod
    def _definir_tamanho_minimo():
        try:
            pygame.Window.from_display_module().minimum_size = TAMANHO_MINIMO
        except Exception:
            pass  # versão do pygame sem suporte; o layout se adapta mesmo assim

    # --- tamanho da tela ----------------------------------------------------

    def aplicar_layout(self, tamanho):
        """Recalcula tudo que depende do tamanho da janela."""
        self.layout = Layout(tamanho)
        self.fontes = Fontes(self.layout)
        self.maquina = Maquina(self.layout, self.fontes, self.imagens)
        self.sombra = sombra_cilindro(self.layout.tamanho_roleta)
        self.cards, self.cards_borrados = criar_cards(self.imagens, self.layout.tamanho_card)

    def alternar_tela_cheia(self):
        if self.tela_cheia:
            self.tela = pygame.display.set_mode(self.tamanho_janela, pygame.RESIZABLE)
        else:
            self.tamanho_janela = self.tela.get_size()
            self.tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.tela_cheia = not self.tela_cheia
        self.aplicar_layout(self.tela.get_size())

    # --- lógica -------------------------------------------------------------

    def girar(self):
        if self.estado == GIRANDO:
            return
        if NA_WEB and pygame.time.get_ticks() - self.inicio_ms < ESPERA_INICIAL_WEB_MS:
            return   # ignora o clique do "clique para começar" da página, que chega logo após a abertura
        for i, (roleta, simbolo) in enumerate(zip(self.roletas, regras.sortear())):
            roleta.girar(simbolo, DURACOES[i], VOLTAS_MIN[i])
        self.estado = GIRANDO
        self.premio = None
        self.confetes.limpar()
        self.alavanca.puxar()
        self.jogadas += 1
        self.sons.parar_todos()   # corta o som da jogada anterior, se ainda estiver tocando
        self.sons.tocar("girar")

    def finalizar_giro(self):
        self.estado = RESULTADO
        self.premio = regras.premio([r.simbolo_central for r in self.roletas])
        self.sons.parar("girar", FADE_ROLETA_MS)
        if self.premio:
            self.vitorias += 1
            self.confetes.soltar(self.layout.largura, self.layout.altura)
            self.sons.tocar("vitoria")
        else:
            self.sons.tocar("derrota")

    def mensagem(self):
        """Textos do display (linha principal, linha secundária, cor da principal)."""
        if self.estado == GIRANDO:
            return "BOA SORTE!", "", Cor.TEXTO_LCD
        if self.premio:
            return "VOCÊ GANHOU!", self.premio.premio, Cor.DOURADO
        pisca = misturar(Cor.TEXTO_LCD, Cor.CIANO, (math.sin(self.tempo * 4) + 1) / 2)
        if self.estado == RESULTADO:
            return "NÃO FOI DESSA VEZ!", "Clique para tentar de novo", Cor.BRANCO
        return "CLIQUE PARA GIRAR", "ou pressione ESPAÇO", pisca

    def atualizar(self, dt):
        self.tempo += dt
        self.alavanca.atualizar(dt)
        self.confetes.atualizar(dt, self.layout.altura)
        if self.estado == GIRANDO:
            for r in self.roletas:
                r.atualizar(dt)
            if not any(r.girando for r in self.roletas):
                self.finalizar_giro()

    # --- desenho ------------------------------------------------------------

    def desenhar(self):
        lay, maq = self.layout, self.maquina
        vitoria = self.premio is not None

        self.tela.blit(maq.fundo, (0, 0))
        for roleta, rect in zip(self.roletas, lay.roletas):
            roleta.desenhar(self.tela, rect, self.cards, self.cards_borrados, lay.passo_simbolo, self.sombra)
        maq.desenhar_vidro(self.tela)
        maq.desenhar_marcadores(self.tela, self.tempo, vitoria)
        maq.desenhar_leds(self.tela, self.tempo, self.estado == GIRANDO, vitoria)
        linha1, linha2, cor = self.mensagem()
        maq.desenhar_display(self.tela, linha1, linha2, cor, self.jogadas, self.vitorias)
        maq.desenhar_alavanca(self.tela, self.alavanca.posicao)
        if not NA_WEB:   # no site não existe F11/ESC do jogo
            maq.desenhar_dica(self.tela)
        self.confetes.desenhar(self.tela, lay.escala)
        pygame.display.flip()

    # --- loop ---------------------------------------------------------------

    def tratar_evento(self, e):
        """Retorna False quando o jogo deve fechar."""
        if e.type == pygame.QUIT:
            return False
        if e.type == pygame.KEYDOWN:
            if NA_WEB and e.key in (pygame.K_ESCAPE, pygame.K_F11):
                return True   # no navegador, sair e tela cheia ficam por conta da página
            if e.key == pygame.K_ESCAPE:
                if self.tela_cheia:
                    self.alternar_tela_cheia()
                else:
                    return False
            elif e.key == pygame.K_F11:
                self.alternar_tela_cheia()
            elif e.key in (pygame.K_SPACE, pygame.K_RETURN):
                self.girar()
        elif e.type == pygame.VIDEORESIZE and not self.tela_cheia:
            self.aplicar_layout(self.tela.get_size())
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            self.girar()
        elif e.type == pygame.FINGERDOWN:   # telas touch
            self.girar()
        return True

    async def executar(self):
        """Laço principal. É assíncrono porque, no navegador, cada quadro precisa
        devolver o controle à página (await asyncio.sleep(0)); no PC não muda nada."""
        rodando = True
        self.inicio_ms = pygame.time.get_ticks()
        while rodando:
            if NA_WEB:
                ms = self.relogio.tick(FPS)   # o navegador já sincroniza os quadros com a tela
            else:
                # tick_busy_loop mantém o intervalo entre quadros bem regular (o tick comum
                # oscila vários ms no Windows e deixa a animação "engasgando")
                ms = self.relogio.tick_busy_loop(FPS)
            dt = min(ms / 1000, 0.1)  # evita salto se a janela travar
            for e in pygame.event.get():
                rodando = self.tratar_evento(e) and rodando
            self.atualizar(dt)
            self.desenhar()
            await asyncio.sleep(0)
        pygame.quit()
