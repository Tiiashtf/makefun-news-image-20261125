#!/usr/bin/env python3
"""Draws the front page of THE WORLD TODAY for Wednesday 25 November 2026.

Pure Python 3.13 standard library only: a small pixel canvas, filled-shape
drawing, a hand-authored 5x7 dot-matrix face, and a PNG writer built on
zlib. The program needs no input files and no network: it draws the whole
front page from the story copy below and writes /output/entry.png (or
$MAKEFUN_OUTPUT_DIR/entry.png). It is deterministic: every run writes the
exact same bytes. It never removes the output directory itself; it clears
only files inside it, then writes the image.
"""

import os
import struct
import sys
import zlib

W, H = 1024, 1024

PAPER = (247, 242, 227)
INK = (18, 18, 18)
RED = (158, 27, 27)
NAVY = (18, 34, 66)
DUSK = (232, 122, 44)
FLAME = (244, 164, 42)
GOLD = (214, 158, 46)
STEEL = (46, 94, 126)
SEA = (24, 62, 96)
GREY = (112, 107, 96)
LIGHT = (233, 227, 211)
SMOKE = (150, 146, 136)
WHITE = (250, 248, 242)

# ---------------------------------------------------------------- font
# A 5x7 dot-matrix face, authored for this page. Every glyph is seven
# rows of five cells; '#' is ink, ' ' is blank. All copy on the page is
# set in capitals, in the manner of a classic broadsheet headline face.
GLYPHS = {
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
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
}


# ---------------------------------------------------------------- canvas
class Canvas:
    """A flat RGB framebuffer with filled-shape drawing helpers."""

    def __init__(self, width, height, background):
        self.w = width
        self.h = height
        self.px = bytearray(background * (width * height))

    def put(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(colour)

    def rect(self, x, y, w, h, colour):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            self.px[base:(base + (x1 - x0) * 3)] = bytes(colour) * (x1 - x0)

    def frame(self, x, y, w, h, colour, t=1):
        self.rect(x, y, w, t, colour)
        self.rect(x, y + h - t, w, t, colour)
        self.rect(x, y, t, h, colour)
        self.rect(x + w - t, y, t, h, colour)

    def hline(self, x, y, w, colour, t=1):
        self.rect(x, y, w, t, colour)

    def vline(self, x, y, h, colour, t=1):
        self.rect(x, y, t, h, colour)

    def disc(self, cx, cy, r, colour):
        for dy in range(-r, r + 1):
            half = int((r * r - dy * dy) ** 0.5)
            self.rect(cx - half, cy + dy, half * 2 + 1, 1, colour)

    def triangle(self, x0, y0, x1, y1, x2, y2, colour):
        """Filled triangle by scanlines, vertices in any order."""
        pts = sorted(((x0, y0), (x1, y1), (x2, y2)), key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        if ay == cy:
            return
        def edge_x(xa, ya, xb, yb, y):
            if yb == ya:
                return xa
            return xa + (xb - xa) * (y - ya) / (yb - ya)
        for y in range(ay, cy + 1):
            if y < by:
                xa = edge_x(ax, ay, bx, by, y)
                xb = edge_x(ax, ay, cx, cy, y)
            else:
                xa = edge_x(bx, by, cx, cy, y)
                xb = edge_x(ax, ay, cx, cy, y)
            lo, hi = int(min(xa, xb)), int(max(xa, xb))
            self.rect(lo, y, hi - lo + 1, 1, colour)

    def vgrad(self, x, y, w, h, top, bottom):
        for i in range(h):
            t = i / max(1, h - 1)
            c = tuple(int(top[k] + (bottom[k] - top[k]) * t) for k in range(3))
            self.rect(x, y + i, w, 1, c)


# ---------------------------------------------------------------- text
def glyph_width(scale):
    return 5 * scale + scale  # five cells plus one cell of tracking


def text_width(s, scale):
    if not s:
        return 0
    return len(s) * glyph_width(scale) - scale


def draw_text(cv, s, x, y, scale, colour):
    """Draw capitals text left-aligned at (x, y); returns the width used."""
    cx = x
    for ch in s:
        rows = GLYPHS.get(ch, GLYPHS[" "])
        for r, row in enumerate(rows):
            for c, cell in enumerate(row):
                if cell == "1":
                    cv.rect(cx + c * scale, y + r * scale, scale, scale, colour)
        cx += glyph_width(scale)
    return cx - x - scale


def draw_centred(cv, s, cx, y, scale, colour):
    return draw_text(cv, s, cx - text_width(s, scale) // 2, y, scale, colour)


def wrap_text(s, max_px, scale):
    """Greedy word wrap of capitals text to a pixel width."""
    words = s.split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_px or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_block(cv, s, x, y, max_px, scale, colour, leading=2):
    lines = wrap_text(s, max_px, scale)
    for i, line in enumerate(lines):
        draw_text(cv, line, x, y + i * (7 * scale + leading), scale, colour)
    return y + len(lines) * (7 * scale + leading)


# ---------------------------------------------------------------- png
def png_bytes(cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * stride:(y + 1) * stride]

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )


# ---------------------------------------------------------------- the page
def draw_refinery(cv, x, y, w, h):
    """Night refinery under a burning sky: the lead picture."""
    cv.vgrad(x, y, w, h, (16, 30, 60), (148, 66, 36))
    # stars, fixed positions so the picture never changes
    for sx, sy in [(70, 14), (180, 30), (320, 12), (470, 26), (620, 10),
                   (760, 28), (880, 12), (930, 34), (250, 44), (540, 8)]:
        cv.rect(x + sx, y + sy, 2, 2, WHITE)
    ground_y = y + h - 26
    cv.rect(x, ground_y, w, 26, (10, 10, 14))
    # storage tanks, flat-topped with a pale rim
    cv.rect(x + 60, ground_y - 52, 130, 52, (12, 12, 18))
    cv.rect(x + 60, ground_y - 52, 130, 4, (52, 52, 64))
    cv.rect(x + 720, ground_y - 62, 160, 62, (12, 12, 18))
    cv.rect(x + 720, ground_y - 62, 160, 4, (52, 52, 64))
    # distillation columns
    for cx in (280, 330, 380):
        cv.rect(x + cx, ground_y - 96, 26, 96, (14, 14, 20))
        cv.disc(x + cx + 13, ground_y - 96, 13, (14, 14, 20))
        for wy in range(ground_y - 88, ground_y - 8, 14):
            cv.rect(x + cx + 9, wy, 8, 5, GOLD)
    # chimneys with smoke
    for cx in (520, 566):
        cv.rect(x + cx, ground_y - 84, 16, 84, (16, 16, 22))
        cv.rect(x + cx - 3, ground_y - 88, 22, 6, (16, 16, 22))
    for sx, sy, r in [(528, 26, 10), (540, 12, 13), (556, 2, 9),
                      (574, 30, 8), (586, 16, 11)]:
        cv.disc(x + sx, y + sy, r, SMOKE)
    # flames over the left tank and the flare stack
    for fx in (105, 140, 175):
        cv.triangle(x + fx - 16, ground_y - 50, x + fx + 16, ground_y - 50,
                    x + fx, ground_y - 96, DUSK)
    for fx in (118, 152):
        cv.triangle(x + fx - 11, ground_y - 50, x + fx + 11, ground_y - 50,
                    x + fx, ground_y - 82, FLAME)
    cv.disc(x + 128, ground_y - 58, 10, GOLD)
    cv.disc(x + 162, ground_y - 56, 8, GOLD)
    # flare stack flame, far right
    cv.rect(x + 920, ground_y - 78, 10, 78, (14, 14, 20))
    cv.triangle(x + 913, ground_y - 78, x + 937, ground_y - 78,
                x + 925, ground_y - 108, FLAME)
    cv.disc(x + 925, ground_y - 84, 8, GOLD)


def draw_block_flats(cv, x, y, w, h):
    """A damaged apartment block, smoke rising: the Zaporizhzhia picture."""
    cv.rect(x, y, w, h, LIGHT)
    cv.frame(x, y, w, h, INK, 1)
    bx, by, bw, bh = x + 40, y + 8, 210, h - 16
    cv.rect(bx, by, bw, bh, (96, 104, 116))
    cv.triangle(bx + bw - 52, by, bx + bw, by, bx + bw, by + 34, INK)
    for wy in range(by + 8, by + bh - 6, 11):
        for wx in range(bx + 10, bx + bw - 12, 24):
            cv.rect(wx, wy, 11, 7, PAPER)
    cv.rect(bx, by + bh - 4, bw, 4, INK)
    for sx, sy, r in [(bx + 158, y + 2, 7), (bx + 176, y - 4, 9),
                      (bx + 194, y + 4, 6)]:
        cv.disc(sx, sy, r, SMOKE)
    # rubble at the foot of the block
    for rx, rw in [(bx - 8, 30), (bx + 24, 22), (bx + 90, 26), (bx + 150, 30)]:
        cv.triangle(rx, by + bh, rx + rw, by + bh, rx + rw // 2,
                    by + bh - 10, INK)
    # a smaller block behind, to the right
    cx, cy, cw, ch = x + 300, y + 26, 130, h - 34
    cv.rect(cx, cy, cw, ch, (128, 132, 140))
    for wy in range(cy + 7, cy + ch - 5, 11):
        for wx in range(cx + 9, cx + cw - 11, 24):
            cv.rect(wx, wy, 11, 7, PAPER)
    cv.rect(cx, cy + ch - 3, cw, 3, INK)


def draw_contract(cv, x, y, w, h):
    """A signed contract and a departing plane: the recruitment picture."""
    cv.rect(x, y, w, h, LIGHT)
    cv.frame(x, y, w, h, INK, 1)
    # the contract
    dx, dy = x + 36, y + 10
    cv.rect(dx, dy, 150, h - 20, WHITE)
    cv.frame(dx, dy, 150, h - 20, INK, 1)
    for i in range(4):
        cv.rect(dx + 12, dy + 12 + i * 8, 110 - i * 18, 2, GREY)
    cv.disc(dx + 118, dy + h - 34, 10, RED)
    cv.rect(dx + 12, dy + h - 32, 52, 2, INK)
    # the plane, heading away
    px, py = x + 250, y + 22
    cv.rect(px, py, 150, 8, INK)
    cv.triangle(px + 150, py, px + 176, py + 4, px + 150, py + 8, INK)
    cv.triangle(px + 70, py + 8, px + 96, py + 8, px + 78, py + 26, INK)
    cv.triangle(px + 30, py, px + 52, py, px + 40, py - 16, INK)
    for tx in range(0, 5):
        cv.disc(px - 14 - tx * 16, py + 2 + tx * 2, 2, GREY)


def draw_tanker(cv, x, y, w, h):
    """A tanker on a dark sea at dusk: the Hormuz strip."""
    cv.vgrad(x, y, w, h, (24, 62, 96), (66, 116, 158))
    for wx in range(x + 20, x + w - 20, 90):
        cv.hline(wx, y + h - 14, 52, (150, 190, 220), 2)
        cv.hline(wx + 30, y + h - 26, 40, (120, 165, 205), 2)
    hx = x + 330
    cv.rect(hx, y + 28, 300, 26, (10, 10, 14))
    cv.triangle(hx + 300, y + 28, hx + 336, y + 41, hx + 300, y + 54, (10, 10, 14))
    cv.rect(hx, y + 28, 300, 3, (60, 60, 70))
    cv.rect(hx + 40, y + 10, 60, 18, (240, 238, 230))
    cv.rect(hx + 46, y + 14, 12, 5, INK)
    cv.rect(hx + 66, y + 14, 12, 5, INK)
    cv.rect(hx + 200, y + 4, 18, 24, (180, 60, 40))
    cv.disc(hx + 209, y + 0, 7, SMOKE)
    cv.disc(hx + 222, y - 8, 9, SMOKE)
    # a small fire on the foredeck
    cv.triangle(hx + 268, y + 28, hx + 288, y + 28, hx + 278, y + 8, FLAME)
    cv.disc(hx + 278, y + 22, 6, GOLD)


def build_page():
    cv = Canvas(W, H, PAPER)
    cv.frame(16, 16, 992, 992, INK, 3)
    cv.frame(22, 22, 980, 980, INK, 1)

    # masthead
    draw_centred(cv, "THE WORLD TODAY", W // 2, 44, 8, INK)
    cv.hline(28, 112, 968, INK, 2)
    draw_centred(cv, "WEDNESDAY 25 NOVEMBER 2026", W // 2, 122, 4, RED)
    cv.hline(28, 158, 968, INK, 1)
    draw_centred(cv, "UKRAINE - THE GULF - ASIA - HUNGER - SPORT",
                 W // 2, 166, 2, GREY)

    # lead story
    draw_centred(cv, "DRONES HIT THREE", W // 2, 196, 5, INK)
    draw_centred(cv, "RUSSIAN REFINERIES", W // 2, 237, 5, INK)
    draw_refinery(cv, 28, 284, 968, 138)
    draw_block(cv,
               "BLASTS AND A LARGE FIRE WERE REPORTED NEAR THREE ROSNEFT "
               "REFINERIES IN RUSSIA'S SAMARA REGION OVERNIGHT. UKRAINIAN "
               "MEDIA REPORTED EXPLOSIONS NEAR PLANTS IN SAMARA, "
               "NOVOKUIBYSHEVSK AND SYZRAN. THE STRIKES WERE NOT OFFICIALLY "
               "CONFIRMED.",
               28, 434, 968, 2, INK)
    cv.hline(28, 494, 968, INK, 2)

    # middle columns
    draw_text(cv, "ZAPORIZHZHIA", 28, 506, 3, RED)
    draw_text(cv, "TOLL RISES TO 50 INJURED", 28, 530, 3, INK)
    draw_block_flats(cv, 28, 584, 472, 64)
    draw_block(cv,
               "A RUSSIAN STRIKE ON ZAPORIZHZHIA KILLED TWO AND INJURED 50, "
               "INCLUDING AN INFANT AND FOUR CHILDREN. HOMES AND A "
               "FIVE-STOREY BLOCK WERE DAMAGED.",
               28, 660, 472, 2, INK)
    cv.vline(511, 506, 230, INK, 1)
    draw_text(cv, "HIRED ABROAD", 524, 506, 3, RED)
    draw_text(cv, "LURED BY JOBS,", 524, 530, 3, INK)
    draw_text(cv, "SENT TO THE FRONT", 524, 554, 3, INK)
    draw_contract(cv, 524, 584, 472, 64)
    draw_block(cv,
               "RUSSIA IS RECRUITING INDONESIAN AND FILIPINO CITIZENS WITH "
               "CIVILIAN JOB OFFERS, THEN SENDING SOME TO THE FRONT. "
               "JAKARTA PROBES POSSIBLE TRAFFICKING.",
               524, 660, 472, 2, INK)
    cv.hline(28, 748, 968, INK, 2)

    # the Gulf
    draw_centred(cv, "IRAN CLAIMS NEW TANKER BLASTS IN HORMUZ",
                 W // 2, 760, 4, INK)
    draw_centred(cv, "TEHRAN SAYS MORE SHIPS HIT MINES; US COMMAND SAYS THE LANES ARE CLEAR",
                 W // 2, 796, 2, INK)
    draw_centred(cv, "COALITION STRIKES HODEIDAH PORT OVERNIGHT AFTER WARNING CIVILIANS TO LEAVE",
                 W // 2, 818, 2, INK)
    draw_tanker(cv, 28, 840, 968, 66)
    cv.hline(28, 918, 968, INK, 1)

    # briefs
    briefs = [
        ("WFP: 266 MILLION FACE ACUTE HUNGER",
         "GAZA TOLL REACHES 74,746, WAFA SAYS"),
        ("MOSCOW CALLS SHIP STRIKES 'TERRORISM'",
         "ENGLAND LEVEL T20 SERIES IN AUSTRALIA"),
    ]
    for row, (left, right) in enumerate(briefs):
        yy = 928 + row * 24
        cv.rect(28, yy + 3, 8, 8, RED)
        draw_text(cv, left, 44, yy, 2, INK)
        cv.rect(524, yy + 3, 8, 8, RED)
        draw_text(cv, right, 540, yy, 2, INK)

    draw_centred(cv, "ALL STORIES REPORTED WEDNESDAY 25 NOVEMBER 2026",
                 W // 2, 978, 2, GREY)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    # Clear only the CONTENTS of the output directory, never the dir itself.
    # Best effort: a stray file another owner left behind must not fail us.
    for name in os.listdir(out_dir):
        path = os.path.join(out_dir, name)
        try:
            if os.path.isfile(path) or os.path.islink(path):
                os.remove(path)
        except OSError:
            pass
    data = png_bytes(build_page())
    target = os.path.join(out_dir, "entry.png")
    with open(target, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes)" % (target, len(data)))


if __name__ == "__main__":
    main()
