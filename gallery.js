(() => {
  const CELL_WIDTH = 192;
  const CELL_HEIGHT = 208;
  const DIRECTION_COUNT = 16;
  const row = document.querySelector('#pet-row');
  const status = document.querySelector('#gallery-status');
  let pointer = null;
  let raf = 0;
  let pets = [];
  let speakingPet = null;

  function setFrame(pet, frameRow, column) {
    pet.sprite.style.backgroundPosition = `${-column * CELL_WIDTH}px ${-frameRow * CELL_HEIGHT}px`;
  }

  function directionFromPointer(pet) {
    if (!pointer) return null;
    const rect = pet.root.getBoundingClientRect();
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
    heart.className = 'pet-piece__heart';
    heart.textContent = '♥';
    heart.setAttribute('aria-hidden', 'true');
    heart.style.setProperty('--heart-x', `${38 + Math.random() * 24}%`);
    pet.root.append(heart);
    heart.addEventListener('animationend', () => heart.remove(), { once: true });
  }

  function petCharacter(pet) {
    pet.reacting = true;
    pet.root.classList.add('is-petted');
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
      pet.root.classList.remove('is-petted');
      showDirection(pet, directionFromPointer(pet));
    }, 650);
    status.textContent = `${pet.data.nickname} received some affection ♥`;
  }

  function closeSpeech(pet) {
    pet.root.classList.remove('is-speaking');
    pet.bubble.hidden = true;
    pet.button.setAttribute('aria-expanded', 'false');
    if (speakingPet === pet) speakingPet = null;
  }

  function openSpeech(pet) {
    if (speakingPet && speakingPet !== pet) closeSpeech(speakingPet);
    const shouldOpen = !pet.root.classList.contains('is-speaking');
    if (!shouldOpen) return closeSpeech(pet);
    pet.root.classList.add('is-speaking');
    pet.bubble.hidden = false;
    pet.button.setAttribute('aria-expanded', 'true');
    speakingPet = pet;
    status.textContent = `${pet.data.nickname} has something weird to say.`;
  }

  function createPiece(data, index) {
    const root = document.createElement('article');
    const slug = data.nickname.toLowerCase().replace(/\s+/g, '-');
    root.className = `pet-piece pet-piece--${slug}`;
    root.style.setProperty('--piece-index', index);
    root.innerHTML = `<div class="pet-piece__speech" hidden><img class="pet-piece__signal" src="./assets/art/ui/signal-${index + 1}.png" alt="Signal 0${index + 1}"><img class="pet-piece__quote" src="./assets/art/ui/quote-${slug}.png" alt="${data.quote}"><a class="pet-piece__install" href="./pet.html?id=${encodeURIComponent(data.id)}" aria-label="Install ${data.nickname}"><img src="./assets/art/ui/action-install.png" alt="Install"></a></div><button class="pet-piece__pet" type="button" aria-label="Pet ${data.nickname} and hear what they say" aria-expanded="false"><span class="pet-piece__portrait" aria-hidden="true"><span class="pet-sprite" style="--sprite: url('${data.asset}')"></span><span class="pet-piece__shadow"></span></span></button><div class="pet-piece__identity"><img src="./assets/art/ui/name-${slug}.png" alt="${data.nickname}"></div>`;
    const pet = { data, root, sprite: root.querySelector('.pet-sprite'), button: root.querySelector('.pet-piece__pet'), bubble: root.querySelector('.pet-piece__speech'), reacting: false };
    setFrame(pet, 0, 6);
    pet.button.addEventListener('click', () => { petCharacter(pet); openSpeech(pet); });
    return pet;
  }

  fetch('./pets.json')
    .then((response) => { if (!response.ok) throw new Error('collection unavailable'); return response.json(); })
    .then((items) => {
      pets = items.map(createPiece);
      row.replaceChildren(...pets.map((pet) => pet.root));
      status.textContent = 'They all follow your cursor.';
    })
    .catch(() => { status.textContent = 'The collection could not be loaded.'; });

  addEventListener('pointermove', (event) => { pointer = { x: event.clientX, y: event.clientY }; scheduleLook(); }, { passive: true });
  addEventListener('pointerleave', () => { pointer = null; scheduleLook(); });
  addEventListener('resize', scheduleLook, { passive: true });
  addEventListener('click', (event) => {
    if (speakingPet && !speakingPet.root.contains(event.target)) closeSpeech(speakingPet);
  });
  addEventListener('keydown', (event) => { if (event.key === 'Escape' && speakingPet) closeSpeech(speakingPet); });
})();
