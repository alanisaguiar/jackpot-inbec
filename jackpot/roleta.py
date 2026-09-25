import math
import random

from .config import REPETICOES_NA_FITA, SIMBOLOS
from .efeitos import ease_out, suave

BORRAO_INICIO, BORRAO_TOTAL = 4.0, 10.0

PASSA_DO_PONTO = 0.12   # fração de um card
TEMPO_VOLTA = 0.35      # segundos


class Roleta:
    def __init__(self):
        self.fita = list(SIMBOLOS) * REPETICOES_NA_FITA
        random.shuffle(self.fita)
        self.pos = float(random.randrange(len(self.fita)))
        self.girando = False
        self.velocidade = 0.0   
        self._inicio = self._alvo = 0.0
        self._t = 0.0
        self._duracao = 1.0

    @property
    def simbolo_central(self):
        return self.fita[round(self.pos) % len(self.fita)]

    def girar(self, resultado, duracao, voltas):
        n = len(self.fita)
        destino = random.choice([i for i, s in enumerate(self.fita) if s == resultado])
        self.pos %= n
        self._inicio = self.pos
        self._alvo = self.pos + voltas * n + ((destino - self.pos) % n)
        self._t = 0.0
        self._duracao = duracao
        self.girando = True

    def _posicao(self, t):
        principal = self._duracao - TEMPO_VOLTA
        passou = self._alvo + PASSA_DO_PONTO
        if t < principal:
            return self._inicio + (passou - self._inicio) * ease_out(t / principal)
        k = min(1.0, (t - principal) / TEMPO_VOLTA)
        return passou - PASSA_DO_PONTO * suave(k)

    def atualizar(self, dt):
        if not self.girando:
            return False
        self._t += dt
        anterior = self.pos
        self.pos = self._posicao(self._t)
        self.velocidade = abs(self.pos - anterior) / dt if dt else 0.0
        if self._t >= self._duracao:
            self.pos = self._alvo % len(self.fita)
            self.girando = False
            self.velocidade = 0.0
            return True
        return False

    def desenhar(self, tela, rect, cards, borrados, passo, sombra):
        base = math.floor(self.pos)
        frac = self.pos - base
        mistura = min(1.0, max(0.0, (self.velocidade - BORRAO_INICIO) / (BORRAO_TOTAL - BORRAO_INICIO)))

        tela.set_clip(rect)
        for k in range(-2, 3):
            chave = self.fita[(base + k) % len(self.fita)]
            centro = (rect.centerx, round(rect.centery + (frac - k) * passo))
            if mistura < 1.0:
                tela.blit(cards[chave], cards[chave].get_rect(center=centro))
            if mistura > 0.0:
                borrado = borrados[chave]
                borrado.set_alpha(int(255 * mistura))
                tela.blit(borrado, borrado.get_rect(center=centro))
        tela.blit(sombra, rect.topleft)
        tela.set_clip(None)
