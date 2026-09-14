(() => {
  const CELL_WIDTH = 192;
  const CELL_HEIGHT = 208;
  const DIRECTION_COUNT = 16;
  const row = document.querySelector('#pet-row');
  const status = document.querySelector('#gallery-status');
  let pointer = null;
  let raf = 0;
  let pets = [];

  function setFrame(pet, frameRow, column) {
    pet.sprite.style.backgroundPosition = `${-column * CELL_WIDTH}px ${-frameRow * CELL_HEIGHT}px`;
  }

  function directionFromPointer(pet) {
    if (!pointer) return null;
    const rect = pet.link.getBoundingClientRect();
    const dx = pointer.x - (rect.left + rect.width / 2);
    const dy = pointer.y - (rect.top + rect.height * 0.42);
    if (Math.hypot(dx, dy) < 24) return null;
    const angle = (Math.atan2(dx, -dy) + Math.PI * 2) % (Math.PI * 2);
    return Math.round(angle / (Math.PI * 2 / DIRECTION_COUNT)) % DIRECTION_COUNT;
  }

  function showDirection(pet, direction) {
    if (direction === null) return setFrame(pet, 0, 6);
    setFrame(pet, direction < 8 ? 9 : 10, direction % 8);
  }

  function updateLook() {
    raf = 0;
    for (const pet of pets) if (!pet.reacting) showDirection(pet, directionFromPointer(pet));
  }

  function scheduleLook() {
    if (!raf) raf = requestAnimationFrame(updateLook);
  }

  function addHeart(pet) {
    const heart = document.createElement('span');
    heart.className = 'pet-card__heart';
    heart.textContent = '♥';
    heart.setAttribute('aria-hidden', 'true');
    heart.style.setProperty('--heart-x', `${38 + Math.random() * 24}%`);
    pet.link.append(heart);
    heart.addEventListener('animationend', () => heart.remove(), { once: true });
  }

  function petCharacter(pet) {
    pet.reacting = true;
    pet.link.classList.add('is-petted');
    addHeart(pet);
    const start = performance.now();
    const tick = (now) => {
      if (!pet.reacting) return;
      setFrame(pet, 3, Math.min(3, Math.floor((now - start) / 105)));
      if (now - start < 520) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
    window.setTimeout(() => {
      pet.reacting = false;
      pet.link.classList.remove('is-petted');
      showDirection(pet, directionFromPointer(pet));
    }, 650);
    status.textContent = `${pet.data.nickname} recebeu carinho ♥ A ficha foi aberta em outra aba.`;
  }

  function createCard(data) {
    const link = document.createElement('a');
    link.className = `pet-card${data.aura ? ' pet-card--aura' : ''}`;
    link.href = `./pet.html?id=${encodeURIComponent(data.id)}`;
    link.target = '_blank';
    link.rel = 'noreferrer';
    link.setAttribute('aria-label', `${data.nickname}: abrir ficha de instalação em outra aba`);
    link.innerHTML = `<span class="pet-card__number">${data.collectionNumber}</span><span class="pet-card__portrait" aria-hidden="true"><span class="pet-sprite" style="--sprite: url('${data.asset}')"></span><span class="pet-card__floor"></span></span><span class="pet-card__info"><strong>${data.nickname}</strong><small>VIEW PET ↗</small></span>`;
    const pet = { data, link, sprite: link.querySelector('.pet-sprite'), reacting: false };
    setFrame(pet, 0, 6);
    link.addEventListener('click', (event) => {
      petCharacter(pet);
      window.open(link.href, '_blank', 'noopener');
      event.preventDefault();
    });
    return pet;
  }

  fetch('./pets.json')
    .then((response) => { if (!response.ok) throw new Error('collection unavailable'); return response.json(); })
    .then((items) => {
      pets = items.map(createCard);
      row.replaceChildren(...pets.map((pet) => pet.link));
      status.textContent = 'Todos acompanham o cursor. Clique para fazer carinho e abrir a instalação.';
    })
    .catch(() => { status.textContent = 'Não foi possível carregar a coleção.'; });

  addEventListener('pointermove', (event) => { pointer = { x: event.clientX, y: event.clientY }; scheduleLook(); }, { passive: true });
  addEventListener('pointerleave', () => { pointer = null; scheduleLook(); });
  addEventListener('resize', scheduleLook, { passive: true });
})();
