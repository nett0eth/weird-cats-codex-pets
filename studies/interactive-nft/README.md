# Interactive NFT study

Study for an interactive Weird Cats NFT: the cat stays in the collection frame (800x800, flat canonical background) and only turns its head toward the cursor or finger, using spritesheet rows 9 and 10 (16 directions).

- `demo/template3.html`: the demo page. Sprites are injected as data URIs at build time.
- `video/video.html`: scripted scene for the announce video. `render(t)` draws the frame at time t; `?f=h` gives 1920x1080, otherwise 1080x1920.
- `video/rend.js`: Playwright frame renderer (`node rend.js <dir> v|h full|preview`).
- `video/offsets.json`: per-frame paw anchor offsets, so no cat jumps while turning (Smoke moved up to 15 px).
- `video/music2.py`: placeholder chiptune. To be replaced by a real track.
