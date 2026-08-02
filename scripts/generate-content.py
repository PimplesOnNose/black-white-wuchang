#!/usr/bin/env python3
"""Generate story.json (with pinyin) and TTS narration text files for 黑白无常.

This script is the single source of truth for story content.
Run:  python3 scripts/generate-content.py
"""
import json
import pathlib
import re
from pypinyin import pinyin, Style

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"

# ---------------------------------------------------------------- content ---

META = {
    "title_en": "The Impermanence",
    "title_zh": "黑白无常",
    "title_pinyin": "Hēi Bái Wú Cháng",
    "subtitle_en": "A Chinese folktale of two brothers who became the guardians between life and death",
    "subtitle_zh": "两位结义兄弟化为阴阳使者的民间传说",
    "subtitle_pinyin": "Liǎng wèi jié yì xiōng dì huà wéi yīn yáng shǐ zhě de mín jiān chuán shuō",
    "duration_minutes": 10,
}

PAGES = [
    # ---------------- 00 · Landing ----------------
    dict(
        id="00", slug="landing",
        section_numeral="", label_en="", label_zh="",
        title_en="The Impermanence", title_zh="黑白无常",
        body_en=(
            "All things flow. All things end. This is the tale the Chinese tell "
            "about two brothers who kept their word beyond death — and became the "
            "guardians between the world of the living and the world of the dead. "
            "Press begin, and listen."
        ),
        body_zh=(
            "万事万物，皆在流动；万事万物，皆有尽时。这是一个中国人讲了千百年的故事——"
            "一对兄弟信守承诺，直至死后，化身阴阳两界之间的守护者。按下开始，请听。"
        ),
    ),
    # ---------------- 01 · The Underworld ----------------
    dict(
        id="01", slug="underworld", numeral="壹",
        label_en="Chapter One", label_zh="第一章",
        title_en="Before There Were Ghosts", title_zh="在鬼魂出现之前",
        body_en=(
            "In the old Chinese imagination, death was not an ending but a transfer. "
            "The dead walked a long road through the underworld — past the courts of "
            "Yanluo the King, the City God, and the judges who weighed every life "
            "like merchants weighing silver. Every soul needed an escort. And every "
            "escort had a story of their own."
        ),
        body_zh=(
            "在古人的想象里，死亡不是结束，而是转场。逝者要走过一条长长的路，"
            "穿过阎罗王的殿堂、城隍的衙门，和判官的案前——判官掂量每一生的分量，"
            "如同商人称量白银。每个魂魄都需要引路的人。而每一个引路者，都有属于他们自己的故事。"
        ),
    ),
    # ---------------- 02 · Two Sworn Brothers ----------------
    dict(
        id="02", slug="brothers", numeral="贰",
        label_en="Chapter Two", label_zh="第二章",
        title_en="Two Sworn Brothers", title_zh="结义兄弟",
        body_en=(
            "Once, long ago, there lived two sworn brothers. The first, Xie Bian, was "
            "tall and gentle, patient as still water. The second, Fan Wujiu, was short "
            "and hot-tempered, loyal as iron. They had grown up together, shared every "
            "meal and every danger, and sworn never to let each other down."
        ),
        body_zh=(
            "很久很久以前，有一对结义兄弟。哥哥谢必安，身材高大，性情温和，像一潭静水；"
            "弟弟范无救，个子矮小，脾气火爆，却忠心似铁。两人从小一起长大，同吃同住，"
            "同历艰险，立誓永不相负。"
        ),
    ),
    # ---------------- 03 · The Bridge at Nantai ----------------
    dict(
        id="03", slug="bridge", numeral="叁",
        label_en="Chapter Three", label_zh="第三章",
        title_en="The Bridge at Nantai", title_zh="南台桥之约",
        body_en=(
            "One summer day, they came to the Nantai Bridge. Dark clouds gathered; "
            "rain was coming. \u201cWait here, brother,\u201d said Xie Bian. \u201cI will fetch an "
            "umbrella.\u201d Fan Wujiu nodded and sat beneath the bridge to wait, as they "
            "had agreed. It was a small promise. But some promises are small only "
            "until they are tested."
        ),
        body_zh=(
            "那年夏天，两人走到南台桥边。乌云压顶，眼看就要下雨。谢必安说：\u201c弟弟，"
            "你在此等候，我回家取伞。\u201d范无救点点头，坐在桥下等着，如同他们约定好的那样。"
            "这只是一个很小的约定。可有些约定，在经受考验之前，永远不知道它有多大。"
        ),
    ),
    # ---------------- 04 · The Raging River ----------------
    dict(
        id="04", slug="river", numeral="肆",
        label_en="Chapter Four", label_zh="第四章",
        title_en="The Raging River", title_zh="暴雨滔天",
        body_en=(
            "The rain came down like the sky had split open. The river swelled, "
            "roaring over its banks. Water rose around Fan Wujiu — to his knees, his "
            "waist, his chest. He could have climbed to safety. He could have broken "
            "his word. Instead he held to the bridge pillar, and held to his promise, "
            "until the river took him."
        ),
        body_zh=(
            "大雨倾盆，仿佛天被撕开了口子。河水暴涨，咆哮着漫过堤岸。水淹过范无救的膝盖、"
            "腰身、胸口。他本可以爬上岸去，本可以失约一次。但他抱着桥柱，抱着那句承诺，"
            "直到河水将他吞没。"
        ),
    ),
    # ---------------- 05 · The Tongue of Grief ----------------
    dict(
        id="05", slug="hanging", numeral="伍",
        label_en="Chapter Five", label_zh="第五章",
        title_en="The Tongue of Grief", title_zh="悲伤的长舌",
        body_en=(
            "When Xie Bian returned with the umbrella, he found only the flood. His "
            "brother was gone. The tall man who had never raised his voice now wept "
            "like a child. Unable to bear a world without his brother, he hanged "
            "himself from the bridge. That is why, to this day, the White Impermanence "
            "is shown with a long tongue — the mark of a man who died of sorrow."
        ),
        body_zh=(
            "谢必安拿着伞赶回来时，只见滔滔洪水，弟弟已不见踪影。这个从不高声说话的巨人，"
            "哭得像个孩子。他无法忍受没有弟弟的世界，于是在桥头自缢身亡。所以直到今天，"
            "白无常的形象总是吐着长长的舌头——那是悲伤至死的印记。"
        ),
    ),
    # ---------------- 06 · Before the Jade Emperor ----------------
    dict(
        id="06", slug="jade-emperor", numeral="陆",
        label_en="Chapter Six", label_zh="第六章",
        title_en="Before the Jade Emperor", title_zh="玉帝敕封",
        body_en=(
            "The two brothers met again in the world of spirits. The Jade Emperor, "
            "who rules the heavens, heard their story. Moved by their faith and "
            "brotherhood, he did not send them to be reborn. Instead he appointed them "
            "officers of the underworld — Xie Bian in white, Fan Wujiu in black — to "
            "guide the souls of the dead and keep order between the worlds."
        ),
        body_zh=(
            "两个兄弟在幽冥之中重逢。天庭的玉皇大帝听说了他们的故事，为他们的信义与情义所感动。"
            "他没有让他们转世投胎，而是册封他们为地府的官差——谢必安白衣，范无救黑衣——"
            "负责接引亡魂，维持阴阳两界的秩序。"
        ),
    ),
    # ---------------- 07 · Black and White, Yin and Yang ----------------
    dict(
        id="07", slug="yin-yang", numeral="柒",
        label_en="Chapter Seven", label_zh="第七章",
        title_en="Black and White, Yin and Yang", title_zh="黑白阴阳",
        body_en=(
            "Why black and white? In Chinese thought, the world turns on two forces: "
            "yin and yang — dark and light, night and day, death and life. The two "
            "brothers became the living symbol of that balance. White Xie Bian's hat "
            "reads \u201cMeet Me and Find Fortune.\u201d Black Fan Wujiu's hat reads \u201cPeace "
            "Under Heaven.\u201d One offers mercy; the other enforces justice."
        ),
        body_zh=(
            "为什么是黑与白？在中国人的观念里，万物都由阴阳两股力量运转——暗与明，夜与昼，"
            "死与生。两位兄弟成了这种平衡的化身。白无常谢必安的高帽上写着\u201c一见生财\u201d，"
            "黑无常范无救的帽上写着\u201c天下太平\u201d。一个带来宽仁，一个维护公正。"
        ),
    ),
    # ---------------- 08 · What They Still Do ----------------
    dict(
        id="08", slug="procession", numeral="捌",
        label_en="Chapter Eight", label_zh="第八章",
        title_en="What They Still Do", title_zh="至今仍在",
        body_en=(
            "Even today, their images stand on either side of the City God in temples "
            "across China and Taiwan — one tall and white, one short and black. During "
            "temple festivals, huge puppet figures of the Seventh and Eighth Lords "
            "lead processions through the streets, towering over the crowd. People "
            "say that to meet them is a warning: keep your word, do no wrong."
        ),
        body_zh=(
            "直到今天，中国和台湾的城隍庙里，他们的神像仍分立两旁——一位高而白，一位矮而黑。"
            "庙会游行时，巨大的七爷八爷神将走在队伍最前面，高过人群，穿街而过。"
            "人们说，见到他们是一种提醒：守信重诺，莫作恶事。"
        ),
    ),
    # ---------------- 09 · A Note on Names ----------------
    dict(
        id="09", slug="names", numeral="玖",
        label_en="Chapter Nine", label_zh="第九章",
        title_en="A Note on Names", title_zh="名字之道",
        body_en=(
            "Their names carry the whole lesson. Xie Bian — \u201crepent, and you will find "
            "peace.\u201d Fan Wujiu — \u201cthe wicked are beyond rescue.\u201d Some say the names "
            "are a promise: those who repent can still be saved, while those who refuse "
            "to change will find no one to save them. The brothers who kept their word "
            "became the guardians of the promise that goodness is rewarded."
        ),
        body_zh=(
            "他们的名字里藏着全部的教诲。谢必安——\u201c谢罪悔过，必得平安\u201d；范无救——"
            "\u201c作恶之人，必定无救\u201d。有人说，这两个名字是一种许诺：肯回头的人仍有救，"
            "不肯改过的人终将无人能救。那对守住约定的兄弟，成了\u201c善有善报\u201d这句话的守护者。"
        ),
    ),
    # ---------------- 10 · Epilogue ----------------
    dict(
        id="10", slug="epilogue",
        section_numeral="", label_en="", label_zh="",
        title_en="Impermanence", title_zh="无常",
        body_en=(
            "The tale of the Black and White Impermanence is not really about ghosts. "
            "It is about impermanence — the Chinese word wuchang — the truth that all "
            "things change, and all things end. The brothers remind us that in a world "
            "of constant change, some things can still hold: a promise, a friendship, "
            "a choice to do right. Keep your word. And when the river rises, hold to "
            "the pillar."
        ),
        body_zh=(
            "黑白无常的故事，说的其实不是鬼。它说的是\u201c无常\u201d——万物皆变，终有尽时。"
            "两位兄弟提醒我们：在这个不断变化的世界里，有些东西仍然可以坚守——一句承诺、"
            "一份情义、一次向善的选择。守好你的承诺。当河水上涨时，抱紧那根桥柱。"
        ),
    ),
]

# ---------------------------------------------------------------- helpers ---

def to_pinyin(text: str, title: bool = False) -> str:
    """Return space-separated pinyin with tone marks. Titles are capitalised."""
    parts = pinyin(text, style=Style.TONE, heteronym=False, errors="default")
    flat = [p[0] for p in parts]
    if title:
        return " ".join(s.capitalize() for s in flat)
    return " ".join(flat)


def build_story() -> dict:
    pages = []
    for pg in PAGES:
        pages.append(
            {
                "id": pg["id"],
                "slug": pg["slug"],
                "image": f"images/{pg['id']}-{pg['slug']}.png",
                "audio": {
                    "en": f"audio/en/{pg['id']}.mp3",
                    "zh": f"audio/zh/{pg['id']}.mp3",
                },
                "section_numeral": pg.get("numeral", ""),
                "section_label_en": pg["label_en"],
                "section_label_zh": pg["label_zh"],
                "title_en": pg["title_en"],
                "title_zh": pg["title_zh"],
                "title_pinyin": to_pinyin(pg["title_zh"], title=True),
                "body_en": pg["body_en"],
                "body_zh": pg["body_zh"],
                "body_pinyin": to_pinyin(pg["body_zh"]),
                "alt_en": pg.get("alt_en", pg["title_en"]),
                "alt_zh": pg.get("alt_zh", pg["title_zh"]),
            }
        )
    return {"meta": META, "pages": pages}


def write_narration(story: dict) -> None:
    """Write per-page TTS text files (same as body for this project)."""
    (CONTENT_DIR / "en").mkdir(parents=True, exist_ok=True)
    (CONTENT_DIR / "zh").mkdir(parents=True, exist_ok=True)
    for pg in story["pages"]:
        (CONTENT_DIR / "en" / f"{pg['id']}.txt").write_text(
            pg["body_en"].replace("\u201c", '"').replace("\u201d", '"'), encoding="utf-8"
        )
        (CONTENT_DIR / "zh" / f"{pg['id']}.txt").write_text(
            pg["body_zh"], encoding="utf-8"
        )


def main() -> None:
    story = build_story()
    out = ROOT / "content" / "story.json"
    out.write_text(json.dumps(story, ensure_ascii=False, indent=2), encoding="utf-8")
    write_narration(story)
    print(f"✅ Wrote {out}")
    print(f"✅ Wrote narration texts in content/en/, content/zh/ ({len(story['pages'])} pages)")
    # sanity check
    for pg in story["pages"]:
        assert pg["title_pinyin"], pg["id"]
        assert pg["body_pinyin"], pg["id"]
    print("✅ Pinyin OK for all pages")


if __name__ == "__main__":
    main()
