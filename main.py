import asyncio
import pygame  
from jackpot import Jogo

async def main():
    await Jogo().executar()

asyncio.run(main())
