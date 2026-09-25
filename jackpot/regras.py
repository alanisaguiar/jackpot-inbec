import random
from .config import CHANCE_LOGO, CHANCE_POR_CURSO, CHAVE_LOGO, N_ROLETAS, SIMBOLOS

def chance_do_simbolo(chave): # Chance de uma jogada terminar com 3 iguais deste símbolo
    return CHANCE_LOGO if chave == CHAVE_LOGO else CHANCE_POR_CURSO


def sortear(): # Sorteia o resultado da jogada
    sorteio = random.random()
    acumulado = 0.0
    for chave in SIMBOLOS:
        acumulado += chance_do_simbolo(chave)
        if sorteio < acumulado:
            return [chave] * N_ROLETAS

    while True:
        resultado = random.choices(list(SIMBOLOS), k=N_ROLETAS)
        if len(set(resultado)) > 1:
            return resultado


def premio(resultado): # Retorna o Simbolo vencedor se todos forem iguais, senão None
    if len(set(resultado)) == 1:
        return SIMBOLOS[resultado[0]]
    return None


def chance_de_ganhar(): # Probabilidade de uma jogada sair premiada
    return sum(chance_do_simbolo(chave) for chave in SIMBOLOS)
