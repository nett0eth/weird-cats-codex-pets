# PAUSE TO FIND YOUR WEIRD CAT — TikTok / Reels (vídeo #2)

- `PauseYourCat.mp4` — 1080×1920, 30 fps, 15 s, só SFX (tick a cada card + sting final + miado). A música entra no app.
- `PauseYourCat.tsrct` — projeto Tesseract editável; `.tesseract-work/build.py` recria tudo.
- Reaproveita a arte de `../launch-video/gpt/` (fundo, portal, stickers) e os 20 gatos "limpos" da coleção.

## Estrutura
| Tempo | O que acontece |
|---|---|
| 0–1,6 s | PAUSE THE VIDEO / TO FIND YOUR WEIRD CAT sobre o portal girando |
| 1,6–2,6 s | 4 cards lentos (0,25 s) pra pessoa entender o jogo |
| 2,6–12,6 s | 100 cards rápidos (0,1 s = 3 frames cada, ordem embaralhada) com PAUSE NOW! piscando |
| 12,6–15 s | congela num gato, flash, WHO DID YOU GET? / comment below |

Cada card: WEIRD CAT #NN, nome e personalidade. Personalidades editáveis na lista `CATS` do `build.py`.

## Legenda sugerida
```
pause the video. that's your weird cat 👾
who did you get? 👇

#weirdcats #pixelart #whichcatareyou #catsoftiktok #weirdcore
```
Comentário pra fixar: `i got ____. explain yourself.`
