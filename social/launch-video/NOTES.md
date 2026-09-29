# Weird Cats — vídeo de lançamento (TikTok / Instagram)

- `WeirdCatsLaunch.mp4` — 1080×1920, 30 fps, 24 s, H.264 + AAC (só efeitos sonoros, pico −5.8 dBTP)
- `WeirdCatsLaunch.tsrct` — projeto Tesseract editável (88 camadas, todas nativas: texto, shapes, imagens, áudio)
- `Previews/` — filmstrip do vídeo final, filmstrip de layout, waveform da trilha
- `.tesseract-work/build.py` — receita que gera o projeto do zero (rode `python3 .tesseract-work/build.py`)

## Roteiro v2 (120 BPM, 1 beat = 0,5 s) — sem trilha, só SFX (a música entra no app)

| Tempo | Cena | Texto |
|---|---|---|
| 0–3 s | Celular neon vibra; notificações "incoming signal…", "psst. look up", "MEOW MEOW MEOW"; orelha do Glitch no rodapé da tela | SOMETHING'S IN YOUR PHONE... |
| 2,7–3 s | Glitch (GPT) sai do celular e atravessa a câmera; flash no drop | WE'RE OUT. |
| 5 / 7 s | Lucky e Smoke saem do celular e dançam no beat | THE WEIRD CATS → ESCAPED. OBVIOUSLY. |
| 8,7–9 s | Beanie (GPT) pula na câmera, flash ciano | AND WE'RE NOT LEAVING |
| 11 s | Rosto gigante do Glitch bate na tela e a câmera atravessa | LIVING IN YOUR FEED |
| 11–17 s | Caos: chuva de 20 gatos, strobe, câmera tremendo, feed rolando; de 13 s a 17 s o personagem gigante troca a cada beat | |
| 17–19 s | Break glitch com o rosto piscando | ERROR: NORMAL CAT NOT FOUND |
| 19–24 s | Logo, gatos em fila, pulo final com miado | NOW ON TIKTOK / + INSTAGRAM / FOLLOW US / TRUST THE COIN. |

Visual da marca: texto pixel com glow neon (sem contorno preto), celular escuro com borda rosa neon, fundo do quarto gerado no GPT.

## Assets

- Gatos: spritesheets oficiais do repo (`assets/*.webp` e os 25 pacotes em `plugins/weird-cats/assets/pets/`), ampliados 4× em nearest-neighbor. A dança troca frames reais dos sprites.
- Fundo: `assets/art/neon-room.mp4` em loop, cortado na vertical, com blur e push-in.
- Logo: `assets/art/weird-cats-official-logo.png`.
- Fontes: Press Start 2P e Silkscreen (Google Fonts, OFL). A Press Start 2P não tem maiúsculas acentuadas, então as frases com acento usam Silkscreen.
- SFX sintetizados localmente (`.tesseract-work/audio/`), sem samples de terceiros. Sem trilha.
- Ficaram fora da chuva: ash, ember, mocha e smoke-laptop (cigarro) e flip (boné do McDonald's). **O Smoke original ainda aparece com cigarro no sprite.**

## Arte do GPT (`gpt/`)

Usados: `background.png`, `cat-glitch-jump.png`, `cat-beanie-jump.png`, `cat-beanie-dance.png`, `cat-giant-face.png`. Qualquer um que faltar é pulado pelo build.

## Trocar por arte gerada no GPT (legado)

Salve os arquivos em `social/launch-video/gpt/` e rode o build de novo. O builder usa esses arquivos automaticamente:

**`gpt/background.png`** (substitui o fundo em vídeo)

> Vertical 9:16 pixel art illustration, 1080x1920. Cozy night bedroom lit by neon purple and hot pink, hanging plants, window with a glowing city skyline, cat posters, lava lamp, glossy reflective floor, same style as the attached reference (gallery-studio.png). The center of the frame is an open, darker, calm area of wall and floor (empty space for a phone and characters composited on top). Details pushed to the edges. No text, no logos, no characters.

**`gpt/phone.png`** (substitui o celular nativo; PNG com fundo transparente)

> A single modern smartphone seen straight from the front, upright, centered, chunky pixel art with thick black pixel outlines, matching the attached Weird Cats logo style. Hot pink body with small cyan and yellow sparkle stickers and one pink slime drip on a corner. The screen is a flat, uniform, solid black rounded rectangle (empty, no UI) so video can be placed inside it. Transparent background, no shadow, no text, portrait, phone fills ~90% of the height.

O conteúdo da tela é um track matte do tamanho 556×1100, centralizado. Se a tela do celular gerado tiver outra proporção, ajuste `SW`/`SH` no `build.py`.
