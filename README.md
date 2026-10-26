# Header Soldering Jigs

*Written by Claude at Bob's direction.*

These are 3D-printable stands for soldering 0.1" pin headers onto microcontroller boards so the headers come out straight. Each board has its own folder with an OpenSCAD model, ready-to-print STLs and a README.

## How the stands work

- **The jig:** a block with a hole for every pin. The holes are 1.0 mm, through the full 8 mm thickness of the block, and chamfered at both ends.
- **Using it:**
  1. Put generic male headers in the holes, **long pins down**, so their plastic bodies sit flat on the top face.
  2. Lay the board on the short pins.
  3. Tack the corners, check that the board is flat, then solder the rest.
- **Why it works:** the depth of the holes keeps the pins parallel. The board rests only on the header bodies, which keeps it square to the pins.

Each board has two versions:

- **`body_bottom`:** the header plastic goes under the board, the normal mounting. The board goes in components up, and the top of the stand is flat.
- **`body_top`:** the header plastic goes on the component side. The board goes in components down, and the top of the stand is pocketed to clear the parts.

## Boards

| Folder | Board | Pins | Geometry source |
|---|---|---|---|
| [`rp2350b-controller/`](rp2350b-controller/) | WeAct Studio RP2350B Core Board, used in the sewing-machine motor controller | 2×15 + 2×15 + 1×4 | `HDK/3D_RP350B.step` from [WeAct's repository](https://github.com/WeActStudio/WeActStudio.RP2350BCoreBoard) |
| [`pico2/`](pico2/) | Raspberry Pi Pico 2 (RP2350A) | 2×20 + 3-pin debug | Raspberry Pi Pico 2 datasheet, Figure 3 |

## Printing

- Print with the top face up. No supports are needed.
- If pins bind in the holes, raise `hole_d` to 1.1 mm in the Customizer, or run a 1.0 mm drill through the holes.
