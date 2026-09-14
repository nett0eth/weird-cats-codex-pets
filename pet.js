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
    const dy = pointer.y - (rect.top + rect.height * 0.42);
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
  function installCommand(pet) {
    return `Install ${pet.nickname} as a Codex Pet from ${releaseUrl(pet)}.`;
  }
  function render(pet) {
    document.title = `${pet.nickname} · Weird Cats Codex Pet`;
    const slug = pet.nickname.toLowerCase().replace(/\s+/g, '-');
    const command = installCommand(pet);
    detail.innerHTML = `<section class="detail-art detail-art--${slug}"><button class="detail-stage" type="button" aria-label="Pet ${pet.nickname}"><span class="detail-sprite" style="--sprite: url('${pet.asset}')" aria-hidden="true"></span><span class="detail-floor" aria-hidden="true"></span></button></section><section class="detail-copy"><h1 class="detail-name"><img src="./assets/art/ui/name-${slug}.png" alt="${pet.nickname}"></h1><img class="install-title" src="./assets/art/ui/title-install.png" alt="Install"><article class="install-sheet"><code class="install-command">${command}</code><button class="copy-command" type="button"><img src="./assets/art/ui/action-copy-command.png" alt="Copy command"></button></article></section>`;
    activePet = { stage: detail.querySelector('.detail-stage'), sprite: detail.querySelector('.detail-sprite') };
    setFrame(0, 6);
    activePet.stage.addEventListener('click', react);
    detail.querySelector('.copy-command').addEventListener('click', async (event) => {
      const button = event.currentTarget;
      try {
        await navigator.clipboard.writeText(command);
      } catch {
        const helper = document.createElement('textarea');
        helper.value = command;
        document.body.append(helper);
        helper.select();
        document.execCommand('copy');
        helper.remove();
      }
      button.innerHTML = '<img src="./assets/art/ui/action-copied.png" alt="Copied">';
      window.setTimeout(() => { button.innerHTML = '<img src="./assets/art/ui/action-copy-command.png" alt="Copy command">'; }, 1600);
    });
  }
  fetch('./pets.json').then((response) => response.json()).then((pets) => render(pets.find((candidate) => candidate.id === id) || pets[0])).catch(() => { detail.innerHTML = '<p class="detail-loading">This pet could not be loaded.</p>'; });
  addEventListener('pointermove', (event) => { pointer = { x: event.clientX, y: event.clientY }; updateLook(); }, { passive: true });
})();
