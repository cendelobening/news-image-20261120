#!/usr/bin/env python3
"""Generator for the 20 November 2026 news front page.

Draws a 1024x1024 PNG newspaper front page with a custom 5x7 bitmap
font and a hand-rolled PNG encoder. Pure standard library only
(zlib, struct, math). Deterministic: every run writes identical bytes.

Design: black masthead with a cream "THE WORLD" wordmark, red "EXTRA"
date band reading "FRIDAY 20 NOVEMBER 2026", a navy Trump/Iran lead
panel, a dense five-story grid (Voyager 1, Cyclone Akvan, Kyiv embassy
strikes, GTA VI at $1.8B, Hayabusa2), and a Europe/Ukraine bottom
strip. Six stories, all first reported on Friday 20 November 2026.
"""
import math
import struct
import zlib

# ---------------------------------------------------------------- font
# 5x7 bitmap font. Each glyph is 7 rows of 5 bits, "1" = ink.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
}

FONT.update({
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10001", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01000", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "00010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "00000", "11110", "10001", "11110", "10000", "10000"),
    "q": ("00000", "00000", "01111", "10001", "01111", "00001", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("01000", "01000", "11100", "01000", "01000", "01000", "00110"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "—": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "•": ("00000", "00000", "01100", "01100", "01100", "00000", "00000"),
    "’": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "|": ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
})

# ---------------------------------------------------------------- canvas
W = 1024
H = 1024
PAPER = (247, 242, 231)
INK = (20, 20, 20)
RED = (176, 42, 30)
BLUE = (31, 78, 121)
DARKBLUE = (18, 38, 66)
GOLD = (198, 142, 26)
GREY = (110, 108, 100)
LIGHT = (255, 255, 255)
NAVY = (13, 27, 54)
PURPLE = (34, 14, 58)
PINK = (255, 71, 150)
TEAL = (32, 178, 170)
CREAM = (250, 246, 235)
STORM = (16, 60, 96)
SAND = (232, 226, 210)
BLACK = (8, 8, 10)
LEAD_BODY = (214, 222, 236)
HALFTONE_DOT = (40, 58, 96)
GREEN_BTN = (60, 200, 110)
LEAD_FIELD = (10, 20, 44)
SPACE = (8, 12, 28)
BUILDING = (96, 96, 104)
ASTEROID = (150, 150, 150)


class Canvas:
    """A flat RGB pixel buffer with simple drawing primitives."""

    def __init__(self, width, height, color):
        self.w = width
        self.h = height
        self.px = bytearray(color * (width * height))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def frame(self, x, y, w, h, color, t=2):
        self.rect(x, y, w, t, color)
        self.rect(x, y + h - t, w, t, color)
        self.rect(x, y, t, h, color)
        self.rect(x + w - t, y, t, h, color)

    def hline(self, x, y, w, color, t=1):
        self.rect(x, y, w, t, color)

    def vline(self, x, y, h, color, t=1):
        self.rect(x, y, t, h, color)

    def line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d2 <= r * r:
                        self.set(xx, yy, color)
                else:
                    if abs(d2 - r * r) <= r:
                        self.set(xx, yy, color)

    def ring(self, cx, cy, r, color, t=2):
        for k in range(t):
            self.circle(cx, cy, r - k, color, fill=False)

    def star(self, cx, cy, r, color):
        pts = []
        for i in range(10):
            ang = -math.pi / 2 + i * math.pi / 5
            rr = r if i % 2 == 0 else r * 0.42
            pts.append((cx + int(rr * math.cos(ang)),
                        cy + int(rr * math.sin(ang))))
        for i in range(10):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % 10]
            self.line(x0, y0, x1, y1, color)
        ys = [p[1] for p in pts]
        for yy in range(min(ys), max(ys) + 1):
            xs = []
            for i in range(10):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % 10]
                if (y0 <= yy < y1) or (y1 <= yy < y0):
                    xs.append(x0 + (yy - y0) * (x1 - x0) // (y1 - y0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                for xx in range(xs[j], xs[j + 1] + 1):
                    self.set(xx, yy, color)

    def triangle(self, pts, color):
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        for yy in range(min(ys), max(ys) + 1):
            row = []
            for i in range(3):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % 3]
                if (y0 <= yy < y1) or (y1 <= yy < y0):
                    row.append(x0 + (yy - y0) * (x1 - x0) // (y1 - y0))
            row.sort()
            if len(row) >= 2:
                for xx in range(row[0], row[-1] + 1):
                    self.set(xx, yy, color)


def char_width(scale):
    return 6 * scale


def text_width(text, scale):
    return len(text) * char_width(scale)


def draw_text(cv, x, y, text, scale, color):
    for ch in text:
        glyph = FONT.get(ch, FONT["?"])
        for r, row in enumerate(glyph):
            for c, bit in enumerate(row):
                if bit == "1":
                    cv.rect(x + c * scale, y + r * scale, scale, scale, color)
        x += char_width(scale)


def text_center(cv, cx, y, text, scale, color):
    draw_text(cv, cx - text_width(text, scale) // 2, y, text, scale, color)


def wrap_text(text, scale, max_width):
    lines = []
    for para in text.split("\n"):
        words = para.split(" ")
        cur = ""
        for word in words:
            trial = (cur + " " + word).strip()
            if text_width(trial, scale) <= max_width:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
    return lines


def halftone(cv, x, y, w, h, color, step, r):
    """Dot grid over a rectangle: classic print halftone texture."""
    yy = y + step // 2
    while yy < y + h:
        xx = x + step // 2
        while xx < x + w:
            cv.circle(xx, yy, r, color)
            xx += step
        yy += step


def chip(cv, x, y, text, bg, fg, scale=1):
    """Filled label chip: rect + INK frame + text. Returns its width."""
    w = text_width(text, scale) + 16
    h = 7 * scale + 10
    cv.rect(x, y, w, h, bg)
    cv.frame(x, y, w, h, INK, 2)
    draw_text(cv, x + 8, y + 5, text, scale, fg)
    return w

# ---------------------------------------------------------------- flags
def flag_us(cv, x, y, w, h):
    """Stars and stripes, bold simplified: stripes, canton, dot stars."""
    stripe = h // 7
    for s in range(7):
        cv.rect(x, y + s * stripe, w, stripe + 1,
                RED if s % 2 == 0 else LIGHT)
    canton_w = (w * 45) // 100
    canton_h = stripe * 4
    cv.rect(x, y, canton_w, canton_h, NAVY)
    for ry in range(3):
        for rx in range(4):
            cv.rect(x + 6 + rx * (canton_w // 4), y + 5 + ry * (canton_h // 3),
                    3, 3, LIGHT)


def flag_ir(cv, x, y, w, h):
    """Green, white and red horizontal thirds, red disc in the middle."""
    third = h // 3
    cv.rect(x, y, w, third + 1, (0, 122, 61))
    cv.rect(x, y + third, w, third + 1, LIGHT)
    cv.rect(x, y + 2 * third, w, h - 2 * third, (218, 0, 0))
    cv.circle(x + w // 2, y + h // 2, max(4, h // 6), (218, 0, 0))


def flag_at(cv, x, y, w, h):
    """Red, white and red horizontal thirds (Austria)."""
    third = h // 3
    cv.rect(x, y, w, third + 1, (237, 41, 36))
    cv.rect(x, y + third, w, third + 1, LIGHT)
    cv.rect(x, y + 2 * third, w, h - 2 * third, (237, 41, 36))


def flag_nl(cv, x, y, w, h):
    """Red, white and blue horizontal thirds (Netherlands)."""
    third = h // 3
    cv.rect(x, y, w, third + 1, (174, 28, 40))
    cv.rect(x, y + third, w, third + 1, LIGHT)
    cv.rect(x, y + 2 * third, w, h - 2 * third, (33, 70, 139))


def flag_eu(cv, x, y, w, h):
    """Blue field with a ring of twelve gold dots (European Union)."""
    cv.rect(x, y, w, h, (0, 51, 153))
    cx, cy = x + w // 2, y + h // 2
    rr = (h * 32) // 100
    for i in range(12):
        ang = -math.pi / 2 + i * math.pi / 6
        cv.circle(cx + int(rr * math.cos(ang)),
                  cy + int(rr * math.sin(ang)), 3, GOLD)


def flag_ua(cv, x, y, w, h):
    """Blue over yellow horizontal halves (Ukraine)."""
    cv.rect(x, y, w, h // 2 + 1, (0, 91, 187))
    cv.rect(x, y + h // 2, w, h - h // 2, (255, 213, 0))


# ---------------------------------------------------------------- pictograms
def pic_lead(cv, x, y, w, h):
    """Lead art: US and Iran flags stacked, gold 2027 chip on navy."""
    cv.rect(x, y, w, h, LEAD_FIELD)
    halftone(cv, x, y, w, h, HALFTONE_DOT, 18, 2)
    fw, fh = 120, 44
    fx = x + 18
    flag_us(cv, fx, y + 18, fw, fh)
    cv.frame(fx, y + 18, fw, fh, INK, 2)
    flag_ir(cv, fx, y + 78, fw, fh)
    cv.frame(fx, y + 78, fw, fh, INK, 2)
    draw_text(cv, fx, y + 140, "NO RUSH", 2, GOLD)
    draw_text(cv, fx, y + 158, "SEE WHAT", 2, CREAM)
    draw_text(cv, fx, y + 176, "HAPPENS", 2, CREAM)
    # gold 2027 chip, right side: the year the decision is pushed to
    cx, cy = x + 176, y + 58
    cw, chh = 168, 84
    cv.rect(cx, cy, cw, chh, GOLD)
    cv.frame(cx, cy, cw, chh, INK, 3)
    text_center(cv, cx + cw // 2, cy + 18, "2027", 6, INK)
    draw_text(cv, cx + 12, cy + chh + 12, "DECISION IN", 2, GOLD)
    draw_text(cv, cx + 12, cy + chh + 30, "2027", 2, CREAM)


def pic_voyager(cv, x, y, w, h):
    """Sun, dotted path and the probe on a near-black star field."""
    cv.rect(x, y, w, h, SPACE)
    for sx, sy in ((12, 14), (38, 34), (64, 10), (96, 26), (124, 12),
                   (140, 40), (24, 62), (58, 84), (132, 66), (16, 96),
                   (88, 52), (110, 92)):
        cv.rect(x + sx, y + sy, 2, 2, LIGHT)
    # GOLD sun, bottom-left, with a ring
    sx, sy = x + 30, y + h - 30
    cv.circle(sx, sy, 20, GOLD)
    cv.ring(sx, sy, 26, GOLD, 2)
    # dotted white path from the sun up to the probe
    for t in range(1, 10):
        px = sx + 22 + t * 9
        py = sy - 24 - t * 9
        cv.rect(px, py, 4, 4, LIGHT)
    # probe top-right: triangle dish + body + boom + PINK tip
    px, py = x + w - 44, y + 18
    cv.triangle([(px, py), (px + 24, py + 7), (px, py + 15)],
                (205, 205, 205))
    cv.rect(px - 34, py + 3, 34, 9, (150, 150, 150))
    cv.rect(px - 34, py + 1, 4, 13, (190, 190, 190))
    cv.line(px - 34, py + 8, px - 50, py + 22, (150, 150, 150))
    cv.circle(px - 52, py + 23, 4, PINK)
    # the distance, bottom-right
    draw_text(cv, x + w - 66, y + h - 42, "16 BN", 2, GOLD)
    draw_text(cv, x + w - 66, y + h - 24, "MILES", 2, GOLD)


def pic_cyclone(cv, x, y, w, h):
    """Concentric storm rings, spiral dots and rain over a coast."""
    cv.rect(x, y, w, h, STORM)
    cx, cy = x + w // 2, y + 66
    for r in (58, 45, 32, 20):
        cv.ring(cx, cy, r, LIGHT, 4)
    cv.circle(cx, cy, 9, GOLD)
    # spiral dots between the rings
    for a in range(0, 720, 18):
        ang = math.radians(a)
        r = 24 + (a % 360) * 0.09
        cv.circle(cx + int(r * math.cos(ang)), cy + int(r * math.sin(ang)),
                  2, LIGHT)
    # rain lines under the storm
    for rx in range(16, w - 8, 20):
        cv.line(x + rx, y + h - 30, x + rx - 7, y + h - 14,
                (170, 210, 240))
        cv.line(x + rx, y + h - 29, x + rx - 7, y + h - 15,
                (170, 210, 240))
    # GOLD coastline along the bottom
    cv.hline(x + 6, y + h - 8, w - 12, GOLD, 3)
    cv.hline(x + 6, y + h - 4, w - 12, GOLD, 1)


def pic_kyiv(cv, x, y, w, h):
    """Damaged grey building with cracks, Austrian and Dutch flags."""
    cv.rect(x, y, w, h, SAND)
    # building silhouette, top broken by dark triangles
    bx, by, bw, bh = x + 30, y + 18, 90, 84
    cv.rect(bx, by, bw, bh, BUILDING)
    cv.triangle([(bx, by), (bx + 30, by), (bx + 12, by + 18)], SAND)
    cv.triangle([(bx + 52, by), (bx + 90, by), (bx + 78, by + 14)], SAND)
    # windows, some dark (broken)
    for wy in range(by + 26, by + bh - 8, 18):
        for wx in range(bx + 10, bx + bw - 10, 22):
            cv.rect(wx, wy, 10, 10,
                    INK if (wx + wy) % 44 == 0 else GOLD)
    # crack lines down the facade
    cv.line(bx + 24, by + 20, bx + 18, by + 60, INK)
    cv.line(bx + 18, by + 60, bx + 30, by + 84, INK)
    cv.line(bx + 66, by + 16, bx + 72, by + 52, INK)
    cv.line(bx + 72, by + 52, bx + 62, by + 84, INK)
    # the two damaged embassies' flags, side by side at the foot
    flag_at(cv, x + 14, y + h - 30, 56, 22)
    cv.frame(x + 14, y + h - 30, 56, 22, INK, 2)
    flag_nl(cv, x + 80, y + h - 30, 56, 22)
    cv.frame(x + 80, y + h - 30, 56, 22, INK, 2)


def pic_gta(cv, x, y, w, h):
    """Neon starburst with $1.8B over a small controller, purple."""
    cv.rect(x, y, w, h, PURPLE)
    halftone(cv, x, y, w, h, (58, 32, 92), 18, 2)
    # gold starburst with the sales figure
    bx, by = x + w // 2, y + 52
    cv.star(bx, by, 48, GOLD)
    text_center(cv, bx, by - 7, "$1.8B", 2, INK)
    # small neon controller below
    cx, cy = x + 30, y + 104
    cv.rect(cx, cy, 90, 28, (24, 20, 34))
    cv.frame(cx, cy, 90, 28, TEAL, 2)
    cv.rect(cx + 10, cy + 8, 12, 12, LIGHT)
    cv.circle(cx + 46, cy + 14, 6, (140, 140, 148))
    cv.circle(cx + 70, cy + 8, 5, PINK)
    cv.circle(cx + 78, cy + 18, 5, GOLD)


def pic_hayabusa(cv, x, y, w, h):
    """Grey asteroid crossed out in red, probe drifting away."""
    cv.rect(x, y, w, h, SPACE)
    for sx, sy in ((10, 10), (36, 22), (150, 12), (128, 30), (20, 56),
                   (160, 48), (60, 60), (96, 8)):
        cv.rect(x + sx, y + sy, 2, 2, LIGHT)
    # asteroid, left, with a bold red X over it
    ax, ay = x + 46, y + h // 2
    cv.circle(ax, ay, 22, ASTEROID)
    cv.circle(ax - 6, ay - 6, 5, (110, 110, 110))
    cv.circle(ax + 8, ay + 7, 4, (110, 110, 110))
    cv.line(ax - 24, ay - 24, ax + 24, ay + 24, (220, 30, 20))
    cv.line(ax - 24, ay - 23, ax + 24, ay + 25, (220, 30, 20))
    cv.line(ax + 24, ay - 24, ax - 24, ay + 24, (220, 30, 20))
    cv.line(ax + 24, ay - 23, ax - 24, ay + 25, (220, 30, 20))
    # probe, right: dish + body + boom
    px, py = x + w - 52, y + 14
    cv.triangle([(px, py), (px + 22, py + 6), (px, py + 13)],
                (205, 205, 205))
    cv.rect(px - 30, py + 2, 30, 8, (150, 150, 150))
    cv.line(px - 30, py + 6, px - 44, py + 18, (150, 150, 150))
    cv.circle(px - 45, py + 19, 3, PINK)
    draw_text(cv, x + w - 74, y + h - 22, "NO LANDING", 1, (220, 30, 20))


def pic_europe(cv, x, y, w, h):
    """EU flag left, Ukraine flag right, side by side on SAND."""
    cv.rect(x, y, w, h, SAND)
    fw, fh = 96, 56
    fy = y + (h - fh) // 2
    flag_eu(cv, x + 8, fy, fw, fh)
    cv.frame(x + 8, fy, fw, fh, INK, 2)
    flag_ua(cv, x + w - 8 - fw, fy, fw, fh)
    cv.frame(x + w - 8 - fw, fy, fw, fh, INK, 2)

# ---------------------------------------------------------------- layout
def grid_panel(cv, x, y, w, h, kicker, kicker_color, headline, body, pic):
    """One grid story: LIGHT panel, art strip left, text right."""
    cv.rect(x, y, w, h, LIGHT)
    cv.frame(x, y, w, h, INK, 3)
    pic(cv, x + 10, y + 10, 150, h - 20)
    cv.frame(x + 10, y + 10, 150, h - 20, INK, 2)
    tx = x + 176
    ty = y + 12
    draw_text(cv, tx, ty, kicker, 1, kicker_color)
    ty += 13
    for line in wrap_text(headline, 2, 296):
        draw_text(cv, tx, ty, line, 2, INK)
        ty += 16
    ty += 3
    for line in wrap_text(body, 2, 296):
        draw_text(cv, tx, ty, line, 2, (40, 40, 40))
        ty += 15


def wide_panel(cv, x, y, w, h, kicker, kicker_color, headline, body, pic):
    """One wide story: LIGHT panel, art left, headline + body right."""
    cv.rect(x, y, w, h, LIGHT)
    cv.frame(x, y, w, h, INK, 3)
    pic(cv, x + 10, y + 10, 170, h - 20)
    cv.frame(x + 10, y + 10, 170, h - 20, INK, 2)
    tx = x + 196
    draw_text(cv, tx, y + 10, kicker, 1, kicker_color)
    draw_text(cv, tx, y + 26, headline, 3, INK)
    ty = y + 52
    for line in wrap_text(body, 2, w - 212):
        draw_text(cv, tx, ty, line, 2, (40, 40, 40))
        ty += 15


def build():
    cv = Canvas(W, H, PAPER)
    # ---- 1. masthead: black band, THE WORLD in CREAM, gold notes
    cv.rect(0, 0, 1024, 118, BLACK)
    draw_text(cv, 28, 20, "EST.", 1, GOLD)
    draw_text(cv, 28, 34, "TODAY", 1, GOLD)
    draw_text(cv, 1024 - 28 - text_width("ONE PAGE", 1), 20,
              "ONE PAGE", 1, GOLD)
    draw_text(cv, 1024 - 28 - text_width("ONLY", 1), 34, "ONLY", 1, GOLD)
    text_center(cv, W // 2, 22, "THE WORLD", 11, CREAM)
    cv.hline(0, 106, 1024, GOLD, 3)

    # ---- 2. red date band
    cv.rect(0, 118, 1024, 34, RED)
    draw_text(cv, 28, 128, "EXTRA", 2, GOLD)
    draw_text(cv, 1024 - 28 - text_width("EXTRA", 2), 128, "EXTRA", 2, GOLD)
    text_center(cv, W // 2, 128, "FRIDAY 20 NOVEMBER 2026", 2, CREAM)

    # ---- 3. lead panel: Trump / Iran on NAVY
    lx, ly, lw, lh = 16, 164, 992, 256
    cv.rect(lx, ly, lw, lh, NAVY)
    cv.frame(lx, ly, lw, lh, INK, 3)
    cv.rect(lx + 3, ly + 3, lw - 6, 4, GOLD)
    draw_text(cv, lx + 20, ly + 16, "POLITICS  •  LEAD STORY", 2, GOLD)
    draw_text(cv, lx + 20, ly + 44, "TRUMP PUTS IRAN", 5, CREAM)
    draw_text(cv, lx + 20, ly + 82, "OFF TO 2027", 5, CREAM)
    body = ("Trump says there is \"no rush\" on an Iran decision — "
            "\"see what happens\" after January 1, pushing any call "
            "into 2027.")
    ty = ly + 124
    for line in wrap_text(body, 2, 540):
        draw_text(cv, lx + 20, ty, line, 2, LEAD_BODY)
        ty += 17
    # bottom chips row
    cx = lx + 20
    cy = ly + lh - 34
    cx += chip(cv, cx, cy, "NO RUSH", GOLD, INK, 1) + 10
    cx += chip(cv, cx, cy, "AFTER JAN 1", TEAL, INK, 1) + 10
    chip(cv, cx, cy, "DECISION IN 2027", PINK, INK, 1)
    # lead art: flags + gold 2027 chip
    pic_lead(cv, lx + 612, ly + 16, 364, 224)
    cv.frame(lx + 612, ly + 16, 364, 224, INK, 2)

    # ---- 4. grid: four stories, 488x160
    grid_panel(cv, 16, 432, 488, 160, "SCIENCE", BLUE,
               "VOYAGER 1, A LIGHT-DAY FROM HOME",
               "NASA confirms the probe is one light-day from "
               "Earth — about 16 billion miles, a first for any "
               "human-made object.",
               pic_voyager)
    grid_panel(cv, 520, 432, 488, 160, "WEATHER", STORM,
               "CYCLONE AKVAN MAKES LANDFALL",
               "Severe Cyclone Akvan hits India's east coast: "
               "300,000 evacuated, schools shut, red alerts in "
               "Odisha and Andhra.",
               pic_cyclone)
    grid_panel(cv, 16, 604, 488, 160, "WAR IN UKRAINE", RED,
               "KYIV EMBASSY STRIKES",
               "Russian strikes damage the Austrian and Dutch "
               "embassies in Kyiv, drawing condemnation from "
               "Vienna and The Hague.",
               pic_kyiv)
    grid_panel(cv, 520, 604, 488, 160, "CULTURE", PURPLE,
               "GTA VI PASSES $1.8 BILLION",
               "Grand Theft Auto VI sales already pass The "
               "Odyssey's $1.80 billion global run — a record "
               "pace for the game.",
               pic_gta)

    # ---- 5. wide panel: Hayabusa2
    wide_panel(cv, 16, 776, 992, 92, "SPACE  •  JAPAN", RED,
               "HAYABUSA2 ABANDONS ASTEROID LANDING",
               "Engine trouble forces Japan's Hayabusa2 probe to "
               "change plans — no more asteroid landing.",
               pic_hayabusa)

    # ---- 6. bottom strip: Europe / Ukraine talks
    bx, by, bw, bh = 16, 880, 992, 88
    cv.rect(bx, by, bw, bh, LIGHT)
    cv.frame(bx, by, bw, bh, INK, 3)
    cv.rect(bx + 3, by + 3, bw - 6, 4, RED)
    pic_europe(cv, bx + 10, by + 10, 220, 68)
    cv.frame(bx + 10, by + 10, 220, 68, INK, 2)
    tx = bx + 246
    draw_text(cv, tx, by + 12, "EUROPE  •  DIPLOMACY", 1, RED)
    draw_text(cv, tx, by + 28, "EUROPE READY FOR UKRAINE TALKS", 2, INK)
    body = ("European leaders say they are ready for talks with "
            "Russia on ending the war in Ukraine.")
    ty = by + 50
    for line in wrap_text(body, 2, bw - 262):
        draw_text(cv, tx, ty, line, 2, (40, 40, 40))
        ty += 15

    # ---- 7. footer
    cv.hline(0, 984, 1024, INK, 3)
    cv.hline(0, 990, 1024, INK, 1)
    text_center(cv, W // 2, 998,
                "DRAWN FROM NEWS FIRST REPORTED ON FRIDAY 20 NOVEMBER 2026",
                1, GREY)
    return cv


# ---------------------------------------------------------------- png
def chunk(ctype, data):
    out = struct.pack(">I", len(data)) + ctype + data
    out += struct.pack(">I", zlib.crc32(ctype + data) & 0xFFFFFFFF)
    return out


def encode_png(cv):
    raw = bytearray()
    for yy in range(cv.h):
        raw.append(0)
        raw += cv.px[yy * cv.w * 3:(yy + 1) * cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    return png


if __name__ == "__main__":
    import sys
    data = encode_png(build())
    path = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    with open(path, "wb") as fh:
        fh.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))
