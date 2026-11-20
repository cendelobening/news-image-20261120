[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/cendelobening/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/cendelobening/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

# The World — Friday 20 November 2026, on one page

A newspaper front page that sums up Friday 20 November 2026's world
news in a single 1024×1024 image. The picture is drawn entirely by a
pure-stdlib Python generator: `gen.py` builds the page on a raw RGB
canvas with a hand-drawn 5×7 bitmap font and a hand-rolled PNG
encoder (zlib + struct only — no Pillow, no image libraries), and
`main.py` validates the image and copies it to the output directory.

## The six stories

1. **Lead — Trump puts the Iran decision off to 2027.** President
   Trump says there is "no rush" on Iran and he will "see what
   happens" after January 1, pushing any decision into 2027.
2. **Voyager 1, a light-day from home.** NASA confirms Voyager 1 is
   now one light-day from Earth — about 16 billion miles — the first
   human-made object ever to reach the mark.
3. **Cyclone Akvan makes landfall.** Severe Cyclone Akvan hits
   India's east coast: 300,000 evacuated in Odisha and Andhra
   Pradesh, schools shut, red alerts in force.
4. **Kyiv embassy strikes.** Russian strikes damage the Austrian and
   Dutch embassies in Kyiv.
5. **GTA VI passes $1.8 billion.** Grand Theft Auto VI sales already
   pass The Odyssey's $1.80 billion global run.
6. **Hayabusa2 abandons asteroid landing.** Engine trouble forces
   Japan's Hayabusa2 probe to change plans — no asteroid landing now.

Bottom strip: **Europe ready for Ukraine talks** — European leaders
say they are ready for talks with Russia on ending the war.

## Design

A black masthead with the cream "THE WORLD" wordmark and gold stars,
a red "EXTRA" date band, a lead panel with a globe pictogram and a
gold 2027 chip, then a four-panel grid — a ringed planet for Voyager,
concentric cyclone rings, Austrian and Dutch flag stripes for Kyiv,
and a gold dollar coin for GTA VI — plus a wide Hayabusa2 panel with
an asteroid and probe, a navy Europe/Ukraine strip, and a paper
footer line.

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Regenerate `entry.png` deterministically with:

```sh
python3 gen.py
```
