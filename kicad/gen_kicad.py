#!/usr/bin/env python3
"""Generate KiCad footprints and symbols for carrier boards that host
(1) the WeAct Studio RP2350B Core Board and (2) the Raspberry Pi Pico 2.

Written by Claude at Bob's direction.

Files are written in KiCad 7 format so they open in KiCad 7 and later.
Footprints are top views of the carrier board: the module sits on top of the
carrier, component side up, with its header pins going down into these holes.
"""
import os, sys, uuid

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
PRETTY = os.path.join(OUT, "MCU_Module_Boards.pretty")
os.makedirs(PRETTY, exist_ok=True)

DRILL, PAD = 1.0, 1.7          # standard 0.1" header pin hole / pad
P = 2.54

def u(): return str(uuid.uuid4())

def fmt(v): return f"{v:.4f}".rstrip("0").rstrip(".") if v != 0 else "0"

# ------------------------------------------------------------------ footprints
def footprint(name, descr, tags, pads, outline, courtyard, extra_fab, ref_xy, val_xy,
              pin1_mark, silk_extra=()):
    L = [f'(footprint "{name}" (version 20221018) (generator pcbnew)',
         '  (layer "F.Cu")',
         f'  (descr "{descr}")',
         f'  (tags "{tags}")',
         '  (attr through_hole)',
         f'  (fp_text reference "REF**" (at {fmt(ref_xy[0])} {fmt(ref_xy[1])}) (layer "F.SilkS")'
         f' (effects (font (size 1 1) (thickness 0.15))) (tstamp {u()}))',
         f'  (fp_text value "{name}" (at {fmt(val_xy[0])} {fmt(val_xy[1])}) (layer "F.Fab")'
         f' (effects (font (size 1 1) (thickness 0.15))) (tstamp {u()}))',
         f'  (fp_text user "${{REFERENCE}}" (at {fmt(val_xy[0])} {fmt(val_xy[1] - 2)}) (layer "F.Fab")'
         f' (effects (font (size 1 1) (thickness 0.15))) (tstamp {u()}))']
    def rect(layer, x0, y0, x1, y1, w):
        L.append(f'  (fp_rect (start {fmt(x0)} {fmt(y0)}) (end {fmt(x1)} {fmt(y1)})'
                 f' (stroke (width {w}) (type solid)) (fill none) (layer "{layer}") (tstamp {u()}))')
    def line(layer, a, b, w):
        L.append(f'  (fp_line (start {fmt(a[0])} {fmt(a[1])}) (end {fmt(b[0])} {fmt(b[1])})'
                 f' (stroke (width {w}) (type solid)) (layer "{layer}") (tstamp {u()}))')
    def circle(layer, c, r, w):
        L.append(f'  (fp_circle (center {fmt(c[0])} {fmt(c[1])}) (end {fmt(c[0] + r)} {fmt(c[1])})'
                 f' (stroke (width {w}) (type solid)) (fill none) (layer "{layer}") (tstamp {u()}))')
    x0, y0, x1, y1 = outline
    rect("F.Fab", x0, y0, x1, y1, 0.1)
    rect("F.SilkS", x0 - 0.11, y0 - 0.11, x1 + 0.11, y1 + 0.11, 0.12)
    cx0, cy0, cx1, cy1 = courtyard
    rect("F.CrtYd", cx0, cy0, cx1, cy1, 0.05)
    for kind, *args in extra_fab:
        if kind == "rect": rect("F.Fab", *args, 0.1)
        if kind == "circle": circle("F.Fab", *args, 0.1)
        if kind == "text":
            t, x, y = args
            L.append(f'  (fp_text user "{t}" (at {fmt(x)} {fmt(y)}) (layer "F.Fab")'
                     f' (effects (font (size 0.8 0.8) (thickness 0.12))) (tstamp {u()}))')
    for a, b in pin1_mark: line("F.SilkS", a, b, 0.12)
    for a, b in silk_extra: line("F.SilkS", a, b, 0.12)
    for num, x, y in pads:
        shape = "rect" if num == "1" else "oval"
        L.append(f'  (pad "{num}" thru_hole {shape} (at {fmt(x)} {fmt(y)}) (size {PAD} {PAD})'
                 f' (drill {DRILL}) (layers "*.Cu" "*.Mask") (tstamp {u()}))')
    L.append(")")
    with open(os.path.join(PRETTY, name + ".kicad_mod"), "w") as f:
        f.write("\n".join(L) + "\n")

# ------------------------------------------------- WeAct RP2350B Core Board
# Board coordinates from HDK/3D_RP350B.step (WeActStudio/WeActStudio.RP2350BCoreBoard),
# converted to KiCad (y down). Footprint origin = pad 1.
# Pin names from HDK/RP2350B_PINOUT.png (silkscreen photo is in the same
# orientation as the STEP model: USB-C on the left edge).
# Names per hole, from the pinout chart, checked against HDK/RP2350B_SCH.pdf.
# Row lists run from the USB end (x = 1.778) to the far end (x = 37.338).
ADC = {40 + i: f"GP{40 + i}_ADC{i}" for i in range(8)}
def gp(n): return ADC.get(n, f"GP{n}")
W_OUT_A = ["GND", "GND", "3V3", "RUN"] + [gp(n) for n in range(46, 25, -2)]       # y=1.524, outer
W_IN_A  = ["GND", "3V3_EN", "3V3"] + [gp(n) for n in range(47, 24, -2)]           # y=4.064, inner
W_OUT_B = ["VBUS", "GND", "VREF"] + [gp(n) for n in range(1, 24, 2)]              # y=39.624, outer
W_IN_B  = ["5V", "GND"] + [gp(n) for n in range(0, 25, 2)]                        # y=37.084, inner
for L_ in (W_OUT_A, W_IN_A, W_OUT_B, W_IN_B): assert len(L_) == 15, L_

X0, YA_O, YA_I, YB_I, YB_O = 1.778, 1.524, 4.064, 37.084, 39.624
# Pad numbers follow WeAct's schematic: H1 -> 1..30 (odd = outer row),
# H2 -> 31..60 (H2 pin n = pad 30+n; odd = inner row), H4 -> 61..64 (3V3, SWDIO, SWCLK, GND).
weact = []  # (pad number, name, board x, board y)
for k in range(15):
    x = X0 + k * P
    weact.append((2*k + 1, W_OUT_B[k], x, YB_O))
    weact.append((2*k + 2, W_IN_B[k],  x, YB_I))
for k in range(15):
    x = X0 + k * P
    weact.append((31 + 2*k, W_IN_A[k],  x, YA_I))
    weact.append((32 + 2*k, W_OUT_A[k], x, YA_O))
for j, nm in enumerate(["3V3", "SWDIO", "SWCLK", "GND"]):
    weact.append((61 + j, nm, 31.09, 32.465 - j * P))
weact.sort()

ox, oy = X0, YB_O          # origin at pad 1 (H1 pin 1, VBUS)
BX0, BY0, BX1, BY1 = 0.013, 0.013, 41.389, 41.135
def wo(x, y): return (x - ox, y - oy)
pads = [(str(n), *wo(x, y)) for n, _, x, y in weact]
b0, b1 = wo(BX0, BY0), wo(BX1, BY1)
fab = [("rect", *wo(0.15, 16.04), *wo(7.90, 24.98)),          # USB-C body (from STEP)
       ("text", "USB-C", *wo(4.0, 20.5))]
for mx, my in [(1.143, 1.143), (40.259, 1.143), (1.143, 40.005), (40.259, 40.005)]:
    fab.append(("circle", wo(mx, my), 1.13))                   # 2.26 mm mounting holes, Fab only
p1 = wo(X0, YB_O)
footprint("WeAct_RP2350B_CoreBoard_THT",
          "WeAct Studio RP2350B Core Board (64 THT pins: H1 2x15, H2 2x15, H4 1x4 SWD; pads 1-30 = H1, 31-60 = H2, 61-64 = H4), carrier-board footprint, "
          "module component side up. Geometry from HDK/3D_RP350B.step, "
          "https://github.com/WeActStudio/WeActStudio.RP2350BCoreBoard",
          "RP2350B WeAct core board module",
          pads, (*b0, *b1), (b0[0] - 0.25, b0[1] - 0.25, b1[0] + 0.25, b1[1] + 0.25), fab,
          ref_xy=wo(20.7, 42.8), val_xy=wo(20.7, 20.6),
          pin1_mark=[((b0[0] - 0.6, p1[1] - 1.3), (b0[0] - 0.6, p1[1] + 1.3))])

# ----------------------------------------------------------- Raspberry Pi Pico 2
# Raspberry Pi Pico 2 datasheet (RP-008299-DS-3), Figure 3 and Figure 2.
# Board 21 x 51, USB end at the top; pin 1 at top left, 1-20 down the left,
# 21-40 up the right. Debug: SWCLK, GND, SWDIO left to right, 1.6 mm from the bottom edge.
PICO = ["GP0", "GP1", "GND", "GP2", "GP3", "GP4", "GP5", "GND", "GP6", "GP7",
        "GP8", "GP9", "GND", "GP10", "GP11", "GP12", "GP13", "GND", "GP14", "GP15",
        "GP16", "GP17", "GND", "GP18", "GP19", "GP20", "GP21", "GND", "GP22", "RUN",
        "GP26_ADC0", "GP27_ADC1", "AGND", "GP28_ADC2", "ADC_VREF", "3V3_OUT", "3V3_EN", "GND", "VSYS", "VBUS"]
PY0 = (51 - 19 * P) / 2
pico = []
for i in range(20): pico.append((i + 1, PICO[i], 1.61, PY0 + i * P))
for i in range(20): pico.append((21 + i, PICO[20 + i], 19.39, PY0 + (19 - i) * P))
for j, nm in enumerate(["SWCLK", "GND", "SWDIO"]): pico.append((41 + j, nm, 10.5 + (j - 1) * P, 51 - 1.6))
ox, oy = 1.61, PY0
def po(x, y): return (x - ox, y - oy)
pads = [(str(n), *po(x, y)) for n, _, x, y in pico]
b0, b1 = po(0, 0), po(21, 51)
fab = [("rect", *po(6.5, -1.3), *po(14.5, 4.3)), ("text", "USB", *po(10.5, 1.5))]
for mx in (4.8, 16.2):
    for my in (2.0, 49.0): fab.append(("circle", po(mx, my), 1.05))
p1 = po(1.61, PY0)
footprint("RaspberryPi_Pico2_THT",
          "Raspberry Pi Pico 2 (RP2350A), 40 THT pins + 3-pin SWD debug, carrier-board footprint, "
          "module component side up. Geometry from the Raspberry Pi Pico 2 datasheet RP-008299-DS-3, Figure 3",
          "RP2350A Raspberry Pi Pico 2 module",
          pads, (*b0, *b1), (b0[0] - 0.25, b0[1] - 1.3 - 0.25, b1[0] + 0.25, b1[1] + 0.25), fab,
          ref_xy=po(10.5, 52.5), val_xy=po(10.5, 25.5),
          pin1_mark=[((p1[0] - 1.3, b0[1] - 0.6), (p1[0] + 1.3, b0[1] - 0.6))])

# ------------------------------------------------------------------- symbols
def etype(n):
    if n in ("GND", "AGND"): return "power_in"
    if n in ("VBUS", "VSYS", "5V"): return "power_in"
    if n in ("3V3", "3V3_OUT"): return "power_out"
    if n in ("RUN", "3V3_EN", "SWCLK"): return "input"
    if n in ("VREF", "ADC_VREF"): return "passive"
    return "bidirectional"

def symbol(name, fp, descr, kw, pins, left, right, top, bottom, width=25.4):
    """pins: list of (number, name); left/right/top/bottom: lists of pin numbers."""
    names = dict(pins)
    n_side = max(len(left), len(right))
    h = (n_side + 1) * P
    hw = width / 2
    top_y = (n_side - 1) * P / 2
    S = [f'  (symbol "{name}" (in_bom yes) (on_board yes)',
         f'    (property "Reference" "U" (at {fmt(-hw)} {fmt(top_y + 2*P + 1.5)} 0) (effects (font (size 1.27 1.27)) (justify left)))',
         f'    (property "Value" "{name}" (at {fmt(-hw)} {fmt(-top_y - 2*P - 1.5)} 0) (effects (font (size 1.27 1.27)) (justify left)))',
         f'    (property "Footprint" "MCU_Module_Boards:{fp}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
         f'    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
         f'    (property "ki_keywords" "{kw}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
         f'    (property "ki_description" "{descr}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
         f'    (symbol "{name}_0_1"',
         f'      (rectangle (start {fmt(-hw)} {fmt(top_y + P)}) (end {fmt(hw)} {fmt(-top_y - P)})'
         f' (stroke (width 0.254) (type default)) (fill (type background)))',
         '    )',
         f'    (symbol "{name}_1_1"']
    def pin(num, x, y, ang):
        nm = names[num]
        # same-name power pins after the first are stacked and hidden? Keep all visible: clearer for a module.
        S.append(f'      (pin {etype(nm)} line (at {fmt(x)} {fmt(y)} {ang}) (length 2.54)'
                 f' (name "{nm}" (effects (font (size 1.016 1.016))))'
                 f' (number "{num}" (effects (font (size 1.016 1.016)))))')
    for i, n in enumerate(left):
        if n is not None: pin(n, -hw - 2.54, top_y - i * P, 0)
    for i, n in enumerate(right):
        if n is not None: pin(n, hw + 2.54, top_y - i * P, 180)
    for i, n in enumerate(top):
        pin(n, (i - (len(top) - 1) / 2) * P, top_y + P + 2.54, 270)
    for i, n in enumerate(bottom):
        pin(n, (i - (len(bottom) - 1) / 2) * P, -top_y - P - 2.54, 90)
    S += ['    )', '  )']
    return "\n".join(S)

# Pico 2: physical layout (pin 1 top left, like the board seen from above), debug on the bottom.
pico_pins = [(str(n), nm) for n, nm, _, _ in pico]
sym_pico = symbol("RaspberryPi_Pico2", "RaspberryPi_Pico2_THT",
                  "Raspberry Pi Pico 2 (RP2350A) module, 40 pins + SWD debug",
                  "RP2350 RP2350A Pico2 Raspberry Pi module",
                  pico_pins,
                  left=[str(i) for i in range(1, 21)],
                  right=[str(i) for i in range(40, 20, -1)],
                  top=[], bottom=["41", "42", "43"], width=22.86)

# WeAct: left = H1 (pads 1-30), right = H2 (pads 31-60), top = H4 SWD (61-64).
weact_pins = [(str(n), nm) for n, nm, _, _ in weact]
sym_weact = symbol("WeAct_RP2350B_CoreBoard", "WeAct_RP2350B_CoreBoard_THT",
                   "WeAct Studio RP2350B Core Board, 64 pins: H1 = pins 1-30, H2 = pins 31-60 (H2 pin n = 30+n), H4 SWD = 61-64",
                   "RP2350 RP2350B WeAct core board module",
                   weact_pins,
                   left=[str(i) for i in range(1, 31)],
                   right=[str(i) for i in range(31, 61)],
                   top=["61", "62", "63", "64"], bottom=[], width=22.86)

with open(os.path.join(OUT, "MCU_Module_Boards.kicad_sym"), "w") as f:
    f.write('(kicad_symbol_lib (version 20220914) (generator kicad_symbol_editor)\n'
            + sym_weact + "\n" + sym_pico + "\n)\n")

# pin tables for the READMEs
with open(os.path.join(OUT, "pin_tables.md"), "w") as f:
    for title, rows in (("WeAct RP2350B Core Board", weact), ("Raspberry Pi Pico 2", pico)):
        f.write(f"### {title}\n\n| Pad | Signal | Pad | Signal |\n|---|---|---|---|\n")
        half = (len(rows) + 1) // 2
        for i in range(half):
            a = rows[i]; b = rows[i + half] if i + half < len(rows) else None
            f.write(f"| {a[0]} | {a[1]} | " + (f"{b[0]} | {b[1]} |" if b else " | |") + "\n")
        f.write("\n")
print("ok", len(weact), len(pico))
