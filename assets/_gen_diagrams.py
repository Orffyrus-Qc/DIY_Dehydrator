#!/usr/bin/env python3
"""Generate labeled diagrams for DIY_Dehydrator Logseq graph."""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
FONT = r"C:\Windows\Fonts\segoeui.ttf"
FONT_BD = r"C:\Windows\Fonts\segoeuib.ttf"
FONT_MONO = r"C:\Windows\Fonts\consola.ttf"

# Palette
BG = (248, 250, 252)
INK = (15, 23, 42)
MUTED = (100, 116, 139)
LINE = (148, 163, 184)
WHITE = (255, 255, 255)
BLUE = (37, 99, 235)
BLUE_L = (219, 234, 254)
GREEN = (22, 163, 74)
GREEN_L = (220, 252, 231)
AMBER = (217, 119, 6)
AMBER_L = (254, 243, 199)
RED = (220, 38, 38)
RED_L = (254, 226, 226)
PURPLE = (124, 58, 237)
PURPLE_L = (237, 233, 254)
SLATE = (51, 65, 85)
CYAN = (8, 145, 178)
CYAN_L = (207, 250, 254)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_BD if bold else FONT
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.truetype(FONT, size)


def mono(size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(FONT_MONO, size)
    except OSError:
        return font(size)


def new_img(w: int, h: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    im = Image.new("RGB", (w, h), BG)
    return im, ImageDraw.Draw(im)


def text_size(draw: ImageDraw.ImageDraw, text: str, f: ImageFont.ImageFont) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=f)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def center_text(draw, xy, text, f, fill=INK):
    tw, th = text_size(draw, text, f)
    x, y = xy
    draw.text((x - tw / 2, y - th / 2), text, font=f, fill=fill)


def rounded_box(draw, box, fill, outline=LINE, width=2, radius=14):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def arrow(draw, start, end, color=INK, width=3, head=12):
    x0, y0 = start
    x1, y1 = end
    draw.line([start, end], fill=color, width=width)
    ang = math.atan2(y1 - y0, x1 - x0)
    left = (x1 - head * math.cos(ang - 0.4), y1 - head * math.sin(ang - 0.4))
    right = (x1 - head * math.cos(ang + 0.4), y1 - head * math.sin(ang + 0.4))
    draw.polygon([end, left, right], fill=color)


def title(draw, text, x=40, y=28):
    draw.text((x, y), text, font=font(28, True), fill=INK)
    draw.text((x, y + 38), "DIY ESP32 Dehydrator — Logseq notes", font=font(14), fill=MUTED)


def save(im: Image.Image, name: str):
    path = OUT / name
    im.save(path, "PNG", optimize=True)
    print(f"wrote {path} ({path.stat().st_size} bytes)")


# ── 1. Architecture ──────────────────────────────────────────────────────────
def diagram_architecture():
    im, d = new_img(1400, 900)
    title(d, "System architecture")

    # Chamber
    rounded_box(d, (60, 100, 520, 520), WHITE, SLATE, 3, 18)
    center_text(d, (290, 130), "Dehydrator chamber", font(18, True), SLATE)

    # Trays
    for i, y in enumerate([180, 240, 300, 360]):
        rounded_box(d, (110, y, 360, y + 40), (241, 245, 249), LINE, 1, 8)
        d.text((125, y + 10), f"Tray {i + 1}", font=font(14), fill=MUTED)

    # Heater / fan
    rounded_box(d, (110, 430, 250, 490), AMBER_L, AMBER, 2, 10)
    center_text(d, (180, 460), "Heater (SSR)", font(14, True), AMBER)
    rounded_box(d, (280, 430, 420, 490), CYAN_L, CYAN, 2, 10)
    center_text(d, (350, 460), "Fan PWM", font(14, True), CYAN)

    # Sensors block
    rounded_box(d, (380, 170, 500, 400), GREEN_L, GREEN, 2, 12)
    center_text(d, (440, 195), "Sensors", font(15, True), GREEN)
    for i, label in enumerate(["SHT31 T+RH", "DS18B20 tray", "DS18B20 exh.", "Door reed"]):
        d.text((395, 230 + i * 35), "• " + label, font=font(13), fill=INK)

    # ESP32
    rounded_box(d, (600, 160, 980, 480), BLUE_L, BLUE, 3, 18)
    center_text(d, (790, 195), "ESP32 controller", font(20, True), BLUE)
    modules = [
        (620, 240, 780, 300, "Sense + filter"),
        (800, 240, 960, 300, "PID + states"),
        (620, 320, 780, 380, "Warnings"),
        (800, 320, 960, 380, "Recommend"),
        (620, 400, 780, 460, "LittleFS logs"),
        (800, 400, 960, 460, "NVS config"),
    ]
    for x0, y0, x1, y1, lab in modules:
        rounded_box(d, (x0, y0, x1, y1), WHITE, BLUE, 1, 10)
        center_text(d, ((x0 + x1) / 2, (y0 + y1) / 2), lab, font(13), SLATE)

    # Soft AP / phone
    rounded_box(d, (1040, 180, 1340, 360), PURPLE_L, PURPLE, 3, 18)
    center_text(d, (1190, 220), "Phone / laptop", font(18, True), PURPLE)
    d.text((1070, 260), "Wi‑Fi Soft-AP", font=font(15), fill=INK)
    d.text((1070, 290), "http://192.168.4.1", font=mono(14), fill=PURPLE)
    d.text((1070, 325), "Stats · Warn · Tips", font=font(14), fill=MUTED)

    # Safety strip
    rounded_box(d, (600, 520, 980, 620), RED_L, RED, 2, 14)
    center_text(d, (790, 545), "Safety layer", font(16, True), RED)
    center_text(d, (790, 580), "Thermal fuse · door interlock · T_max · FAULT safe-state", font(13), SLATE)

    # Power
    rounded_box(d, (1040, 420, 1340, 620), WHITE, LINE, 2, 14)
    center_text(d, (1190, 455), "Power domains", font(16, True), SLATE)
    d.text((1070, 490), "Mains → heater + SSR", font=font(14), fill=INK)
    d.text((1070, 525), "12 V → fans", font=font(14), fill=INK)
    d.text((1070, 560), "5 V / 3.3 V → ESP + sensors", font=font(14), fill=INK)

    # Arrows
    arrow(d, (500, 285), (600, 285), BLUE, 3)
    arrow(d, (790, 480), (790, 520), RED, 3)
    arrow(d, (420, 490), (620, 430), AMBER, 2)
    arrow(d, (350, 490), (700, 430), CYAN, 2)
    arrow(d, (980, 270), (1040, 270), PURPLE, 3)
    arrow(d, (1190, 360), (1190, 420), MUTED, 2)
    d.text((990, 250), "telemetry", font=font(12), fill=PURPLE)
    d.text((510, 255), "I²C / 1-Wire", font=font(12), fill=BLUE)

    # Legend bottom
    d.text((60, 700), "Layers: Sense → Decide (PID + state machine) → Actuate → Present (AP web) → Remember (logs)", font=font(15), fill=MUTED)
    d.text((60, 740), "Local-first: no cloud required. Control continues if phone disconnects.", font=font(15), fill=MUTED)
    d.text((60, 820), "Diagram for Logseq graph DIY_Dehydrator", font=font(12), fill=LINE)
    save(im, "architecture.png")


# ── 2. Airflow ───────────────────────────────────────────────────────────────
def diagram_airflow():
    im, d = new_img(1200, 900)
    title(d, "Chamber airflow layout")

    # Outer chamber
    rounded_box(d, (200, 100, 1000, 780), WHITE, SLATE, 4, 12)

    # Intake
    rounded_box(d, (40, 400, 180, 500), CYAN_L, CYAN, 2, 10)
    center_text(d, (110, 450), "INTAKE", font(14, True), CYAN)
    arrow(d, (180, 450), (220, 450), CYAN, 4)

    # Heater zone bottom
    rounded_box(d, (260, 620, 940, 720), AMBER_L, AMBER, 2, 10)
    center_text(d, (600, 655), "Heater zone (hot air rises / forced)", font(16, True), AMBER)
    center_text(d, (600, 690), "SSR-switched element + thermal fuse in series", font(13), SLATE)

    # Fan
    rounded_box(d, (260, 540, 420, 600), CYAN_L, CYAN, 2, 10)
    center_text(d, (340, 570), "Fan", font(16, True), CYAN)

    # Trays with flow arrows
    for i, y in enumerate([160, 250, 340, 430]):
        rounded_box(d, (320, y, 880, y + 55), (241, 245, 249), LINE, 2, 8)
        d.text((340, y + 16), f"Food tray {i + 1}", font=font(15), fill=INK)
        # flow chevrons
        for x in range(500, 820, 60):
            arrow(d, (x, y + 28), (x + 35, y + 28), BLUE, 2, 8)

    # Exhaust
    rounded_box(d, (1020, 160, 1160, 260), GREEN_L, GREEN, 2, 10)
    center_text(d, (1090, 195), "EXHAUST", font(14, True), GREEN)
    center_text(d, (1090, 225), "+ RH out", font(12), MUTED)
    arrow(d, (1000, 200), (1020, 200), GREEN, 4)

    # Sensor markers
    def sensor_dot(xy, label, color=GREEN):
        x, y = xy
        d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=color, outline=WHITE, width=2)
        d.text((x + 16, y - 10), label, font=font(13, True), fill=color)

    sensor_dot((700, 520), "SHT31 mid-air (T+RH)", GREEN)
    sensor_dot((850, 280), "DS18B20 tray", BLUE)
    sensor_dot((920, 180), "DS18B20 exhaust", PURPLE)
    sensor_dot((960, 480), "Door reed", AMBER)

    # Side notes
    d.text((200, 810), "Tip: place primary climate sensor in free air, not on the heater. Baffles between trays improve uniformity.", font=font(14), fill=MUTED)
    save(im, "airflow_layout.png")


# ── 3. Electrical ────────────────────────────────────────────────────────────
def diagram_electrical():
    im, d = new_img(1400, 950)
    title(d, "Electrical overview (conceptual)")

    # Warning banner
    rounded_box(d, (60, 90, 1340, 140), RED_L, RED, 2, 10)
    center_text(d, (700, 115), "MAINS HAZARD — thermal fuse independent of ESP32 · earth chassis · SSR isolation", font(15, True), RED)

    # Mains path
    d.text((60, 170), "Mains domain", font=font(18, True), fill=RED)
    boxes_m = [
        (60, 210, 220, 290, "LINE", RED_L, RED),
        (260, 210, 420, 290, "FUSE", AMBER_L, AMBER),
        (460, 210, 680, 290, "THERMAL FUSE", RED_L, RED),
        (720, 210, 920, 290, "HEATER", AMBER_L, AMBER),
        (960, 210, 1160, 290, "SSR load", SLATE, LINE),
        (1200, 210, 1340, 290, "NEUTRAL", RED_L, RED),
    ]
    for x0, y0, x1, y1, lab, fill, out in boxes_m:
        rounded_box(d, (x0, y0, x1, y1), fill, out, 2, 10)
        center_text(d, ((x0 + x1) / 2, (y0 + y1) / 2), lab, font(14, True), INK)
    for x in [220, 420, 680, 920, 1160]:
        arrow(d, (x, 250), (x + 40, 250), INK, 3)

    # SSR control
    d.text((960, 320), "SSR input (low voltage, isolated)", font=font(13), fill=MUTED)
    arrow(d, (1060, 360), (1060, 290), BLUE, 3)

    # ESP32 block
    rounded_box(d, (480, 380, 920, 720), BLUE_L, BLUE, 3, 16)
    center_text(d, (700, 415), "ESP32 DevKit (3.3 V logic)", font(18, True), BLUE)
    pins = [
        "GPIO25 → heater SSR input",
        "GPIO26 → fan MOSFET PWM",
        "GPIO27 → buzzer",
        "GPIO34 → door (ext. pull-up)",
        "GPIO21/22 → I²C SHT31",
        "GPIO4 → 1-Wire DS18B20",
    ]
    for i, p in enumerate(pins):
        d.text((520, 460 + i * 35), p, font=mono(15), fill=INK)

    # LV supplies
    rounded_box(d, (60, 400, 400, 560), WHITE, LINE, 2, 12)
    center_text(d, (230, 430), "LV supplies", font(16, True), SLATE)
    d.text((90, 470), "5 V / ≥2 A → ESP32 USB", font=font(14), fill=INK)
    d.text((90, 505), "12 V fused → fans", font=font(14), fill=INK)
    d.text((90, 540), "Common GND (LV only)", font=font(14), fill=MUTED)

    # Fan driver
    rounded_box(d, (60, 600, 400, 760), CYAN_L, CYAN, 2, 12)
    center_text(d, (230, 640), "Fan driver", font(16, True), CYAN)
    d.text((90, 680), "N-MOSFET low-side (e.g. IRLZ44N)", font=font(14), fill=INK)
    d.text((90, 715), "PWM ~25 kHz · flyback diode", font=font(14), fill=INK)

    # Sensors
    rounded_box(d, (1000, 400, 1340, 760), GREEN_L, GREEN, 2, 12)
    center_text(d, (1170, 435), "Sensors", font(16, True), GREEN)
    for i, s in enumerate(["SHT31/40 I²C 3.3 V", "DS18B20 + 4.7 kΩ pull-up", "Door reed → GPIO", "Optional current sense"]):
        d.text((1030, 490 + i * 45), "• " + s, font=font(14), fill=INK)

    # Arrows to ESP
    arrow(d, (400, 480), (480, 480), MUTED, 2)
    arrow(d, (400, 680), (480, 620), CYAN, 2)
    arrow(d, (1000, 560), (920, 560), GREEN, 2)
    arrow(d, (700, 720), (1060, 360), BLUE, 2)
    d.text((820, 700), "heater GPIO", font=font(12), fill=BLUE)

    d.text((60, 860), "Not a construction permit drawing — verify wire gauge, fuse rating, and local electrical code before mains work.", font=font(14), fill=MUTED)
    save(im, "electrical_overview.png")


# ── 4. State machine ─────────────────────────────────────────────────────────
def diagram_state_machine():
    im, d = new_img(1400, 820)
    title(d, "Control state machine")

    states = [
        # name, x, y, fill, outline
        ("IDLE", 80, 200, WHITE, SLATE),
        ("PREHEAT", 320, 200, AMBER_L, AMBER),
        ("RUNNING", 560, 200, GREEN_L, GREEN),
        ("FINISHING", 800, 200, CYAN_L, CYAN),
        ("COOLDOWN", 1040, 200, BLUE_L, BLUE),
        ("DONE", 1200, 380, GREEN_L, GREEN),
        ("PAUSED", 560, 420, AMBER_L, AMBER),
        ("FAULT", 320, 560, RED_L, RED),
        ("RECOVER", 80, 420, PURPLE_L, PURPLE),
    ]
    w, h = 160, 70
    centers = {}
    for name, x, y, fill, out in states:
        rounded_box(d, (x, y, x + w, y + h), fill, out, 3, 14)
        center_text(d, (x + w / 2, y + h / 2), name, font(16, True), INK)
        centers[name] = (x + w / 2, y + h / 2)

    def link(a, b, label="", color=INK, dy=0):
        x0, y0 = centers[a]
        x1, y1 = centers[b]
        # edge points
        if abs(x1 - x0) > abs(y1 - y0):
            if x1 > x0:
                s, e = (x0 + 80, y0 + dy), (x1 - 80, y1 + dy)
            else:
                s, e = (x0 - 80, y0 + dy), (x1 + 80, y1 + dy)
        else:
            if y1 > y0:
                s, e = (x0, y0 + 35), (x1, y1 - 35)
            else:
                s, e = (x0, y0 - 35), (x1, y1 + 35)
        arrow(d, s, e, color, 3)
        if label:
            mx, my = (s[0] + e[0]) / 2, (s[1] + e[1]) / 2 - 12
            tw, th = text_size(d, label, font(12))
            d.rectangle((mx - tw / 2 - 4, my - 2, mx + tw / 2 + 4, my + th + 2), fill=BG)
            center_text(d, (mx, my + th / 2), label, font(12), color)

    link("IDLE", "PREHEAT", "Start", GREEN)
    link("PREHEAT", "RUNNING", "T in band", GREEN)
    link("RUNNING", "FINISHING", "RH / time", CYAN)
    link("FINISHING", "COOLDOWN", "confirm", BLUE)
    link("COOLDOWN", "DONE", "cool OK", GREEN)
    link("RUNNING", "PAUSED", "door / user", AMBER, dy=20)
    link("PAUSED", "RUNNING", "resume", AMBER, dy=-20)
    # FAULT from many — show generic
    arrow(d, (400, 270), (400, 560), RED, 3)
    d.text((410, 400), "CRITICAL", font=font(12, True), fill=RED)
    link("FAULT", "RECOVER", "ack + clear", PURPLE)
    link("RECOVER", "IDLE", "review", PURPLE)
    arrow(d, (1280, 415), (1280, 235), MUTED, 2)
    d.text((1290, 320), "Reset", font=font(12), fill=MUTED)

    # Legend box
    rounded_box(d, (560, 540, 1340, 760), WHITE, LINE, 2, 12)
    d.text((590, 560), "Finish criteria (RUNNING → FINISHING)", font=font(16, True), fill=INK)
    d.text((590, 600), "• RH < rh_end for rh_hold_min minutes", font=font(14), fill=SLATE)
    d.text((590, 635), "• OR RH slope ≈ 0 after t_min  (AND elapsed < t_max)", font=font(14), fill=SLATE)
    d.text((590, 670), "• MAX_TIME → force finish with WARN", font=font(14), fill=SLATE)
    d.text((590, 710), "Any CRITICAL → FAULT (heater duty = 0, alarm, UI red banner)", font=font(14), fill=RED)
    save(im, "state_machine.png")


# ── 5. Web UI mockup ─────────────────────────────────────────────────────────
def diagram_web_ui():
    im, d = new_img(1200, 900)
    title(d, "Web AP dashboard (mockup)")

    # Phone frame
    rounded_box(d, (80, 100, 480, 820), (15, 23, 42), SLATE, 4, 28)
    rounded_box(d, (100, 140, 460, 780), (30, 41, 59), (51, 65, 85), 2, 18)

    # Status bar
    d.text((120, 155), "Dehydrator-A1B2", font=font(12), fill=(148, 163, 184))
    d.text((360, 155), "AP", font=font(12, True), fill=GREEN)

    # Big state
    rounded_box(d, (120, 190, 440, 270), (22, 101, 52), GREEN, 0, 12)
    center_text(d, (280, 220), "RUNNING", font(22, True), WHITE)
    center_text(d, (280, 250), "Profile: Apple slices", font(13), (187, 247, 208))

    # Metrics
    metrics = [
        (120, 290, 270, 380, "57.2 °C", "Air temp"),
        (290, 290, 440, 380, "34 %", "Humidity"),
        (120, 400, 270, 490, "68 %", "Heater duty"),
        (290, 400, 440, 490, "72 %", "Fan"),
    ]
    for x0, y0, x1, y1, big, small in metrics:
        rounded_box(d, (x0, y0, x1, y1), (51, 65, 85), (71, 85, 105), 1, 10)
        center_text(d, ((x0 + x1) / 2, y0 + 35), big, font(22, True), WHITE)
        center_text(d, ((x0 + x1) / 2, y0 + 70), small, font(12), (148, 163, 184))

    # Sparkline area
    rounded_box(d, (120, 510, 440, 600), (51, 65, 85), (71, 85, 105), 1, 10)
    d.text((135, 520), "T / RH last 60 min", font=font(12), fill=(148, 163, 184))
    pts_t = []
    pts_rh = []
    for i in range(20):
        x = 140 + i * 14
        yt = 580 - int(20 + 15 * math.sin(i / 3) + i)
        yrh = 590 - int(10 + 8 * math.cos(i / 2.5))
        pts_t.append((x, yt))
        pts_rh.append((x, yrh))
    d.line(pts_t, fill=(96, 165, 250), width=2)
    d.line(pts_rh, fill=(52, 211, 153), width=2)

    # Warning + recommend cards
    rounded_box(d, (120, 620, 440, 680), (120, 53, 15), AMBER, 1, 10)
    d.text((135, 635), "WARN  Gradient high — tray 3", font=font(13, True), fill=AMBER_L)
    d.text((135, 655), "Suggest +15% fan", font=font(12), fill=(253, 230, 138))

    rounded_box(d, (120, 695, 440, 755), (76, 29, 149), PURPLE, 1, 10)
    d.text((135, 710), "TIP  Apply fan boost?", font=font(13, True), fill=PURPLE_L)
    d.text((135, 730), "[ Apply ]   [ Dismiss ]", font=font(12), fill=WHITE)

    # Desktop panel
    rounded_box(d, (540, 140, 1140, 780), WHITE, LINE, 3, 16)
    d.text((570, 165), "Desktop browser view — same UI", font=font(18, True), fill=INK)
    d.text((570, 205), "http://192.168.4.1  ·  offline assets (no CDN)", font=mono(14), fill=MUTED)

    panels = [
        (570, 250, 840, 400, "Stats", "Session time, energy est.,\ndRH/dt, ETA, history list", BLUE_L, BLUE),
        (860, 250, 1110, 400, "Warnings", "INFO / WARN / CRITICAL\nack + history", AMBER_L, AMBER),
        (570, 430, 840, 580, "Profiles", "Apple, herbs, jerky…\noverrides before Start", GREEN_L, GREEN),
        (860, 430, 1110, 580, "Recommend", "Explainable rules\nApply / Dismiss", PURPLE_L, PURPLE),
        (570, 610, 1110, 740, "Controls", "Start · Pause · Stop · Setpoint · Settings (PIN for safety limits)", CYAN_L, CYAN),
    ]
    for x0, y0, x1, y1, head, body, fill, out in panels:
        rounded_box(d, (x0, y0, x1, y1), fill, out, 2, 12)
        d.text((x0 + 16, y0 + 16), head, font=font(16, True), fill=out)
        for j, line in enumerate(body.split("\n")):
            d.text((x0 + 16, y0 + 50 + j * 24), line, font=font(13), fill=SLATE)

    save(im, "web_ui_mockup.png")


# ── 6. Automation stack ──────────────────────────────────────────────────────
def diagram_automation_stack():
    im, d = new_img(1200, 800)
    title(d, "Automation stack (max hands-off)")

    layers = [
        (L0 := "L0 Hardware safeties", "Thermal fuse · mains fuse · chassis earth · SSR off when unpowered", RED_L, RED),
        ("L1 Firmware interlocks", "Sensor valid · door closed · T_max · duty cap · 2 s heater heartbeat", AMBER_L, AMBER),
        ("L2 Climate loops", "Temp PID · RH-aware fan curve · ramp limits", BLUE_L, BLUE),
        ("L3 Session automation", "Profiles · PREHEAT→RUN→FINISH→COOL→DONE · auto-end", GREEN_L, GREEN),
        ("L4 UX intelligence", "Live stats · warnings · recommendations · one-tap Apply", PURPLE_L, PURPLE),
    ]
    y = 120
    for head, body, fill, out in layers:
        rounded_box(d, (100, y, 1100, y + 100), fill, out, 3, 14)
        d.text((130, y + 22), head, font=font(20, True), fill=out)
        d.text((130, y + 58), body, font=font(15), fill=INK)
        y += 120

    d.text((100, 740), "User target: select profile → Start. Everything else is automated unless a CRITICAL needs human ack.", font=font(15), fill=MUTED)
    save(im, "automation_stack.png")


# ── 7. Pin map visual ────────────────────────────────────────────────────────
def diagram_pin_map():
    im, d = new_img(1100, 900)
    title(d, "ESP32 suggested pin map")

    # Board outline
    rounded_box(d, (350, 120, 750, 820), (30, 41, 59), SLATE, 4, 16)
    center_text(d, (550, 160), "ESP32 DevKitC", font(18, True), WHITE)
    center_text(d, (550, 195), "(adjust to your silk screen)", font(12), (148, 163, 184))

    left = [
        (25, "SSR heater"),
        (26, "Fan PWM"),
        (27, "Buzzer"),
        (14, "Status LED"),
        (4, "1-Wire DS18B20"),
    ]
    right = [
        (21, "I²C SDA"),
        (22, "I²C SCL"),
        (34, "Door input"),
        (35, "Current sense"),
        (0, "Boot / free"),
    ]

    for i, (gpio, lab) in enumerate(left):
        y = 260 + i * 90
        rounded_box(d, (80, y, 320, y + 60), BLUE_L, BLUE, 2, 10)
        d.text((100, y + 10), f"GPIO {gpio}", font=mono(14), fill=BLUE)
        d.text((100, y + 32), lab, font=font(14, True), fill=INK)
        arrow(d, (320, y + 30), (350, y + 30), BLUE, 2)

    for i, (gpio, lab) in enumerate(right):
        y = 260 + i * 90
        rounded_box(d, (780, y, 1020, y + 60), GREEN_L, GREEN, 2, 10)
        d.text((800, y + 10), f"GPIO {gpio}", font=mono(14), fill=GREEN)
        d.text((800, y + 32), lab, font=font(14, True), fill=INK)
        arrow(d, (750, y + 30), (780, y + 30), GREEN, 2)

    d.text((80, 820), "Avoid strapping pins for critical outputs when possible. Door on 34 needs external pull-up.", font=font(14), fill=MUTED)
    save(im, "pin_map.png")


def main():
    diagram_architecture()
    diagram_airflow()
    diagram_electrical()
    diagram_state_machine()
    diagram_web_ui()
    diagram_automation_stack()
    diagram_pin_map()
    print("done")


if __name__ == "__main__":
    main()
