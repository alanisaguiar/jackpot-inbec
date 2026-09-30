"""Transforma o site gerado em um app instalável que funciona sem internet (PWA).

Chamado pelo gerar_site.py depois do pygbag. Cria, dentro de build_web/build/web:
  - manifest.json         nome, ícones, orientação e modo tela cheia do app
  - icone-192/512.png      ícones do app (logo da INBEC sobre fundo branco)
  - sw.js                  service worker: guarda todos os arquivos do jogo no aparelho
e liga tudo isso no index.html.

Atenção: o pygbag baixa o "motor" do Python (cpython, pygame etc.) de um servidor
externo (a CDN abaixo). Para o jogo abrir offline, esses arquivos também precisam
ficar guardados, então eles estão listados em ARQUIVOS_CDN. A lista vale para o
pygbag 0.9.3 (versão fixada em requirements-site.txt). Se um dia o pygbag for
atualizado, é preciso refazer a lista: abra o site, veja na aba "Rede" (F12) quais
arquivos vêm de pygame-web.github.io e atualize aqui.
"""

import hashlib
import json

import pygame

CDN = "https://pygame-web.github.io/cdn/"
ARQUIVOS_CDN = [
    "0.9.3/pythons.js",
    "0.9.3/cpython312/main.js",
    "0.9.3/cpython312/main.wasm",
    "0.9.3/cpython312/main.data",
    "0.9.3/cpythonrc.py",
    "0.9.3/empty.html",
    "0.9.3/empty.ogg",
    "index-0.9.3-cp312.json",
    "cp312/pygame_ce-2.5.7-cp312-cp312-wasm32_bi_emscripten.whl",
    "vtx.js",
    "vt/xterm.js",
    "vt/xterm.css",
    "vt/xterm-addon-image.js",
]

# arquivos do próprio site que o jogo usa (relativos à pasta do site)
ARQUIVOS_LOCAIS = [
    "./",
    "index.html",
    "build_web.tar.gz",
    "favicon.png",
    "logo_inicial.png",
    "fontes/Exo2-600.ttf",
    "fontes/Exo2-800.ttf",
    "fontes/Exo2-900.ttf",
    "manifest.json",
    "icone-192.png",
    "icone-512.png",
]

NOME_APP = "Jackpot Faculdade INBEC"
NOME_CURTO = "Jackpot INBEC"
COR_TEMA = "#1b2a5a"      # azul INBEC (barra de status / tela de abertura do app)

SW_MODELO = """\
// Service worker do Jackpot INBEC: gerado por ferramentas/pwa.py (não edite à mão).
// Na instalação guarda todos os arquivos do jogo; depois responde do que está guardado,
// para o jogo abrir mesmo sem internet.
const CACHE = "jackpot-inbec-__VERSAO__";
const ARQUIVOS = __ARQUIVOS__;

self.addEventListener("install", (evento) => {
    evento.waitUntil(
        caches.open(CACHE)
            .then((cache) => cache.addAll(ARQUIVOS))
            .then(() => self.skipWaiting())
    );
});

self.addEventListener("activate", (evento) => {
    // apaga os arquivos de versões antigas do jogo
    evento.waitUntil(
        caches.keys()
            .then((nomes) => Promise.all(nomes.filter((n) => n !== CACHE).map((n) => caches.delete(n))))
            .then(() => self.clients.claim())
    );
});

self.addEventListener("fetch", (evento) => {
    const pedido = evento.request;
    if (pedido.method !== "GET" || !pedido.url.startsWith("http")) return;

    evento.respondWith((async () => {
        const cache = await caches.open(CACHE);
        const guardado = await cache.match(pedido, { ignoreSearch: true });
        if (guardado) return guardado;
        try {
            const resposta = await fetch(pedido);
            if (resposta.status === 200) cache.put(pedido, resposta.clone());
            return resposta;
        } catch (erro) {
            if (pedido.mode === "navigate") {
                const pagina = await cache.match("./");
                if (pagina) return pagina;
            }
            throw erro;
        }
    })());
});
"""

TAGS_HEAD = f"""
    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="{COR_TEMA}">
    <link rel="apple-touch-icon" href="icone-192.png">
    <meta name="apple-mobile-web-app-title" content="{NOME_CURTO}">
    <script>
        if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js");
    </script>
"""


def _icone(logo, lado):
    """Logo centralizada sobre fundo branco, com margem para o recorte redondo do Android."""
    icone = pygame.Surface((lado, lado))
    icone.fill((255, 255, 255))
    alvo = int(lado * 0.62)
    k = alvo / max(logo.get_size())
    menor = pygame.transform.smoothscale(logo, (round(logo.get_width() * k), round(logo.get_height() * k)))
    icone.blit(menor, menor.get_rect(center=(lado // 2, lado // 2)))
    return icone


def _manifest():
    return {
        "name": NOME_APP,
        "short_name": NOME_CURTO,
        "lang": "pt-BR",
        "start_url": "./",
        "scope": "./",
        "display": "fullscreen",
        "orientation": "landscape",
        "background_color": "#ffffff",
        "theme_color": COR_TEMA,
        "icons": [
            {"src": "icone-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": "icone-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
            {"src": "icone-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
    }


def _versao(web):
    """Muda sempre que o conteúdo do jogo muda: assim os aparelhos baixam a versão nova."""
    h = hashlib.sha256()
    for nome in ("index.html", "build_web.tar.gz"):
        h.update((web / nome).read_bytes())
    return h.hexdigest()[:12]


def gerar_pwa(web, logo):
    """Cria manifest, ícones e service worker em `web` e os liga ao index.html."""
    for lado in (192, 512):
        pygame.image.save(_icone(logo, lado), web / f"icone-{lado}.png")
    (web / "manifest.json").write_text(json.dumps(_manifest(), ensure_ascii=False, indent=2), encoding="utf-8")

    pagina = web / "index.html"
    html = pagina.read_text(encoding="utf-8")
    html = html.replace("</head>", TAGS_HEAD + "</head>", 1)
    pagina.write_text(html, encoding="utf-8")

    arquivos = ARQUIVOS_LOCAIS + [CDN + a for a in ARQUIVOS_CDN]
    faltando = [a for a in ARQUIVOS_LOCAIS if a != "./" and not (web / a).exists()]
    if faltando:
        raise FileNotFoundError(f"arquivos do site não encontrados para o modo offline: {faltando}")
    sw = SW_MODELO.replace("__VERSAO__", _versao(web)).replace("__ARQUIVOS__", json.dumps(arquivos, indent=4))
    (web / "sw.js").write_text(sw, encoding="utf-8")
