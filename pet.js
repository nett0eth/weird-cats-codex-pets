(() => {
  const CELL_WIDTH = 192;
  const CELL_HEIGHT = 208;
  const REPO = 'nett0eth/weird-cats-codex-pets';
  const RELEASE = 'v1.0.0';
  const detail = document.querySelector('#pet-detail');
  const id = new URLSearchParams(location.search).get('id');
  let activePet = null;
  let pointer = null;
  let reacting = false;

  const releaseUrl = (pet) => `https://github.com/${REPO}/releases/download/${RELEASE}/${pet.package}`;
  function setFrame(row, column) { activePet.sprite.style.backgroundPosition = `${-column * CELL_WIDTH}px ${-row * CELL_HEIGHT}px`; }
  function updateLook() {
    if (!activePet || !pointer || reacting) return;
    const rect = activePet.stage.getBoundingClientRect();
    const dx = pointer.x - (rect.left + rect.width / 2);
    const dy = pointer.y - (rect.top + rect.height * 0.43);
    if (Math.hypot(dx, dy) < 24) return setFrame(0, 6);
    const direction = Math.round(((Math.atan2(dx, -dy) + Math.PI * 2) % (Math.PI * 2)) / (Math.PI * 2 / 16)) % 16;
    setFrame(direction < 8 ? 9 : 10, direction % 8);
  }
  function react() {
    if (!activePet) return;
    reacting = true;
    activePet.stage.classList.remove('is-petted');
    void activePet.stage.offsetWidth;
    activePet.stage.classList.add('is-petted');
    const start = performance.now();
    const tick = (now) => {
      if (!reacting) return;
      setFrame(3, Math.min(3, Math.floor((now - start) / 105)));
      if (now - start < 520) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
    window.setTimeout(() => { reacting = false; activePet.stage.classList.remove('is-petted'); setFrame(0, 6); updateLook(); }, 650);
  }
  function windowsCommand(pet) {
    const url = releaseUrl(pet);
    return `$pet = "${pet.id}"\n$zip = Join-Path $env:TEMP "$pet.zip"\n$dest = Join-Path $HOME ".codex\\pets\\$pet"\nInvoke-WebRequest "${url}" -OutFile $zip\nNew-Item -ItemType Directory -Force -Path $dest | Out-Null\nExpand-Archive -LiteralPath $zip -DestinationPath $dest -Force`;
  }
  function unixCommand(pet) {
    const url = releaseUrl(pet);
    return `pet="${pet.id}"\nzip="/tmp/$pet.zip"\ndest="$HOME/.codex/pets/$pet"\ncurl -L "${url}" -o "$zip"\nmkdir -p "$dest"\nunzip -o "$zip" -d "$dest"`;
  }
  function codexUrl(pet) {
    const prompt = `Install the Codex Pet ${pet.nickname} from ${releaseUrl(pet)} into $HOME/.codex/pets/${pet.id}. The ZIP contains pet.json and spritesheet.webp. Do not modify other pets. After installation, tell me to open Settings > Pets, select Refresh, and choose ${pet.nickname}.`;
    return `codex://new?prompt=${encodeURIComponent(prompt)}`;
  }
  function render(pet) {
    document.title = `${pet.nickname} · Weird Cats Codex Pet`;
    const traits = pet.traits.map((trait) => `<li>${trait}</li>`).join('');
    const slug = pet.nickname.toLowerCase().replace(/\s+/g, '-');
    detail.innerHTML = `<section class="detail-art detail-art--${slug}"><p class="eyebrow">${pet.collectionNumber}</p><button class="detail-stage" type="button" aria-label="Fazer carinho em ${pet.nickname}"><span class="detail-sprite" style="--sprite: url('${pet.asset}')" aria-hidden="true"></span><span class="detail-floor" aria-hidden="true"></span><span class="detail-pet-hint">CLICK TO PET ♥</span></button></section><section class="detail-copy"><img class="detail-name-art" src="${pet.nameArt}" alt="${pet.nickname}" /><p class="detail-description">${pet.description}</p><ul class="trait-list">${traits}</ul><article class="install-sheet"><div class="install-sheet__lead"><div><span class="install-sheet__step">READY TO MOVE IN</span><h1>Install ${pet.nickname}</h1></div><span class="format-badge">PET V2</span></div><a class="install-primary" href="${codexUrl(pet)}">INSTALL IN CODEX <span>↗</span></a><div class="command-tabs" role="tablist" aria-label="Sistema operacional"><button class="is-active" type="button" data-os="windows" role="tab" aria-selected="true">WINDOWS</button><button type="button" data-os="unix" role="tab" aria-selected="false">MAC / LINUX</button></div><div class="command-box"><pre><code id="install-command"></code></pre><button id="copy-command" type="button">COPY</button></div><div class="install-foot"><a class="download-link" href="${releaseUrl(pet)}" download>DOWNLOAD ZIP ↓</a><ol class="install-steps"><li>Execute o comando.</li><li>Abra Settings → Pets.</li><li>Refresh e escolha ${pet.nickname}.</li></ol></div></article></section>`;
    const command = detail.querySelector('#install-command');
    const tabs = [...detail.querySelectorAll('[data-os]')];
    const commands = { windows: windowsCommand(pet), unix: unixCommand(pet) };
    command.textContent = commands.windows;
    tabs.forEach((tab) => tab.addEventListener('click', () => {
      tabs.forEach((item) => { const selected = item === tab; item.classList.toggle('is-active', selected); item.setAttribute('aria-selected', String(selected)); });
      command.textContent = commands[tab.dataset.os];
    }));
    detail.querySelector('#copy-command').addEventListener('click', async (event) => {
      const button = event.currentTarget;
      await navigator.clipboard.writeText(command.textContent);
      button.textContent = 'COPIED ✓';
      setTimeout(() => { button.textContent = 'COPY'; }, 1400);
    });
    activePet = { stage: detail.querySelector('.detail-stage'), sprite: detail.querySelector('.detail-sprite') };
    setFrame(0, 6);
    activePet.stage.addEventListener('click', react);
  }
  fetch('./pets.json').then((response) => response.json()).then((pets) => render(pets.find((candidate) => candidate.id === id) || pets[0])).catch(() => { detail.innerHTML = '<p class="detail-loading">Não foi possível carregar este mascote.</p>'; });
  addEventListener('pointermove', (event) => { pointer = { x: event.clientX, y: event.clientY }; updateLook(); }, { passive: true });
})();
