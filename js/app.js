/* ═══════════════════════════════════════════════════════════
   黑白无常 · The Impermanence — application logic
   Bilingual story reader: English / Simplified Chinese + pinyin,
   pre-rendered narration, optional autoplay.
   ═══════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  const $  = (sel, root) => (root || document).querySelector(sel);
  const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));

  /* ── State ─────────────────────────────────────────────── */
  const STATE = {
    pages: [],
    current: 0,
    lang: 'en',
    autoplay: false,
    isPlaying: false,
  };

  const I18N = {
    en: {
      prev: 'Prev', next: 'Next', autoplay: 'Autoplay',
      begin: 'Begin', replay: 'Replay',
      startNote: 'Press Begin to start the tale. Turn on Autoplay for narration.',
    },
    zh: {
      prev: '上页', next: '下页', autoplay: '自动播放',
      begin: '开始', replay: '重听',
      startNote: '按下开始进入故事。开启自动播放，聆听旁白。',
    },
  };

  /* ── Load story (works on file:// and http://) ─────────── */
  function loadStory() {
    if (window.location.protocol === 'file:') {
      return new Promise((resolve, reject) => {
        const s = document.createElement('script');
        s.type = 'application/json';
        s.src = 'content/story.json';
        s.onload = () => {
          try { resolve(JSON.parse(s.textContent)); } catch (e) { reject(e); }
          s.remove();
        };
        s.onerror = () => reject(new Error('Failed to load content/story.json'));
        document.head.appendChild(s);
      });
    }
    return fetch('content/story.json').then((r) => {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    });
  }

  /* ── Render ────────────────────────────────────────────── */
  function buildPage(pg, index) {
    const sec = document.createElement('section');
    sec.className = 'bww-page';
    sec.dataset.pageId = pg.id;
    sec.dataset.index = String(index);
    sec.hidden = index !== 0;

    const wrap = document.createElement('div');
    wrap.className = 'bww-page__image-wrap';

    const img = document.createElement('img');
    img.className = 'bww-page__image';
    img.src = pg.image;
    img.alt = pg.alt_en || pg.title_en;
    img.loading = index === 0 ? 'eager' : 'lazy';
    img.fetchPriority = index === 0 ? 'high' : 'auto';
    wrap.appendChild(img);

    const text = document.createElement('div');
    text.className = 'bww-page__text';

    const header = document.createElement('div');
    header.className = 'ink-section-header';

    const num = document.createElement('div');
    num.className = 'ink-section-num';
    num.textContent = pg.section_numeral || '';
    num.hidden = !pg.section_numeral;

    const group = document.createElement('div');
    group.className = 'ink-section-title-group';

    const label = document.createElement('div');
    label.className = 'ink-section-label';
    label.dataset.field = 'label';

    const title = document.createElement('h2');
    title.className = 'ink-section-title';
    title.dataset.field = 'title';

    group.appendChild(label);
    group.appendChild(title);
    header.appendChild(num);
    header.appendChild(group);

    const bodyEn = document.createElement('p');
    bodyEn.className = 'bww-body';
    bodyEn.dataset.lang = 'en';
    bodyEn.setAttribute('lang', 'en');
    bodyEn.textContent = pg.body_en;

    const bodyZh = document.createElement('p');
    bodyZh.className = 'bww-body bww-body--zh';
    bodyZh.dataset.lang = 'zh';
    bodyZh.setAttribute('lang', 'zh-CN');
    bodyZh.hidden = true;
    bodyZh.textContent = pg.body_zh;

    const pinyin = document.createElement('p');
    pinyin.className = 'bww-pinyin';
    pinyin.dataset.lang = 'pinyin';
    pinyin.setAttribute('lang', 'zh-Latn-pinyin');
    pinyin.hidden = true;
    pinyin.textContent = pg.body_pinyin;

    text.appendChild(header);
    text.appendChild(bodyEn);
    text.appendChild(bodyZh);
    text.appendChild(pinyin);

    sec.appendChild(wrap);
    sec.appendChild(text);

    /* Landing / epilogue hero actions */
    if (pg.id === '00' || pg.id === '10') {
      const actions = document.createElement('div');
      actions.className = 'bww-hero-actions';

      const primary = document.createElement('button');
      primary.className = 'ink-btn ink-btn--primary';
      primary.dataset.heroAction = pg.id === '00' ? 'begin' : 'replay';

      const note = document.createElement('div');
      note.className = 'bww-hero-note';
      note.dataset.i18n = 'startNote';
      if (pg.id !== '00') note.hidden = true;

      actions.appendChild(primary);
      actions.appendChild(note);
      text.appendChild(actions);
    }

    return sec;
  }

  function renderAllPages() {
    const stage = $('#bwwStage');
    stage.innerHTML = '';
    STATE.pages.forEach((pg, i) => stage.appendChild(buildPage(pg, i)));
    $('#bwwTotalNum').textContent = String(STATE.pages.length);
  }

  function getPageEl(index) {
    return $('.bww-page[data-index="' + index + '"]');
  }

  function renderPage(index) {
    STATE.current = index;
    $$('.bww-page').forEach((el) => {
      el.hidden = Number(el.dataset.index) !== index;
    });
    const el = getPageEl(index);
    if (el) {
      el.style.animation = 'none';
      void el.offsetWidth;          // restart ink-bloom
      el.style.animation = '';
    }
    updatePageMarker();
    updateProgress();
  }

  /* ── Language ──────────────────────────────────────────── */
  function setLang(lang) {
    STATE.lang = lang;
    document.documentElement.lang = lang === 'en' ? 'en' : 'zh-CN';
    try { localStorage.setItem('bww-lang', lang); } catch (e) { /* ignore */ }

    $$('.bww-lang-btn').forEach((b) => {
      const on = b.dataset.lang === lang;
      b.classList.toggle('is-active', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });

    $$('.bww-page').forEach((el) => syncPageTextForLang(el, lang));
    syncHeroActions(lang);
    syncI18n(lang);
    updateAudioSrc();

    if (STATE.isPlaying) restartAudio();
  }

  function syncPageTextForLang(el, lang) {
    const idx = Number(el.dataset.index);
    const pg = STATE.pages[idx];
    if (!pg) return;

    el.dataset.langActive = lang;

    const label = $('[data-field="label"]', el);
    const title = $('[data-field="title"]', el);
    const bodyEn = $('.bww-body[data-lang="en"]', el);
    const bodyZh = $('.bww-body[data-lang="zh"]', el);
    const pinyin = $('.bww-pinyin[data-lang="pinyin"]', el);

    if (lang === 'zh') {
      label.textContent = pg.section_label_zh || '';
      title.textContent = pg.title_zh;
      bodyEn.hidden = true;
      bodyZh.hidden = false;
      pinyin.hidden = false;
    } else {
      label.textContent = pg.section_label_en || '';
      title.textContent = pg.title_en;
      bodyEn.hidden = false;
      bodyZh.hidden = true;
      pinyin.hidden = true;
    }

    const img = $('.bww-page__image', el);
    if (img) img.alt = lang === 'zh' ? (pg.alt_zh || pg.title_zh) : (pg.alt_en || pg.title_en);
  }

  function syncHeroActions(lang) {
    $$('[data-hero-action]').forEach((btn) => {
      const kind = btn.dataset.heroAction;
      btn.textContent = I18N[lang][kind] || kind;
    });
    const note = $('[data-i18n="startNote"]');
    if (note) note.textContent = I18N[lang].startNote;
  }

  function syncI18n(lang) {
    $$('[data-i18n]').forEach((el) => {
      const key = el.dataset.i18n;
      if (I18N[lang][key]) el.textContent = I18N[lang][key];
    });
  }

  /* ── Audio ─────────────────────────────────────────────── */
  function getAudio() { return $('#bwwAudio'); }

  function currentPage() { return STATE.pages[STATE.current]; }

  function updateAudioSrc() {
    const audio = getAudio();
    const pg = currentPage();
    if (!pg) return;
    audio.src = STATE.lang === 'en' ? pg.audio.en : pg.audio.zh;
    audio.load();
  }

  function playCurrent() {
    const audio = getAudio();
    const p = audio.play();
    if (p && p.catch) p.catch(() => { /* autoplay policy etc. */ });
  }

  function pauseCurrent() {
    getAudio().pause();
  }

  function restartAudio() {
    const audio = getAudio();
    audio.currentTime = 0;
    audio.play().catch(() => { /* ignore */ });
  }

  function updatePlayButton() {
    const icon = $('.bww-play-icon');
    const btn = $('#bwwPlay');
    if (!icon || !btn) return;
    icon.textContent = STATE.isPlaying ? '❚❚' : '▶';
    btn.setAttribute('aria-label', STATE.isPlaying
      ? (STATE.lang === 'zh' ? '暂停' : 'Pause narration')
      : (STATE.lang === 'zh' ? '播放' : 'Play narration'));
  }

  /* ── Autoplay ──────────────────────────────────────────── */
  function toggleAutoplay() {
    STATE.autoplay = !STATE.autoplay;
    updateAutoplayButton();
    try { localStorage.setItem('bww-autoplay', STATE.autoplay ? '1' : '0'); } catch (e) { /* ignore */ }
    if (STATE.autoplay && !STATE.isPlaying) playCurrent();
  }

  function updateAutoplayButton() {
    const btn = $('#bwwAutoplay');
    if (!btn) return;
    btn.classList.toggle('is-on', STATE.autoplay);
    btn.setAttribute('aria-pressed', STATE.autoplay ? 'true' : 'false');
    const icon = $('.bww-autoplay-icon', btn);
    if (icon) icon.textContent = STATE.autoplay ? '●' : '◐';
  }

  /* ── Navigation ────────────────────────────────────────── */
  function next() {
    if (STATE.current < STATE.pages.length - 1) {
      pauseCurrent();
      STATE.current += 1;
      renderPage(STATE.current);
      updateAudioSrc();
      if (STATE.autoplay) playCurrent();
    }
  }

  function prev() {
    if (STATE.current > 0) {
      pauseCurrent();
      STATE.current -= 1;
      renderPage(STATE.current);
      updateAudioSrc();
      if (STATE.autoplay) playCurrent();
    }
  }

  function jumpTo(index) {
    pauseCurrent();
    STATE.current = Math.max(0, Math.min(STATE.pages.length - 1, index));
    renderPage(STATE.current);
    updateAudioSrc();
    if (STATE.autoplay) playCurrent();
  }

  function updatePageMarker() {
    $('#bwwCurNum').textContent = String(STATE.current + 1);
  }

  function updateProgress() {
    const total = STATE.pages.length;
    const pct = total > 1 ? (STATE.current / (total - 1)) * 100 : 0;
    $('#bwwProgressFill').style.width = pct + '%';
  }

  /* ── UI bindings ───────────────────────────────────────── */
  function bindUI() {
    $('#bwwPlay').addEventListener('click', () => {
      if (STATE.isPlaying) pauseCurrent();
      else playCurrent();
    });

    $('#bwwNext').addEventListener('click', next);
    $('#bwwPrev').addEventListener('click', prev);
    $('#bwwAutoplay').addEventListener('click', toggleAutoplay);

    $$('.bww-lang-btn').forEach((b) => b.addEventListener('click', () => setLang(b.dataset.lang)));

    $('[data-action="restart"]').addEventListener('click', (e) => { e.preventDefault(); jumpTo(0); });

    document.addEventListener('click', (e) => {
      const hero = e.target.closest('[data-hero-action]');
      if (!hero) return;
      if (hero.dataset.heroAction === 'begin') jumpTo(1);
      if (hero.dataset.heroAction === 'replay') jumpTo(0);
    });

    document.addEventListener('keydown', onKey);
  }

  function bindAudioEvents() {
    const audio = getAudio();

    audio.addEventListener('play', () => { STATE.isPlaying = true; updatePlayButton(); });
    audio.addEventListener('pause', () => { STATE.isPlaying = false; updatePlayButton(); });
    audio.addEventListener('ended', () => {
      STATE.isPlaying = false;
      if (STATE.autoplay && STATE.current < STATE.pages.length - 1) {
        STATE.current += 1;
        renderPage(STATE.current);
        updateAudioSrc();
        playCurrent();
      } else if (STATE.autoplay) {
        STATE.autoplay = false;
        updateAutoplayButton();
      }
    });
    audio.addEventListener('error', () => { /* keep going; user can still read */ });
  }

  function onKey(e) {
    const t = e.target;
    const editable = t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable;
    if (editable) return;
    if (e.key === ' ') {
      e.preventDefault();
      STATE.isPlaying ? pauseCurrent() : playCurrent();
    } else if (e.key === 'ArrowRight') next();
    else if (e.key === 'ArrowLeft') prev();
    else if (e.key === 'l' || e.key === 'L') setLang(STATE.lang === 'en' ? 'zh' : 'en');
    // 't' handled by ink.js
  }

  /* ── Init ──────────────────────────────────────────────── */
  async function init() {
    /* Canonical mood: dark theme unless the user already chose. */
    try {
      if (!localStorage.getItem('ink-theme')) document.documentElement.setAttribute('data-theme', 'dark');
    } catch (e) { /* ignore */ }

    let story;
    try {
      story = await loadStory();
    } catch (err) {
      const stage = $('#bwwStage');
      stage.innerHTML = '<div class="bww-page__text" style="padding-top:4rem;text-align:center">' +
        '<p class="bww-body">Unable to load story.json. Serve this folder over HTTP (e.g. <code>python -m http.server</code>) and reload.</p></div>';
      return;
    }

    STATE.pages = story.pages || [];

    renderAllPages();

    /* Restore preferences */
    let savedLang = 'en';
    let savedAutoplay = false;
    try {
      savedLang = localStorage.getItem('bww-lang') || 'en';
      savedAutoplay = localStorage.getItem('bww-autoplay') === '1';
    } catch (e) { /* ignore */ }

    bindUI();
    bindAudioEvents();

    setLang(savedLang === 'zh' ? 'zh' : 'en');
    STATE.autoplay = savedAutoplay;
    updateAutoplayButton();

    renderPage(0);
    updateAudioSrc();
  }

  document.addEventListener('DOMContentLoaded', init);
})();
