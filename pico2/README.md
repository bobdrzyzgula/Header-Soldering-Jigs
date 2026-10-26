# Header soldering stand for the Raspberry Pi Pico 2

*Written by Claude at Bob's direction.*

This is a 3D-printed jig that holds generic 0.1" male headers vertical and parallel while you solder them to a Raspberry Pi Pico 2 (RP2350A). It works the same way as the RP2350B controller-board stand.

## Files

| File | What it is |
|---|---|
| `pico2_header_stand.scad` | OpenSCAD model. It contains everything and needs no data file. |
| `pico2_stand_body_bottom.stl` | Stand for mounting the header plastic **under** the board (normal Pico mounting) |
| `pico2_stand_body_top.stl` | Stand for mounting the header plastic **on the component side** |

## Geometry source

The dimensions come from Figure 3 of the *Raspberry Pi Pico 2 Datasheet* (RP-008299-DS-3):

- The board is 51 × 21 mm and 1 mm thick. It's single-sided: all parts are on the top, and the bottom has only test pads.
- **Main headers:**
  - 2 × 20 pins at 2.54 mm pitch, with 1 mm holes
  - the two rows are 17.78 mm apart, with each row 1.61 mm in from a long edge
  - the end pins are 1.37 mm in from the short edges, i.e. (51 − 48.26)/2
- **Debug (SWD) header:**
  - 3 pins centered on the lower edge, 1.6 mm in from that edge, at 2.54 mm pitch
  - the center pin is 5.7 mm from the mounting hole at 4.8 mm, so it sits at x = 10.5 mm, the board's centerline
- **Mounting holes:** four 2.1 mm holes, 4.8 mm in from the long edges and 2 mm in from the ends. The stand doesn't use them.
- **USB:** the micro-USB connector is 8 mm wide and overhangs the top edge by 1.3 mm.

The Pico 2 has no STEP file in this set. The datasheet gives no part outlines or heights, so instead of matching individual parts, the component-side version clears the whole area between the pin rows.

## Stand design

- **Holes:**
  - through holes drawn at 1.3 mm, in an 8 mm block
  - a 0.4 mm chamfer at the top of each hole and a 0.3 mm chamfer at the bottom
- **Size:** the stand extends 4 mm past the board on three sides and 6.5 mm at the USB end, which makes room for the USB cutout and the "USB" mark.
- **Markings:** the board outline is engraved on top, and the variant name is engraved on the left long face.
- **Mirroring:** the Pico's hole pattern is symmetric about its long axis. Flipping the board component side down therefore moves no holes, and the two versions differ only in the pocket.
- **Component-side version (`body_side = "top"`):**
  - Everything between the two pin rows is pocketed 2.5 mm deep. With the 2.5 mm header bodies, that leaves 5 mm under the board for the parts.
  - The pocket runs past the top edge of the board to clear the overhanging micro-USB connector.
  - At least 0.75 mm of solid surface is kept around every header body, including the debug header.
- **No debug header:** set `include_debug = false` to drop its holes.

## Printing

- Print with the top face up. No supports are needed.
- Holes are drawn at 1.3 mm. FDM printing makes holes smaller than drawn, and the Pico 2 stand printed at 1.0 mm needed its holes opened to 1.3 mm, after which it worked well. If your printer's holes come out tight or loose, adjust `hole_d` in the Customizer (0.05 mm steps).
- Every numeric parameter has a range and step set, so the OpenSCAD Customizer keeps decimal values instead of rounding them to whole numbers.

## Using the stand

1. Cut header strips to 1×20, 1×20 and 1×3 (debug). Push them into the stand, **long pins down**, until the plastic bodies sit flat.
2. Lay the Pico 2 on the short pins with the USB end toward the "USB" mark. In the bottom version, components face up. In the top version, they face down into the pocket.
3. Tack one end pin of each row and check that the board sits flat on all the header bodies. If it doesn't, reheat a tack and press the board down. Then tack the other ends, and finally solder the rest.
4. Keep each joint short, about 2 seconds, and skip around the board rather than going down a row in order, so the header plastic doesn't soften.
5. Lift the board straight up off the stand.

**Note on the debug header:** it sits only 1.6 mm from the board edge, and a 1×3 header body extends about 0.3 mm past that edge. The stand allows for this.

## Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `body_side` | `"bottom"` | `"bottom"` or `"top"`: which side of the board the header plastic goes on |
| `include_debug` | true | Include holes for the 3-pin debug header |
| `hole_d` | 1.3 | Pin hole diameter as drawn |
| `stand_h` | 8.0 | Stand thickness, which is also the hole depth |
| `margin` / `usb_margin` | 4.0 / 6.5 | How far the stand extends past the board / at the USB end |
| `pocket_depth` | 2.5 | Pocket depth in the component-side version |
| `keepout` | 0.75 | Solid margin kept around each header body |
| `usb_overhang` / `usb_w` / `usb_clr` | 1.3 / 8.0 / 1.0 | USB connector overhang, width, and the clearance cut around it |
| `show_board` | false | Shows a ghost of the board and header bodies in preview |

To export from the command line:

```sh
openscad -D 'body_side="bottom"' -o pico2_stand_body_bottom.stl pico2_header_stand.scad
openscad -D 'body_side="top"'    -o pico2_stand_body_top.stl    pico2_header_stand.scad
```
