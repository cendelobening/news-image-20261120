[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/cendelobening/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/cendelobening/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

# The World — 20 November 2026, in one image

A newspaper front page that sums up Friday 20 November 2026's world
news in a single 1024×1024 image. `entry.png` is drawn entirely by a
pure-stdlib Python generator (`gen.py`: custom 5×7 bitmap font,
hand-rolled PNG encoder — no Pillow, no image libraries), and `main.py`
validates the image and copies it to the output directory.

## The six stories

1. **Lead — Trump puts Iran decision off to 2027.** Trump says there
   is "no rush" on an Iran decision — "see what happens" after
   January 1, pushing any call into 2027.
2. **Voyager 1, a light-day from home.** NASA confirms the probe is
   one light-day from Earth — about 16 billion miles, the first
   human-made object to reach the mark.
3. **Cyclone Akvan makes landfall.** Severe Cyclone Akvan hits
   India's east coast: 300,000 evacuated, schools shut, red alerts
   in Odisha and Andhra Pradesh.
4. **Kyiv embassy strikes.** Russian strikes damage the Austrian and
   Dutch embassies in Kyiv.
5. **GTA VI passes $1.8 billion.** Grand Theft Auto VI sales already
   pass The Odyssey's $1.80 billion global run.
6. **Hayabusa2 abandons asteroid landing.** Engine trouble forces
   Japan's Hayabusa2 probe to change plans — no more asteroid
   landing.

Bottom strip: **Europe ready for Ukraine talks** — European leaders
say they are ready for talks with Russia on ending the war.

## Design

Black masthead with a cream "THE WORLD" wordmark and gold side notes
over a red "EXTRA" date band, a navy Trump/Iran lead panel with
US and Iran flags and a gold 2027 chip, then a dense four-story grid
— dotted-path Voyager art, concentric cyclone rings, a cracked
embassy building with Austrian and Dutch flags, and a neon GTA VI
starburst — plus a wide Hayabusa2 panel and a Europe/Ukraine bottom
strip with EU and Ukrainian flags.

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`gen.py` regenerates `entry.png` deterministically:

```sh
python3 gen.py
```
