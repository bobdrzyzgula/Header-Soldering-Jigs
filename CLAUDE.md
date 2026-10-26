# Instructions for Claude: adding a board to this repo

Written by Claude at Bob's direction. Bob asked that every new board get **both** of the following.

1. **A soldering stand** in its own folder `<board-name>/`. It needs:
   - an OpenSCAD model with a `body_side` parameter (`"bottom"` / `"top"`)
   - STLs for both versions
   - a README in the style of `rp2350b-controller/README.md` and `pico2/README.md`
   - a new row in the board table in the top-level `README.md`

   Defaults:
   - 1.0 mm through holes, 8 mm deep, with a 0.4 mm chamfer at the top and 0.3 mm at the bottom
   - a 4 mm margin around the board
   - an engraved board outline, a USB marker, and the variant name on a side face
   - for the component-side (`"top"`) version, pockets that clear the parts, with at least 0.75 mm of solid surface kept around every header body
2. **A KiCad footprint and symbol**, added to the `MCU_Module_Boards` library by extending `kicad/gen_kicad.py`. Regenerate the library and add the pin table to `kicad/README.md`. The defaults:
   - **Footprint:** a carrier-board footprint, module component side up, with pad 1 as the origin. Pads are 1.0 mm drill and 1.7 mm across. The board outline, USB connector and mounting holes go on F.Fab, and the courtyard is the outline plus 0.25 mm, including any USB overhang.
   - **Format:** KiCad 7. Validate with `kicad-cli fp upgrade` / `sym upgrade` (they should report "not updated") and by plotting to SVG.
   - **Pin numbering:** use the manufacturer's own numbering and signal names (from its schematic or datasheet) wherever they exist.

## What's needed, and when to ask

| Needed for | Sources, best first |
|---|---|
| Hole positions and board outline | Manufacturer STEP file, then a dimension drawing or datasheet figure, then a KiCad/EasyEDA footprint |
| Part outlines and heights (component-side pocket) | STEP file. Without one, pocket the whole area between the header rows to a generous depth, and say so in the README. |
| Signal name and number for every pin | Manufacturer schematic, then a pinout chart, then silkscreen photos. Cross-check two sources where possible. |

- **Missing information:** if the hole positions or the pin assignments can't be established from the material available, tell Bob what is missing before building, rather than guessing. The stand needs only the hole positions; the KiCad symbol also needs every pin's signal.
- **Conflicting sources:** if two sources disagree (as the WeAct pinout chart's numbering did against its schematic), follow the schematic and note the difference in the README.
- **Citing sources:** record the source file and commit, or the document and figure, in each README and in the file headers.
- **Large source files:** don't commit large manufacturer files such as STEP models. Link to them instead.

## Commits

- Commit and push to `main` (Bob asked for this repo to be updated directly).
- Writing here is credited to Claude at Bob's direction, never to Bob as author.
