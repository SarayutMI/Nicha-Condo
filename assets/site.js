'use strict';

// Content is rendered in HTML. JavaScript adds filtering and image previews.
const search = document.getElementById('property-search');
const cards = Array.from(document.querySelectorAll('.property-card'));
const filters = Array.from(document.querySelectorAll('[data-filter]'));
let selectedRegion = 'all';
const normalize = value => value.normalize('NFKC').toLocaleLowerCase('th').trim();
function filterProperties() {
  const query = normalize(search ? search.value : '');
  let visible = 0;
  cards.forEach(card => {
    const matchesRegion = selectedRegion === 'all' || card.dataset.region === selectedRegion;
    const matchesQuery = query.split(/\s+/).every(word => normalize(card.dataset.search).includes(word));
    card.hidden = !(matchesRegion && matchesQuery);
    if (!card.hidden) visible += 1;
  });
  const count = document.getElementById('result-count');
  if (count) count.textContent = `พบ ${visible} รายการ`;
  const empty = document.getElementById('empty-results');
  if (empty) empty.hidden = visible !== 0;
}
filters.forEach(button => button.addEventListener('click', () => {
  selectedRegion = button.dataset.filter;
  filters.forEach(filter => {
    const active = filter === button;
    filter.classList.toggle('active', active);
    filter.setAttribute('aria-pressed', String(active));
  });
  filterProperties();
}));
if (search) search.addEventListener('input', filterProperties);

// A regional map remains usable as a list when JavaScript is unavailable.
const mapAreaButtons = Array.from(document.querySelectorAll('[data-map-area]'));
const mapProperties = Array.from(document.querySelectorAll('[data-map-property]'));
function selectMapArea(area, label) {
  let visible = 0;
  mapProperties.forEach(property => {
    property.hidden = area !== 'all' && property.dataset.mapProperty !== area;
    if (!property.hidden) visible++;
  });
  mapAreaButtons.forEach(button => {
    const active = button.dataset.mapArea === area;
    button.classList.toggle('is-active', active);
    button.setAttribute('aria-pressed', String(active));
  });
  document.querySelector('[data-map-title]').textContent = area === 'all' ? 'ที่พักทุกทำเล' : label;
  document.querySelector('[data-map-count]').textContent = `${visible} รายการ`;
  document.querySelector('.map-property-list').scrollTop = 0;
}
mapAreaButtons.forEach(button => {
  const select = event => {
    event.preventDefault();
    const title = button.querySelector('text');
    const label = title ? title.textContent : button.childNodes[0].textContent.trim();
    selectMapArea(button.dataset.mapArea, label);
  };
  button.addEventListener('click', select);
  if (button.tagName.toLowerCase() === 'a') button.addEventListener('keydown', event => {
    if (event.key === ' ' || event.key === 'Enter') select(event);
  });
});

const slideshow = document.querySelector('[data-slideshow]');
if (slideshow) {
  const slides = Array.from(slideshow.querySelectorAll('[data-hero-slide]'));
  const dots = Array.from(slideshow.querySelectorAll('[data-hero-dot]'));
  const pauseButton = slideshow.querySelector('[data-hero-pause]');
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let index = 0, timer = null, paused = motion.matches;
  function showSlide(next) {
    index = (next + slides.length) % slides.length;
    slides.forEach((slide, number) => {
      const active = number === index;
      slide.classList.toggle('is-active', active);
      slide.setAttribute('aria-hidden', String(!active));
      slide.querySelector('a').tabIndex = active ? 0 : -1;
      dots[number].classList.toggle('is-active', active);
      dots[number].setAttribute('aria-pressed', String(active));
    });
    slideshow.querySelector('[data-hero-counter]').textContent = `${index + 1} / ${slides.length}`;
  }
  function schedule() {
    clearInterval(timer);
    if (!paused && !document.hidden && !slideshow.matches(':hover') && !slideshow.contains(document.activeElement)) {
      timer = setInterval(() => showSlide(index + 1), 6000);
    }
  }
  function renderPause() {
    pauseButton.textContent = paused ? 'เล่นภาพ ▶' : 'หยุดภาพ Ⅱ';
    pauseButton.setAttribute('aria-label', paused ? 'เล่นสไลด์อัตโนมัติ' : 'หยุดสไลด์อัตโนมัติ');
    pauseButton.setAttribute('aria-pressed', String(paused));
    schedule();
  }
  slideshow.querySelector('.hero-slide-controls').hidden = false;
  slideshow.querySelector('[data-hero-prev]').addEventListener('click', () => { showSlide(index - 1); schedule(); });
  slideshow.querySelector('[data-hero-next]').addEventListener('click', () => { showSlide(index + 1); schedule(); });
  dots.forEach((dot, number) => dot.addEventListener('click', () => { showSlide(number); schedule(); }));
  pauseButton.addEventListener('click', () => { paused = !paused; renderPause(); });
  slideshow.addEventListener('mouseenter', schedule);
  slideshow.addEventListener('mouseleave', schedule);
  slideshow.addEventListener('focusin', schedule);
  slideshow.addEventListener('focusout', () => setTimeout(schedule, 0));
  document.addEventListener('visibilitychange', schedule);
  motion.addEventListener('change', event => { paused = event.matches; renderPause(); });
  showSlide(0);
  renderPause();
}

// Progressive galleries expose every image without fetching every full-size original.
document.querySelectorAll('[data-gallery]').forEach(gallery => {
  const photos = Array.from(gallery.querySelectorAll('.gallery-card'));
  const categoryButtons = Array.from(gallery.querySelectorAll('[data-gallery-filter]'));
  const more = gallery.querySelector('[data-gallery-more]');
  const count = gallery.querySelector('.gallery-count');
  let selectedCategory = 'all';
  let expanded = false;
  const controls = gallery.querySelector('[data-gallery-controls]');
  if (controls) controls.hidden = false;
  const previewLimit = Number(gallery.dataset.galleryLimit) || 16;
  function renderGallery() {
    const matches = photos.filter(photo => selectedCategory === 'all' || photo.dataset.photoCategory === selectedCategory);
    const visible = expanded ? matches.length : Math.min(previewLimit, matches.length);
    const shown = new Set(matches.slice(0, visible));
    photos.forEach(photo => { photo.hidden = !shown.has(photo); });
    gallery.dataset.selectedCategory = selectedCategory;
    count.textContent = `แสดง ${visible} จาก ${matches.length} ภาพ`;
    more.hidden = visible === matches.length;
    more.textContent = `ดูภาพทั้งหมด (${matches.length} ภาพ)`;
  }
  categoryButtons.forEach(button => button.addEventListener('click', () => {
    selectedCategory = button.dataset.galleryFilter;
    expanded = false;
    categoryButtons.forEach(item => {
      const active = item === button;
      item.classList.toggle('active', active);
      item.setAttribute('aria-pressed', String(active));
    });
    renderGallery();
  }));
  more.addEventListener('click', () => { expanded = true; renderGallery(); });
  renderGallery();
});

const lightbox = document.getElementById('lightbox');
if (lightbox && typeof lightbox.showModal === 'function') {
  const image = lightbox.querySelector('img');
  const caption = lightbox.querySelector('p');
  const source = lightbox.querySelector('.lightbox-source');
  const previous = lightbox.querySelector('.lightbox-prev');
  const next = lightbox.querySelector('.lightbox-next');
  let sequence = [];
  let currentIndex = 0;
  function showPhoto() {
    const button = sequence[currentIndex];
    image.src = button.dataset.fullImage;
    image.alt = button.querySelector('img').alt;
    image.dataset.photoCategory = button.closest('.gallery-card').dataset.photoCategory;
    caption.textContent = `${image.alt} · ${currentIndex + 1} / ${sequence.length}`;
    source.hidden = !button.dataset.sourceUrl;
    if (button.dataset.sourceUrl) source.href = button.dataset.sourceUrl;
    else source.removeAttribute('href');
    previous.hidden = next.hidden = sequence.length < 2;
  }
  function movePhoto(direction) {
    currentIndex = (currentIndex + direction + sequence.length) % sequence.length;
    showPhoto();
  }
  document.querySelectorAll('[data-full-image]').forEach(button => {
    button.addEventListener('click', () => {
      const gallery = button.closest('[data-gallery]');
      const category = gallery.dataset.selectedCategory || 'all';
      sequence = Array.from(gallery.querySelectorAll('[data-full-image]')).filter(item => category === 'all' || item.closest('.gallery-card').dataset.photoCategory === category);
      currentIndex = sequence.indexOf(button);
      showPhoto();
      lightbox.showModal();
    });
  });
  previous.addEventListener('click', () => movePhoto(-1));
  next.addEventListener('click', () => movePhoto(1));
  lightbox.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault();
      movePhoto(event.key === 'ArrowLeft' ? -1 : 1);
    }
  });
  lightbox.querySelector('.lightbox-close').addEventListener('click', () => lightbox.close());
  lightbox.addEventListener('click', event => {
    const rect = lightbox.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) lightbox.close();
  });
} else {
  document.querySelectorAll('[data-full-image]').forEach(button => {
    button.addEventListener('click', () => window.open(button.dataset.fullImage, '_blank', 'noopener'));
  });
}

const copyButton = document.getElementById('copy-inquiry');
if (copyButton) copyButton.addEventListener('click', async () => {
  const message = document.getElementById('inquiry-message');
  const status = document.getElementById('copy-status');
  try {
    if (!navigator.clipboard || !window.isSecureContext) throw new Error('Clipboard unavailable');
    await navigator.clipboard.writeText(message.value);
    status.textContent = 'คัดลอกแล้ว เปิด LINE แล้ววางข้อความเพื่อส่งให้ผู้ดูแล';
  } catch (_) {
    message.focus();
    message.select();
    status.textContent = 'เลือกข้อความแล้ว กดคัดลอกบนอุปกรณ์ของคุณ แล้วนำไปส่งใน LINE';
  }
});
