# 黑白无常 · The Impermanence

> 一个双语、配有旁白的民间故事网页应用，讲述两位结拜兄弟成为「黑白无常」——
> 生死之间引路者的传说。

**在线演示** → [https://PimplesOnNose.github.io/black-white-wuchang/](https://PimplesOnNose.github.io/black-white-wuchang/)

[English](README.md) · 中文版

---

## 故事

幽冥地府之前，有一对兄弟曾立下誓言：无论风、雨、洪水，都要等彼此归来。
一人信守承诺，直到被河水吞没；另一人不愿独活，随之而去。
玉皇大帝为他们的信义所动，册封他们为黑白无常——游走于生死之间的引路人，
赏善罚恶，缉拿罪魂。

本应用将这段传说讲述为 **11 页配图、配旁白的篇章**——序页、九章与终章，
献给正站在成年门槛上的年轻读者。

## 功能

- **双语阅读** — 一键切换 `EN` / `中`；中文视图为简体中文，
  并配有**独立注音（拼音）区块**（非 ruby，含声调）。
- **旁白朗读** — 22 段预生成 MP3（11 页 × 2 种语言），不使用实时语音合成。
  - 英文：`en-US-MichelleNeural`（女声，常速）
  - 中文：`zh-CN-YunjianNeural`（男声，放慢 5%）
- **自动播放** — 播完当前页旁白后自动翻到下一页。
- **水墨插图** — 11 幅黑白水墨画（1024×576），由 FLUX 生成，CSS 统一去色。
- **明暗主题** — 基于墨韵（Ink Line）设计系统；默认暗色，贴合鬼故事的氛围。
- **键盘快捷键** — `Space` 播放/暂停，`←` / `→` 翻页，`L` 切换语言，`T` 切换主题。
- **无障碍** — 语义化 HTML、`lang` 属性、`aria` 标签、键盘可达、支持
  `prefers-reduced-motion`。

## 章节

| # | 章节 | 内容 |
|---|------|------|
| — | 序 · Prologue | 封面 |
| 壹 | 幽冥 · The Underworld | 引魂之所 |
| 贰 | 兄弟 · The Brothers | 谢必安与范无救立誓 |
| 叁 | 桥 · The Bridge | 南台桥之约 |
| 肆 | 河 · The River | 风雨、洪水，与一个守候的人 |
| 伍 | 殉 · The Hanging | 不愿独活的兄弟 |
| 陆 | 玉帝 · The Jade Emperor | 双魂、一诏 |
| 柒 | 阴阳 · Yin and Yang | 黑白无常 |
| 捌 | 出巡 · The Procession | 迎神巡游 |
| 玖 | 名 · The Names | 一见生财 · 天下太平 |
| — | 终 · Epilogue | 无常所问 |

## 本地运行

```bash
git clone https://github.com/PimplesOnNose/black-white-wuchang.git
cd black-white-wuchang
python3 -m http.server 8080
# 打开 http://localhost:8080
```

无需构建、无依赖、无后端。直接以 `file://` 打开 `index.html` 也可运行。

## 设计决策

1. **单一数据源** — 所有文字（英文、中文、拼音、资源路径）都存放在
   `content/story.json` 中；阅读器、音频生成、图片管线全部读取同一份数据，
   杜绝文字与音频脱节。
2. **静态无构建架构** — 一个 `index.html` 加上墨韵设计系统与一个
   `app.js`，加载快，托管到 GitHub Pages 零成本。
3. **预生成旁白而非实时 TTS** — 用 Edge TTS 一次性生成音频，
   每位访客听到的都是同一段从容的朗读；中文男声放慢 5%，
   为故事增添沉稳肃穆的节奏。
4. **拼音独立成块，而非 ruby** — 中文学习者常觉得逐字注音视觉嘈杂；
   正文下方一行安静的斜体拼音，既保持阅读流畅，又触手可得。
5. **默认暗色主题** — 墨韵设计系统自带明暗切换；本故事默认暗色，
   因为幽冥本不是明亮之地。
6. **CSS 强制单色** — 插图按水墨画提示词生成，再以
   `filter: grayscale(100%)` 统一黑白，避免模型随机偏差。
7. **复用一个音频元素** — 浏览器仅持有一个 `<audio>` 节点，
   按页与语言切换 `src`，让自动播放的衔接简单、内存占用低。
8. **自动播放始终可选、且需用户手势触发** — 浏览器禁止未交互就发声，
   所以「开始」是一个真实的点击，而非虚假的自动播放。

## 技术栈

| 层 | 选型 |
|----|------|
| 前端 | HTML + CSS + 原生 JS（无框架） |
| 设计系统 | 墨韵 Ink Line —— 依故事氛围适配 |
| 插图 | Cloudflare Workers AI（FLUX schnell），1024×576 |
| 旁白 | Microsoft Edge TTS（`edge-tts`） |
| 拼音 | `pypinyin`（含声调） |
| 托管 | GitHub Pages |

## 目录结构

```
index.html            应用外壳
css/app.css           项目样式（叠加于墨韵系统之上）
js/app.js             阅读器逻辑（状态、音频、自动播放、i18n）
content/story.json    全部故事文本（EN / ZH / 拼音）与资源路径
audio/en|zh/*.mp3     每页每语言的旁白
images/*.png          水墨插图（1024×576）
ink/                  墨韵（Ink Line）设计系统
scripts/              内容 / 音频 / 图片生成脚本
```

## 重新生成资源

```bash
python3 scripts/generate-content.py    # 重建 story.json + 拼音 + TTS 文本
bash   scripts/generate-audio.sh       # 用 edge-tts 重建全部 MP3
python3 scripts/generate-images.py     # 重新生成插图（Cloudflare AI）
```

---

由 🤖 [Pi](https://pi.dev) 与 [Deepseek](https://deepseek.com) 精心打造
