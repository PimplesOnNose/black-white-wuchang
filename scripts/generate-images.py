#!/usr/bin/env python3
"""Generate the 11 ink-wash illustrations for 黑白无常 using cf-image.py."""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CF = pathlib.Path(__file__).resolve().parent / "cf-image.py"
OUT = ROOT / "images"
OUT.mkdir(exist_ok=True)

STYLE = (
    "Traditional Chinese ink wash painting (shuǐmò huà), monochrome black ink on "
    "aged rice paper, calligraphic brushwork, expressive negative space, no color, "
    "sumi-e aesthetic, vertical handscroll composition, atmospheric mist, "
    "muted grays, historical illustration. "
)
NEG = "color, neon, photograph, 3d render, cartoon, modern clothing, watermark, text, letters, caption"

# slug -> detailed subject prompt
PROMPTS = {
    "landing": (
        "Two ghostly court officials standing side by side at twilight beneath "
        "willow trees: one tall, thin, pale figure in flowing white robes, one "
        "short, stout, dark figure in black robes, ink mist swirling around them"
    ),
    "underworld": (
        "The Chinese underworld court: a stern judge-king seated on a raised "
        "throne in a vast empty hall, scribes and guards with scrolls and chains, "
        "columns of incense smoke, solemn and immense"
    ),
    "brothers": (
        "Two men walking together along a riverbank at dusk, one tall and slim "
        "with a gentle face, one short and stocky with a bold stride, sweeping "
        "brushstrokes suggesting lifelong friendship and shared purpose"
    ),
    "bridge": (
        "A traditional stone arch bridge over a wide river, dark storm clouds "
        "gathering on the horizon, a tall figure walking away toward distant "
        "houses, a short figure waiting patiently beneath the bridge, first "
        "drops of rain beginning to fall"
    ),
    "river": (
        "A furious river in flood, water crashing against a stone bridge, rain "
        "slashing down in long ink strokes, a small resolute figure clinging to "
        "a bridge pillar with both arms, determined not to abandon his post"
    ),
    "hanging": (
        "A lone tall thin figure collapsing in grief beneath a willow tree at "
        "the edge of a swollen river, a rope hanging from a branch above, vast "
        "empty space, sombre silence, vertical scroll composition"
    ),
    "jade-emperor": (
        "The Jade Emperor in flowing celestial robes seated among clouds, "
        "bestowing two imperial scrolls upon two kneeling figures who have just "
        "crossed into the afterlife, light breaking through the mist"
    ),
    "yin-yang": (
        "An abstract taiji symbol rendered in ink wash, a white-robed figure "
        "and a black-robed figure forming the two halves, hat-text marks hinted "
        "as abstract brushstrokes, balance and harmony"
    ),
    "procession": (
        "A nighttime temple festival parade: two enormous puppet-figures — one "
        "tall and white, one short and black — carried high on shoulders through "
        "a narrow street, swirling incense smoke, lanterns, towering over the "
        "crowd below"
    ),
    "names": (
        "Two large calligraphic name plaques hanging in the void, one tall "
        "plaque and one square plaque, ink brush calligraphy on aged rice paper, "
        "vertical composition, quiet reverence"
    ),
    "epilogue": (
        "An empty stone bridge at dawn, mist rising from the river, two faint "
        "silhouettes receding into the distance, vast blank paper, quiet "
        "stillness, the feeling of a story ending"
    ),
}


def main():
    story = json.loads((ROOT / "content" / "story.json").read_text(encoding="utf-8"))
    only = sys.argv[1] if len(sys.argv) > 1 else None

    for pg in story["pages"]:
        slug = pg["slug"]
        if only and slug != only:
            continue
        subject = PROMPTS[slug]
        out = OUT / f"{pg['id']}-{slug}.png"
        if out.exists() and only is None:
            print(f"⏭  {out.name} exists — skip (use arg to regenerate one)")
            continue
        print(f"→ Generating {out.name} ...")
        result = subprocess.run(
            [
                sys.executable, str(CF),
                STYLE + subject,
                "--output", str(out),
                "--width", "1024",
                "--height", "576",
                "--steps", "4",
                "--negative", NEG,
            ],
            cwd=str(ROOT),
        )
        if result.returncode != 0:
            print(f"❌ Failed: {out.name}")
            sys.exit(1)

    print("✅ All requested images generated.")


if __name__ == "__main__":
    main()
