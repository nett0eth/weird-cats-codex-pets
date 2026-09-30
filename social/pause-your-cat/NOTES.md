# PAUSE TO FIND YOUR WEIRD CAT — TikTok / Reels (vídeo #2)

- `PauseYourCat.mp4` — 1080×1920, 30 fps, 15 s, só SFX (tique a cada card, sem som de fechamento). A música entra no app.
- `PauseYourCat.tsrct` — projeto Tesseract editável; `.tesseract-work/build.py` recria tudo.
- Reaproveita a arte de `../launch-video/gpt/` (fundo, portal, stickers) e os 20 gatos "limpos" da coleção.

## Estrutura (v2, loop)
| Tempo | O que acontece |
|---|---|
| 0–1,6 s | "PAUSE THE VIDEO / to find your weird cat" no topo, com os cards já rodando |
| 0–15 s | 150 cards (0,1 s = 3 frames cada, 19 gatos em ordem embaralhada), PAUSE NOW! piscando, stickers orbitando |

Sem card final e sem som de fechamento: portal, stickers e tique fecham ciclo exato em 15 s, então o vídeo repete sem emenda.
Frog Hat saiu da seleção (erro de traço no sprite). Cada card: WEIRD CAT #NN, nome e personalidade (lista `CATS` no `build.py`).

## Legenda sugerida
```
pause the video. that's your weird cat 👾
who did you get? 👇

#weirdcats #pixelart #whichcatareyou #catsoftiktok #weirdcore
```
Comentário pra fixar: `i got ____. explain yourself.`
