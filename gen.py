#!/usr/bin/env python3
"""Draw a 1024x1024 newspaper front page for Friday 20 November 2026.

Pure standard library: zlib + struct + math only. The picture is built
on a raw RGB canvas, the letters come from a hand-drawn 5x7 bitmap
font defined below, and the PNG file is encoded by hand. Running this
script always writes byte-identical output.
"""

import math
import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 240, 222)   # warm newsprint cream
INK = (18, 18, 18)        # near-black ink
RED = (178, 34, 34)       # headline red
NAVY = (24, 46, 96)       # deep navy
GOLD = (198, 148, 42)     # gold accent
PURPLE = (96, 48, 120)    # purple accent
GREY = (150, 140, 120)    # asteroid grey-brown
LIGHT = (255, 252, 244)   # bright paper white for masthead text

# ------------------------------------------------------- 5x7 bitmap font
# Each glyph is seven rows of five cells; '#' is ink, '.' is blank.
# Every letter shape below was drawn from scratch for this page.
GLYPHS = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"),
    "3": ("#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": ("..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", "..#..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#.#.", "#..##"),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "•": (".....", ".....", ".##..", ".##..", ".##..", ".....", "....."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    "—": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "’": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "×": (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
}

# Unknown characters fall back to a blank glyph so text never crashes.
BLANK = (".....", ".....", ".....", ".....", ".....", ".....", ".....")


def glyph_rows(ch):
    """Return the seven 5-cell rows for a character, upper-cased."""
    return GLYPHS.get(ch.upper(), BLANK)


def text_width(text, scale):
    """Pixel width of text drawn at the given scale."""
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def wrap_lines(text, scale, max_width):
    """Greedy word wrap; returns a list of lines fitting max_width."""
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if text_width(trial, scale) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ------------------------------------------------------------------ canvas
class Sheet:
    """A plain RGB canvas with small drawing helpers."""

    def __init__(self, width, height, base):
        self.w = width
        self.h = height
        self.buf = bytearray(bytes(base) * (width * height))

    def _offset(self, x, y):
        return (y * self.w + x) * 3

    def dot(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            off = self._offset(x, y)
            self.buf[off:off + 3] = bytes(colour)

    def rect(self, x, y, w, h, colour):
        for yy in range(max(0, y), min(self.h, y + h)):
            row = yy * self.w * 3
            for xx in range(max(0, x), min(self.w, x + w)):
                off = row + xx * 3
                self.buf[off:off + 3] = bytes(colour)

    def frame(self, x, y, w, h, colour, thick):
        self.rect(x, y, w, thick, colour)
        self.rect(x, y + h - thick, w, thick, colour)
        self.rect(x, y, thick, h, colour)
        self.rect(x + w - thick, y, thick, h, colour)

    def hline(self, x, y, length, colour, thick=1):
        self.rect(x, y, length, thick, colour)

    def vline(self, x, y, length, colour, thick=1):
        self.rect(x, y, thick, length, colour)

    def disc(self, cx, cy, r, colour):
        for dy in range(-r, r + 1):
            half = int(math.sqrt(max(0, r * r - dy * dy)))
            self.rect(cx - half, cy + dy, half * 2 + 1, 1, colour)

    def ring(self, cx, cy, r, colour, thick=2):
        for dy in range(-r - thick, r + thick + 1):
            for dx in range(-r - thick, r + thick + 1):
                dist = math.sqrt(dx * dx + dy * dy)
                if abs(dist - r) <= thick / 2.0:
                    self.dot(cx + dx, cy + dy, colour)

    def ellipse_ring(self, cx, cy, rx, ry, colour, thick=2):
        for dy in range(-ry - thick, ry + thick + 1):
            for dx in range(-rx - thick, rx + thick + 1):
                value = (dx * dx) / float(rx * rx) + (dy * dy) / float(ry * ry)
                if abs(value - 1.0) <= 0.12:
                    self.dot(cx + dx, cy + dy, colour)

    def poly(self, points, colour):
        """Scanline fill of a simple polygon given as (x, y) vertices."""
        top = min(p[1] for p in points)
        bottom = max(p[1] for p in points)
        for yy in range(top, bottom + 1):
            hits = []
            count = len(points)
            for i in range(count):
                x1, y1 = points[i]
                x2, y2 = points[(i + 1) % count]
                if (y1 <= yy < y2) or (y2 <= yy < y1):
                    cross = x1 + (yy - y1) * (x2 - x1) / float(y2 - y1)
                    hits.append(cross)
            hits.sort()
            for k in range(0, len(hits) - 1, 2):
                start = int(math.ceil(hits[k]))
                stop = int(math.floor(hits[k + 1]))
                if stop >= start:
                    self.rect(start, yy, stop - start + 1, 1, colour)

    def star(self, cx, cy, radius, colour):
        """A five-pointed star built from its ten vertices."""
        verts = []
        for i in range(10):
            angle = -math.pi / 2 + i * math.pi / 5
            rad = radius if i % 2 == 0 else radius * 0.42
            verts.append((int(cx + rad * math.cos(angle)),
                          int(cy + rad * math.sin(angle))))
        self.poly(verts, colour)

    def spark(self, cx, cy, size, colour):
        """A small four-point sparkle: a plus with diagonal ticks."""
        self.rect(cx - size, cy, size * 2 + 1, 1, colour)
        self.rect(cx, cy - size, 1, size * 2 + 1, colour)
        self.dot(cx - 1, cy - 1, colour)
        self.dot(cx + 1, cy - 1, colour)
        self.dot(cx - 1, cy + 1, colour)
        self.dot(cx + 1, cy + 1, colour)

    def draw_glyph(self, x, y, ch, scale, colour):
        rows = glyph_rows(ch)
        for row_idx, row in enumerate(rows):
            for col_idx, cell in enumerate(row):
                if cell == "#":
                    self.rect(x + col_idx * scale, y + row_idx * scale,
                              scale, scale, colour)

    def draw_text(self, x, y, text, scale, colour):
        for i, ch in enumerate(text):
            self.draw_glyph(x + i * 6 * scale, y, ch, scale, colour)
        return x + text_width(text, scale)

    def draw_centred(self, y, text, scale, colour, x0=0, x1=None):
        if x1 is None:
            x1 = self.w
        width = text_width(text, scale)
        self.draw_text(x0 + (x1 - x0 - width) // 2, y, text, scale, colour)

    def draw_para(self, x, y, text, scale, colour, max_width, leading):
        """Draw wrapped paragraph text; returns the y just below it."""
        cursor = y
        for line in wrap_lines(text, scale, max_width):
            self.draw_text(x, cursor, line, scale, colour)
            cursor += leading
        return cursor


# -------------------------------------------------------------- PNG writer
def _chunk(tag, payload):
    crc = zlib.crc32(tag + payload) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + tag + payload + struct.pack(">I", crc)


def encode_png(width, height, buf):
    raw = bytearray()
    stride = width * 3
    for row in range(height):
        raw.append(0)  # filter type 0: no filtering
        raw += buf[row * stride:(row + 1) * stride]
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", header)
            + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + _chunk(b"IEND", b""))


# ------------------------------------------------------------------- layout
MARGIN = 24
CONTENT_RIGHT = WIDTH - MARGIN


def draw_masthead(page):
    page.rect(0, 0, WIDTH, 116, INK)
    page.star(140, 58, 20, GOLD)
    page.star(WIDTH - 140, 58, 20, GOLD)
    page.draw_centred(16, "THE WORLD", 11, LIGHT)
    page.hline(0, 100, WIDTH, GOLD, 4)


def draw_date_band(page):
    page.rect(0, 116, WIDTH, 44, RED)
    page.draw_text(MARGIN + 4, 126, "FRIDAY 20 NOVEMBER 2026", 4, LIGHT)
    page.draw_text(WIDTH - MARGIN - 4 - text_width("EXTRA", 4), 126,
                   "EXTRA", 4, LIGHT)


def draw_lead(page):
    x, y, w, h = MARGIN, 178, WIDTH - 2 * MARGIN, 258
    page.frame(x, y, w, h, INK, 3)
    page.draw_text(x + 20, y + 16, "LEAD STORY", 2, RED)
    page.draw_text(x + 20, y + 42, "TRUMP PUTS IRAN", 5, INK)
    page.draw_text(x + 20, y + 86, "DECISION OFF TO 2027", 5, INK)
    page.hline(x + 20, y + 130, 660, RED, 4)
    page.draw_para(x + 20, y + 146,
                   "PRESIDENT TRUMP SAYS THERE IS 'NO RUSH' ON IRAN AND HE "
                   "WILL 'SEE WHAT HAPPENS' AFTER JANUARY 1, PUSHING ANY "
                   "DECISION INTO 2027.",
                   2, INK, 660, 19)
    # Gold 2027 chip in the lower-left corner of the panel.
    page.rect(x + 20, y + 210, 118, 32, GOLD)
    page.draw_text(x + 20 + (118 - text_width("2027", 3)) // 2, y + 217,
                   "2027", 3, NAVY)
    # Globe pictogram: ring, meridian ellipse and latitude chords.
    gx, gy = 895, 312
    page.ring(gx, gy, 62, NAVY, 3)
    page.ellipse_ring(gx, gy, 26, 62, NAVY, 2)
    page.hline(gx - 58, gy - 22, 116, NAVY, 2)
    page.hline(gx - 58, gy + 22, 116, NAVY, 2)
    page.star(952, 216, 14, GOLD)


# Pictogram zone: a square corner box inside each story panel.
ZONE_SIZE = 76
ZONE_PAD = 16


def draw_story_panel(page, x, y, w, h, kicker, kicker_colour,
                     headline, body, art):
    page.frame(x, y, w, h, INK, 2)
    pad = 16
    page.draw_text(x + pad, y + 14, kicker, 2, kicker_colour)
    # Pictogram lives in the top-right corner; headlines stay clear of it.
    zone_x = x + w - ZONE_PAD - ZONE_SIZE
    zone_y = y + 14
    art(page, zone_x, zone_y)
    page.draw_para(x + pad, y + 36, headline, 3, INK, w - pad - 108, 26)
    page.draw_para(x + pad, y + 100, body, 2, INK, w - 2 * pad, 19)


def art_voyager(page, zx, zy):
    cx, cy = zx + 38, zy + 38
    page.spark(zx + 8, zy + 6, 4, GOLD)
    page.spark(zx + 66, zy + 12, 3, GOLD)
    page.spark(zx + 60, zy + 66, 4, GOLD)
    page.disc(cx, cy + 6, 16, NAVY)
    page.ellipse_ring(cx, cy + 6, 30, 9, GOLD, 2)
    page.disc(cx + 26, cy - 16, 4, RED)


def art_cyclone(page, zx, zy):
    cx, cy = zx + 38, zy + 38
    page.ring(cx, cy, 30, NAVY, 3)
    page.ring(cx, cy, 20, RED, 3)
    page.ring(cx, cy, 10, NAVY, 3)
    page.disc(cx, cy, 5, RED)


def art_kyiv(page, zx, zy):
    # Austria: red-white-red horizontal stripes.
    page.rect(zx, zy + 8, 76, 20, RED)
    page.rect(zx, zy + 15, 76, 6, LIGHT)
    # Netherlands: red-white-blue horizontal stripes.
    page.rect(zx, zy + 38, 76, 20, RED)
    page.rect(zx, zy + 45, 76, 6, LIGHT)
    page.rect(zx, zy + 51, 76, 7, NAVY)


def art_gta(page, zx, zy):
    cx, cy = zx + 38, zy + 38
    page.disc(cx, cy, 28, GOLD)
    page.ring(cx, cy, 28, NAVY, 2)
    page.draw_text(cx - text_width("$", 4) // 2, cy - 14, "$", 4, NAVY)


def draw_wide_panel(page, x, y, w, h, headline, body):
    page.frame(x, y, w, h, INK, 2)
    page.draw_text(x + 16, y + 10, headline, 3, INK)
    page.draw_para(x + 16, y + 38, body, 2, INK, w - 170, 19)
    # Asteroid rock with a small probe drifting beside it.
    rock = [(928, 892), (946, 884), (966, 890), (972, 908),
            (960, 924), (940, 926), (926, 912)]
    page.poly(rock, GREY)
    page.disc(948, 904, 5, INK)
    page.disc(884, 902, 8, GOLD)
    page.hline(892, 901, 34, GOLD, 2)


def draw_bottom_strip(page):
    page.rect(0, 966, WIDTH, 40, NAVY)
    head = "EUROPE READY FOR UKRAINE TALKS"
    page.draw_text(MARGIN, 974, head, 3, LIGHT)
    after = MARGIN + text_width(head, 3) + 24
    page.draw_text(after, 978, "LEADERS READY FOR TALKS", 2, GOLD)


def draw_footer(page):
    page.draw_centred(1010,
                      "THE WORLD • FRIDAY 20 NOVEMBER 2026 • ALL THE NEWS "
                      "THAT FITS ON ONE PAGE",
                      2, INK)


def build_page():
    page = Sheet(WIDTH, HEIGHT, PAPER)
    draw_masthead(page)
    draw_date_band(page)
    page.hline(0, 160, WIDTH, GOLD, 4)
    draw_lead(page)
    stories = [
        (MARGIN, 452, "SPACE", NAVY,
         "VOYAGER 1, A LIGHT-DAY FROM HOME",
         "NASA CONFIRMS VOYAGER 1 IS ONE LIGHT-DAY FROM EARTH, ABOUT 16 "
         "BILLION MILES. THE FIRST HUMAN-MADE OBJECT TO REACH THE MARK.",
         art_voyager),
        (524, 452, "WEATHER", RED,
         "CYCLONE AKVAN MAKES LANDFALL",
         "SEVERE CYCLONE AKVAN HITS INDIA'S EAST COAST. 300,000 EVACUATED "
         "IN ODISHA AND ANDHRA PRADESH AS SCHOOLS SHUT AND RED ALERTS SOUND.",
         art_cyclone),
        (MARGIN, 664, "EUROPE", NAVY,
         "KYIV EMBASSY STRIKES",
         "RUSSIAN STRIKES DAMAGE THE AUSTRIAN AND DUTCH EMBASSIES IN KYIV, "
         "DIPLOMATS CONFIRM.",
         art_kyiv),
        (524, 664, "BUSINESS", PURPLE,
         "GTA VI PASSES $1.8 BILLION",
         "GRAND THEFT AUTO VI SALES ALREADY PASS THE ODYSSEY'S $1.80 "
         "BILLION GLOBAL RUN.",
         art_gta),
    ]
    for px, py, kicker, kcolour, head, body, art in stories:
        draw_story_panel(page, px, py, 476, 196, kicker, kcolour,
                         head, body, art)
    draw_wide_panel(page, MARGIN, 876, WIDTH - 2 * MARGIN, 76,
                    "HAYABUSA2 ABANDONS ASTEROID LANDING",
                    "ENGINE TROUBLE FORCES JAPAN'S HAYABUSA2 PROBE TO "
                    "CHANGE PLANS. NO ASTEROID LANDING NOW.")
    draw_bottom_strip(page)
    draw_footer(page)
    return page


def main():
    page = build_page()
    data = encode_png(WIDTH, HEIGHT, page.buf)
    here = os.path.dirname(os.path.abspath(__file__))
    target = os.path.join(here, "entry.png")
    with open(target, "wb") as handle:
        handle.write(data)
    os.chmod(target, 0o644)
    print("wrote {} ({} bytes)".format(target, len(data)))


if __name__ == "__main__":
    main()
