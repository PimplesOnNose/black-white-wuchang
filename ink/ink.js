/* ═══════════════════════════════════════════
   INK DESIGN SYSTEM — JavaScript
   墨韵设计系统 · 交互
   ═══════════════════════════════════════════ */

(function() {
  'use strict';

  // =============================================
  // 1. THEME TOGGLE
  // =============================================
  const root = document.documentElement;

  function getStoredTheme() {
    try { return localStorage.getItem('ink-theme'); } catch (e) { return null; }
  }

  function setStoredTheme(theme) {
    try { localStorage.setItem('ink-theme', theme); } catch (e) { /* ignore */ }
  }

  window.inkToggleTheme = function() {
    const current = root.getAttribute('data-theme');
    setTheme(current === 'light' ? 'dark' : 'light');
  };

  function setTheme(theme) {
    root.classList.add('ink-theme-transition');
    root.setAttribute('data-theme', theme);
    setStoredTheme(theme);
    // Sync the control-block dark toggle if present
    const darkToggle = document.getElementById('inkDarkModeToggle');
    if (darkToggle) darkToggle.classList.toggle('on', theme === 'dark');
    setTimeout(() => root.classList.remove('ink-theme-transition'), 600);
  }

  // Initialize from storage or system preference
  (function initTheme() {
    const saved = getStoredTheme();
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    setTheme(saved || (prefersDark ? 'dark' : 'light'));
  })();

  // Attach header toggle
  function initThemeButton() {
    const btn = document.getElementById('inkThemeToggle');
    if (btn) btn.addEventListener('click', window.inkToggleTheme);
  }

  // =============================================
  // 2. GENERIC TOGGLES
  // =============================================
  function initToggles() {
    document.querySelectorAll('.ink-toggle').forEach(t => {
      if (t.id === 'inkDarkModeToggle') return; // handled by theme
      t.addEventListener('click', () => {
        t.classList.toggle('on');
        if (t.id === 'inkTextureToggle') {
          document.body.classList.toggle('no-texture');
        }
      });
    });
  }

  // =============================================
  // 3. PILLS
  // =============================================
  function initPills() {
    document.querySelectorAll('.ink-pill').forEach(p => {
      p.addEventListener('click', () => p.classList.toggle('is-active'));
    });
    document.querySelectorAll('.ink-pill__close').forEach(close => {
      close.addEventListener('click', (e) => {
        e.stopPropagation();
        const pill = close.closest('.ink-pill');
        if (pill) pill.remove();
      });
    });
  }

  // =============================================
  // 4. ALERTS
  // =============================================
  window.inkDismissAlert = function(btn) {
    const alert = btn.closest('.ink-alert');
    if (alert) alert.style.display = 'none';
  };

  // =============================================
  // 5. MEDIA PLAYER
  // =============================================
  function initPlayer() {
    const playBtn = document.getElementById('inkPlayBtn');
    const playIcon = document.getElementById('inkPlayIcon');
    const trackFill = document.getElementById('inkTrackFill');
    const trackBar = document.getElementById('inkTrackBar');
    const currentTime = document.getElementById('inkCurrentTime');
    const likeBtn = document.getElementById('inkLikeBtn');
    const volumeSlider = document.getElementById('inkVolumeSlider');
    const volumeFill = document.getElementById('inkVolumeFill');

    if (!playBtn) return;

    let playing = false;
    let progress = 35;
    let playerInterval;

    function formatTime(s) {
      const m = Math.floor(s / 60);
      const sec = Math.floor(s % 60);
      return String(m).padStart(2, '0') + ':' + String(sec).padStart(2, '0');
    }

    playBtn.addEventListener('click', () => {
      playing = !playing;
      playIcon.textContent = playing ? '❚❚' : '▶';
      if (playing) {
        playerInterval = setInterval(() => {
          progress += 0.3;
          if (progress >= 100) {
            progress = 0;
            playing = false;
            playIcon.textContent = '▶';
            clearInterval(playerInterval);
          }
          if (trackFill) trackFill.style.width = progress + '%';
          if (currentTime) {
            const cur = Math.floor((progress / 100) * 390);
            currentTime.textContent = formatTime(cur);
          }
        }, 300);
      } else {
        clearInterval(playerInterval);
      }
    });

    if (trackBar) {
      trackBar.addEventListener('click', (e) => {
        const rect = e.currentTarget.getBoundingClientRect();
        progress = ((e.clientX - rect.left) / rect.width) * 100;
        if (trackFill) trackFill.style.width = progress + '%';
        if (currentTime) currentTime.textContent = formatTime(Math.floor((progress / 100) * 390));
      });
    }

    if (likeBtn) {
      likeBtn.addEventListener('click', () => {
        likeBtn.classList.toggle('liked');
        likeBtn.textContent = likeBtn.classList.contains('liked') ? '♥' : '♡';
      });
    }

    if (volumeSlider && volumeFill) {
      volumeSlider.addEventListener('click', (e) => {
        const rect = e.currentTarget.getBoundingClientRect();
        const pct = ((e.clientX - rect.left) / rect.width) * 100;
        volumeFill.style.width = pct + '%';
      });
    }

    // Playlist tabs
    document.querySelectorAll('.ink-player__playlist-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.ink-player__playlist-btn').forEach(b => b.classList.remove('is-active'));
        btn.classList.add('is-active');
      });
    });
  }

  // =============================================
  // 6. MENU
  // =============================================
  function initMenu() {
    document.querySelectorAll('.ink-menu__item').forEach(item => {
      item.addEventListener('click', () => {
        document.querySelectorAll('.ink-menu__item').forEach(i => i.classList.remove('is-active'));
        item.classList.add('is-active');
      });
    });
  }

  // =============================================
  // 7. SCROLL REVEAL + PROGRESS
  // =============================================
  function initScrollReveal() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed');
          entry.target.classList.add('ink-reveal--visible');
          // Animate progress fills inside
          if (entry.target.id === 'ink-controls') {
            setTimeout(() => {
              document.querySelectorAll('.ink-progress__fill[data-width]').forEach(f => {
                f.style.width = f.dataset.width + '%';
              });
              document.querySelectorAll('.ink-circular__fg[data-target]').forEach(c => {
                c.style.strokeDashoffset = c.dataset.target;
              });
            }, 300);
          }
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });

    document.querySelectorAll('.ink-section, .ink-reveal').forEach(el => {
      if (!el.classList.contains('ink-reveal')) el.classList.add('ink-reveal');
      observer.observe(el);
    });
  }

  // =============================================
  // 8. MOBILE MENU
  // =============================================
  function initMobileMenu() {
    const btn = document.querySelector('.ink-nav__mobile-btn');
    const menu = document.querySelector('.ink-nav-mobile');
    if (!btn || !menu) return;

    btn.addEventListener('click', () => {
      menu.classList.toggle('is-open');
    });

    menu.querySelectorAll('.ink-nav-mobile__link').forEach(link => {
      link.addEventListener('click', () => menu.classList.remove('is-open'));
    });
  }

  // =============================================
  // 9. KEYBOARD SHORTCUT
  // =============================================
  function initKeyboard() {
    document.addEventListener('keydown', (e) => {
      if (e.key === 't' && !e.target.matches('input, textarea')) {
        window.inkToggleTheme();
      }
    });
  }

  // =============================================
  // 10. INITIALIZE
  // =============================================
  document.addEventListener('DOMContentLoaded', function() {
    initThemeButton();
    initToggles();
    initPills();
    initPlayer();
    initMenu();
    initScrollReveal();
    initMobileMenu();
    initKeyboard();

    // Animate above-the-fold on load
    window.addEventListener('load', () => {
      setTimeout(() => {
        document.querySelectorAll('.ink-section, .ink-reveal').forEach(el => {
          const rect = el.getBoundingClientRect();
          if (rect.top < window.innerHeight) {
            el.classList.add('ink-reveal--visible');
          }
        });
      }, 100);
    });
  });

})();
