#!/usr/bin/env bash
# Weird Cats TV ao vivo no X. Rodar como root num Ubuntu 22.04/24.04:
#   bash install.sh
# Pergunta a URL do servidor e a chave do X (não aparecem na tela e ficam só neste servidor).
set -euo pipefail
DIR=/opt/weirdcats-tv
PLAYLIST_URL="${PLAYLIST_URL:-https://raw.githubusercontent.com/nett0eth/weird-cats-codex-pets/claude/project-thread-ed91dz/tools/tv-live/playlist.txt}"
mkdir -p "$DIR/clips" /etc/weirdcats-tv
cd "$DIR"

echo "==> Instalando ffmpeg"
apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq ffmpeg curl >/dev/null

if [ ! -f playlist.txt ]; then
  [ -n "$PLAYLIST_URL" ] || { echo "Coloque playlist.txt em $DIR ou rode com PLAYLIST_URL=..."; exit 1; }
  curl -fsSL "$PLAYLIST_URL" -o playlist.txt
fi

if [ ! -f /etc/weirdcats-tv/stream.env ]; then
  echo "==> No X: Creator Studio > Live Studio > Sources. Copie os dois campos."
  read -rp  "Server URL (rtmp/rtmps): " SRV
  read -rsp "Stream key (não aparece na tela): " KEY; echo
  printf 'STREAM_URL=%s/%s\n' "${SRV%/}" "$KEY" > /etc/weirdcats-tv/stream.env
  chmod 600 /etc/weirdcats-tv/stream.env
fi

cat > "$DIR/build.sh" <<'B'
#!/usr/bin/env bash
# Baixa e padroniza cada vídeo (1080p30, H.264 4.5 Mbps, keyframe a cada 3 s, AAC 128k) e junta tudo em tv.mp4.
set -euo pipefail
cd /opt/weirdcats-tv
: > list.txt
n=0
grep -vE '^\s*(#|$)' playlist.txt | while read -r url; do
  n=$((n+1)); id=$(printf '%02d' "$n"); raw="clips/$id.src"; out="clips/$id.mp4"
  if [ ! -s "$out" ]; then
    echo "  [$id] $url"
    curl -fsSL "$url" -o "$raw"
    if ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$raw" | grep -q .; then
      AIN=(-i "$raw"); AMAP=(-map 0:v:0 -map 0:a:0)
    else
      AIN=(-i "$raw" -f lavfi -i anullsrc=r=44100:cl=stereo); AMAP=(-map 0:v:0 -map 1:a:0 -shortest)
    fi
    # GIF curto do GIPHY: repete por ~15 s
    LOOP=(); [[ "$url" == *giphy* ]] && LOOP=(-stream_loop 4)
    ffmpeg -nostdin -hide_banner -loglevel error -y "${LOOP[@]}" "${AIN[@]}" "${AMAP[@]}" \
      -vf "scale=1920:1080:force_original_aspect_ratio=decrease:flags=lanczos,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black,fps=30,format=yuv420p,setsar=1" \
      -c:v libx264 -preset veryfast -profile:v high -b:v 4500k -maxrate 4500k -bufsize 9000k \
      -g 90 -keyint_min 90 -sc_threshold 0 \
      -c:a aac -b:a 128k -ar 44100 -ac 2 -movflags +faststart "$out"
    rm -f "$raw"
  fi
  echo "file '$PWD/$out'" >> list.txt
done
ffmpeg -nostdin -hide_banner -loglevel error -y -f concat -safe 0 -i list.txt -c copy -movflags +faststart tv.new.mp4
mv tv.new.mp4 tv.mp4
echo "==> tv.mp4 pronto: $(ffprobe -v error -show_entries format=duration -of csv=p=0 tv.mp4 | cut -d. -f1) s"
B
chmod +x "$DIR/build.sh"

echo "==> Preparando os vídeos (leva alguns minutos)"
"$DIR/build.sh"

cat > /etc/systemd/system/weirdcats-tv.service <<'S'
[Unit]
Description=Weird Cats TV ao vivo no X
After=network-online.target
Wants=network-online.target

[Service]
EnvironmentFile=/etc/weirdcats-tv/stream.env
ExecStart=/usr/bin/ffmpeg -hide_banner -loglevel warning -re -stream_loop -1 -i /opt/weirdcats-tv/tv.mp4 -c copy -f flv ${STREAM_URL}
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
S

# O X corta cada live em 24 h: reinicia todo dia às 03:00 UTC (meia-noite em Brasília).
cat > /etc/systemd/system/weirdcats-tv-restart.service <<'S'
[Unit]
Description=Reinicio diario da Weird Cats TV
[Service]
Type=oneshot
ExecStart=/bin/systemctl restart weirdcats-tv.service
S
cat > /etc/systemd/system/weirdcats-tv-restart.timer <<'S'
[Unit]
Description=Reinicio diario da Weird Cats TV
[Timer]
OnCalendar=*-*-* 03:00:00 UTC
Persistent=false
[Install]
WantedBy=timers.target
S

systemctl daemon-reload
echo
echo "Pronto. Comandos:"
echo "  systemctl start weirdcats-tv      # liga a live"
echo "  systemctl stop weirdcats-tv       # desliga"
echo "  journalctl -u weirdcats-tv -f     # ver o que está acontecendo"
echo "  systemctl enable --now weirdcats-tv weirdcats-tv-restart.timer   # deixar 24/7 depois do teste"
