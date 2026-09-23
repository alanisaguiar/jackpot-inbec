import asyncio

# importado aqui de propósito: na versão site, o pygbag só lê este arquivo
# para decidir quais bibliotecas baixar no navegador
import pygame  # noqa: F401

from jackpot import Jogo


async def main():
    await Jogo().executar()


# o pygbag (versão site) exige o asyncio.run no nível do arquivo
asyncio.run(main())
