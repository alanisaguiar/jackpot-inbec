"""Gera a versão site do jogo (roda no navegador via pygbag / WebAssembly).

Uso (na pasta do projeto):
    py ferramentas/gerar_site.py            gera o site e abre um servidor de teste em http://localhost:8000
    py ferramentas/gerar_site.py --build    só gera; o site pronto fica em build_web/build/web

O que o script faz, sem mexer nos arquivos originais do projeto:
  1. copia o código e as fontes para build_web/
  2. copia só as imagens usadas, reduzidas (os bonecos originais têm ~2 MB cada)
  3. converte os sons de MP3 para OGG (formato que o pygbag toca no navegador)
  4. cria o ícone da aba (favicon) a partir da logo
  5. roda o pygbag, que empacota tudo em uma página web
  6. (só com --build) troca a tela "Ready to start" do pygbag pela tela inicial
     da INBEC, que fica em ferramentas/site/tela_inicial.html
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "build_web"
ALTURA_MAX_IMAGEM = 700      # px; suficiente para os cards mesmo em tela cheia Full HD
TITULO_PAGINA = "Jackpot Faculdade INBEC"
TELA_INICIAL = RAIZ / "ferramentas" / "site" / "tela_inicial.html"

sys.path.insert(0, str(RAIZ))
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame  # noqa: E402
from jackpot.config import LOGO, SIMBOLOS, SONS  # noqa: E402
from jackpot.recursos import remover_fundo_claro  # noqa: E402


def copiar_codigo():
    shutil.copy2(RAIZ / "main.py", DESTINO / "main.py")
    ignorar = shutil.ignore_patterns("__pycache__", "*.pyc")
    shutil.copytree(RAIZ / "jackpot", DESTINO / "jackpot", ignore=ignorar)
    shutil.copytree(RAIZ / "fontes", DESTINO / "fontes", ignore=ignorar)


def copiar_imagens():
    (DESTINO / "imagens").mkdir()
    usadas = {s.arquivo for s in SIMBOLOS.values()} | {LOGO}
    for nome in sorted(usadas):
        img = pygame.image.load(RAIZ / "imagens" / nome)
        if img.get_height() > ALTURA_MAX_IMAGEM:
            k = ALTURA_MAX_IMAGEM / img.get_height()
            img = pygame.transform.smoothscale(img, (round(img.get_width() * k), ALTURA_MAX_IMAGEM))
        destino = DESTINO / "imagens" / nome
        pygame.image.save(img, destino)
        antes = (RAIZ / "imagens" / nome).stat().st_size / 1024
        print(f"  imagem {nome}: {antes:.0f} KB -> {destino.stat().st_size / 1024:.0f} KB")


def converter_sons():
    import imageio_ffmpeg
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    (DESTINO / "sons").mkdir()
    usados = {arq for lista in SONS.values() for arq in lista}
    for nome in sorted(usados):
        origem = RAIZ / "sons" / nome
        if not origem.exists():
            print(f"  AVISO: som {nome} não encontrado, pulando")
            continue
        destino = DESTINO / "sons" / (origem.stem + ".ogg")
        subprocess.run([ffmpeg, "-loglevel", "error", "-y", "-i", str(origem),
                        "-c:a", "libvorbis", "-q:a", "4", str(destino)], check=True)
        print(f"  som {nome} -> {destino.name} ({destino.stat().st_size / 1024:.0f} KB)")


def carregar_logo():
    """Logo sem o fundo claro e recortada, pronta para o favicon e a tela inicial."""
    logo = remover_fundo_claro(pygame.image.load(RAIZ / "imagens" / LOGO))
    return logo.subsurface(logo.get_bounding_rect()).copy()


def caber_em_quadrado(img, lado):
    k = lado / max(img.get_size())
    menor = pygame.transform.smoothscale(img, (round(img.get_width() * k), round(img.get_height() * k)))
    quadrado = pygame.Surface((lado, lado), pygame.SRCALPHA)
    quadrado.blit(menor, menor.get_rect(center=(lado // 2, lado // 2)))
    return quadrado


def criar_favicon(logo):
    pygame.image.save(caber_em_quadrado(logo, 64), DESTINO / "favicon.png")


def rodar_pygbag(so_gerar):
    comando = [sys.executable, "-m", "pygbag", "--title", TITULO_PAGINA, "--app_name", "jackpot_inbec"]
    if so_gerar:
        comando.append("--build")
    comando.append(str(DESTINO))
    subprocess.run(comando, check=True, cwd=RAIZ)


def ajustar_pagina(logo):
    """Personaliza a página gerada pelo pygbag: fundo branco, idioma e a tela inicial da INBEC."""
    web = DESTINO / "build" / "web"

    # arquivos usados pela tela inicial (ferramentas/site/tela_inicial.html)
    pygame.image.save(caber_em_quadrado(logo, 240), web / "logo_inicial.png")
    (web / "fontes").mkdir(exist_ok=True)
    for peso in (600, 800, 900):
        shutil.copy2(RAIZ / "fontes" / f"Exo2-{peso}.ttf", web / "fontes")

    pagina = web / "index.html"
    html = pagina.read_text(encoding="utf-8")
    html = html.replace('document.body.style.background = "#7f7f7f"', 'document.body.style.background = "#ffffff"')
    html = html.replace('<html lang="en-us">', '<html lang="pt-BR">', 1)
    tela_inicial = TELA_INICIAL.read_text(encoding="utf-8")
    html = html.replace("</body>", tela_inicial + "\n</body>", 1)
    pagina.write_text(html, encoding="utf-8")


def main():
    so_gerar = "--build" in sys.argv
    if DESTINO.exists():
        shutil.rmtree(DESTINO)
    DESTINO.mkdir()

    print("Copiando código e fontes...")
    copiar_codigo()
    print("Reduzindo imagens...")
    copiar_imagens()
    print("Convertendo sons...")
    converter_sons()
    logo = carregar_logo()
    criar_favicon(logo)

    print("Empacotando com pygbag...")
    rodar_pygbag(so_gerar)
    if so_gerar:
        ajustar_pagina(logo)
        print(f"\nSite gerado em: {DESTINO / 'build' / 'web'}")


if __name__ == "__main__":
    main()
