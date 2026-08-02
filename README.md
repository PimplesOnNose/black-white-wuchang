# 黑白无常 · The Impermanence

> A bilingual, narrated folktale of two sworn brothers who became the Black and
> White Impermanence — the guardians between life and death.

**Live demo** → [https://PimplesOnNose.github.io/black-white-wuchang/](https://PimplesOnNose.github.io/black-white-wuchang/)

[中文版](README.zh-CN.md) · English

---

## The Story

In the court of the underworld, two brothers once swore to wait for each other
— come wind, come rain, come flood. One kept his word until the river took him.
The other, unwilling to live without his brother, followed. The Jade Emperor,
moved by their faith, appointed them the Black and White Impermanence: guides
who walk between life and death, rewarding the good and calling the guilty.

This app retells the tale across **11 illustrated, narrated pages** — a landing,
nine chapters, and an epilogue — written for students standing at the threshold
of adulthood.

## Features

- **Bilingual** — toggle `EN` / `中`; the Chinese view shows Simplified Chinese
  with a **separate pinyin block** (no ruby, tone marks included).
- **Narration** — 22 pre-rendered MP3s (11 pages × 2 languages), no live TTS.
  - English: `en-US-MichelleNeural` (female, normal speed)
  - Chinese: `zh-CN-YunjianNeural` (male, slowed 5%)
- **Autoplay** — plays the current page's narration and auto-advances when it ends.
- **Illustrations** — 11 black-and-white ink-wash paintings (1024×576),
  generated with FLUX and forced monochrome in CSS.
- **Theme** — light/dark toggle built on the Ink Line (墨韵) design system;
  dark is the default, to suit the ghost-tale mood.
- **Keyboard** — `Space` play/pause, `←` / `→` navigate, `L` language, `T` theme.
- **Accessible** — semantic HTML, `lang` attributes, `aria` labels, focus-friendly
  controls, `prefers-reduced-motion` support.

## Chapters

| # | Chapter | Page |
|---|---------|------|
| — | 序 · Prologue | Landing cover |
| 壹 | 幽冥 · The Underworld | Where souls are led |
| 贰 | 兄弟 · The Brothers | 谢必安 and 范无救 take an oath |
| 叁 | 桥 · The Bridge | The promise at 南台桥 |
| 肆 | 河 · The River | Rain, flood, and one who waited |
| 伍 | 殉 · The Hanging | The brother who would not live on |
| 陆 | 玉帝 · The Jade Emperor | Two ghosts, one decree |
| 柒 | 阴阳 · Yin and Yang | Black and White Impermanence |
| 捌 | 出巡 · The Procession | The festival walk |
| 玖 | 名 · The Names | 一见生财 · 天下太平 |
| — | 终 · Epilogue | What impermanence asks of us |

## Run it yourself

```bash
git clone https://github.com/PimplesOnNose/black-white-wuchang.git
cd black-white-wuchang
python3 -m http.server 8080
# open http://localhost:8080
```

No build step, no dependencies, no backend. The app even works when opened
directly as `index.html` over `file://`.

## Design Decisions

1. **One source of truth** — every word lives in `content/story.json`
   (English, Chinese, pinyin, and asset paths). The reader, the audio generator,
   and the image pipeline all read from it, so text can never drift from audio.
2. **Static, no-build architecture** — a single `index.html` plus the ink-design
   system and one `app.js`. Fast to load, trivial to host on GitHub Pages.
3. **Pre-rendered narration over live TTS** — audio is generated once with Edge
   TTS so every visitor hears the identical, deliberate reading; a male Chinese
   voice at −5% speed gives the tale a measured, solemn cadence.
4. **Pinyin as a separate block, not ruby** — Chinese learners often find ruby
   annotations visually noisy; a quiet italic pinyin line underneath preserves
   the reading flow while staying one glance away.
5. **Dark-first theme** — the ink design system ships light/dark; this story
   defaults to dark because the underworld is not a bright place.
6. **Monochrome enforced in CSS** — the illustrations are generated with an
   ink-wash prompt, and `filter: grayscale(100%)` guarantees a unified
   black-and-white palette regardless of model variance.
7. **One audio element, reused** — the browser plays a single `<audio>` node,
   swapped per page and per language, which keeps autoplay chaining simple and
   memory low.
8. **Autoplay is always opt-in and gesture-gated** — browsers block sound until
   the user interacts, so "Begin" is a real click, not a fake one.

## Tech Stack

| Layer | Choice |
|-------|--------|
| Frontend | HTML + CSS + vanilla JS (no framework) |
| Design system | Ink Line (墨韵) — adapted for the story mood |
| Illustrations | Cloudflare Workers AI (FLUX schnell), 1024×576 |
| Narration | Microsoft Edge TTS via `edge-tts` |
| Pinyin | `pypinyin` (tone marks) |
| Hosting | GitHub Pages |

## Project layout

```
index.html            app shell
css/app.css           project styles on top of the ink system
js/app.js             reader logic (state, audio, autoplay, i18n)
content/story.json    all story text (EN / ZH / pinyin) + asset paths
audio/en|zh/*.mp3     narration per page per language
images/*.png          ink-wash illustrations (1024×576)
ink/                  the Ink Line (墨韵) design system
scripts/              content / audio / image generators
```

## Regenerate assets

```bash
python3 scripts/generate-content.py    # rebuild story.json + pinyin + TTS text
bash   scripts/generate-audio.sh       # rebuild all MP3s via edge-tts
python3 scripts/generate-images.py     # regenerate illustrations (Cloudflare AI)
```

---

Crafted with 🤖 [Pi](https://pi.dev) and [Deepseek](https://deepseek.com)
