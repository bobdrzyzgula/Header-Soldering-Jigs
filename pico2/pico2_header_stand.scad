// Header soldering stand for the Raspberry Pi Pico 2 (RP2350A)
// Written by Claude at Bob's direction.
//
// Geometry from the Raspberry Pi Pico 2 datasheet (RP-008299-DS-3),
// Figure 3, "The dimensions of the Raspberry Pi Pico 2 board":
//   board 51 x 21 mm, 1 mm thick, single sided (all parts on top)
//   2 x 20 pins, 2.54 mm pitch, rows 17.78 mm apart, 1.61 mm in from the
//   long edges, end pins 1.37 mm in from the short edges (51 - 48.26)/2, 1 mm holes
//   3-pin debug (SWD) header on the lower edge, centred, 1.6 mm in from the edge
//     (centre pin is 5.7 mm from the mounting-hole centre at 4.8 mm -> x = 10.5)
//   4 x 2.1 mm mounting holes, 4.8 mm from the long edges (11.4 apart), 2 mm from the ends
//   micro-USB overhangs the top edge by 1.3 mm
//
// Coordinates: x across the board (0..21), y down the board from the USB end (0..51).
//
// How it is used:
//   1. Drop generic male headers into the stand, LONG pins down, so the
//      plastic bodies sit flat on the stand's top face.
//   2. Lay the Pico 2 over the short pins and solder.
//
// body_side = "bottom": header plastic under the board (normal Pico mounting).
//                       Board goes component side UP. Flat top.
// body_side = "top":    header plastic on the component side. Board goes
//                       component side DOWN, so the centre of the stand is
//                       pocketed to clear the parts and the overhanging USB.
// The Pico's hole pattern is symmetric about its long axis, so flipping the board
// does not move any holes; the two variants differ only in the pocket.
//
// Print top face up (holes vertical). No supports needed.

/* [Main] */
// Which side of the board the header plastic goes on
body_side      = "bottom"; // [bottom, top]
// Holes for the 3-pin debug header
include_debug  = true;
// Pin hole diameter as drawn; printed holes come out smaller (1.3 tested on a Pico 2 print)
hole_d         = 1.3; // [0.8:0.05:1.6]
// Stand thickness = hole depth (holes go through)
stand_h        = 8.0; // [4:0.5:15]
// Stand extends this far past the board outline
margin         = 4.0; // [2:0.5:10]
// Extra room at the USB end for the USB pocket and marker
usb_margin     = 6.5; // [4:0.5:12]
// Corner radius of the stand
corner_r       = 2.0; // [0:0.5:5]

/* [Hole entry] */
// Chamfer depth at the top of each hole
countersink    = 0.4; // [0:0.05:1]
// Relieves elephant's-foot shrink of the holes
bottom_chamfer = 0.3; // [0:0.05:1]

/* [Component pocket: body_side = "top" only] */
// Height of the header's plastic body (for reference)
header_body_h  = 2.5; // [2:0.05:3.5]
// Gives header_body_h + pocket_depth = 5 mm under the board
pocket_depth   = 2.5; // [0:0.1:5]
// Solid margin kept around each header body footprint
keepout        = 0.75; // [0:0.05:2]
// Footprint kept solid under each header body
header_body_w  = 2.54; // [2.3:0.02:2.8]
// Datasheet: micro-USB overhangs the top edge 1.3 mm (typ)
usb_overhang   = 1.3; // [0:0.1:3]
// Datasheet: 8 mm
usb_w          = 8.0; // [5:0.1:12]
// Clearance around the USB overhang
usb_clr        = 1.0; // [0:0.1:3]

/* [Markings] */
// Depth of the engraved outline and labels
engrave_depth  = 0.5; // [0:0.1:1.5]
// Preview ghost of the board and header bodies
show_board     = false;

/* [Hidden] */
$fn = 24;
BW = 21; BL = 51;
PITCH = 2.54;
ROW_X = [1.61, BW - 1.61];
PIN_Y0 = (BL - 19*PITCH) / 2;            // 1.37
MAIN_PINS = [for (x = ROW_X) for (i = [0:19]) [x, PIN_Y0 + i*PITCH]];
DEBUG_PINS = [for (i = [-1:1]) [BW/2 + i*PITCH, BL - 1.6]];
MOUNT_HOLES = [for (x = [4.8, BW - 4.8]) for (y = [2, BL - 2]) [x, y]];
pins = include_debug ? concat(MAIN_PINS, DEBUG_PINS) : MAIN_PINS;
top = body_side == "top";

module rrect(x0, y0, x1, y1, r) {
    translate([x0 + r, y0 + r]) offset(r = r) square([x1 - x0 - 2*r, y1 - y0 - 2*r]);
}

module header_bodies_2d() {
    for (p = pins) translate(p) square(header_body_w, center = true);
}

module pocket_2d() {
    difference() {
        union() {
            // everything between the two pin rows, full length of the board
            translate([ROW_X[0], -usb_overhang - usb_clr])
                square([ROW_X[1] - ROW_X[0], BL + usb_overhang + usb_clr]);
            // the micro-USB overhang past the top edge
            translate([BW/2 - usb_w/2 - usb_clr, -usb_overhang - usb_clr])
                square([usb_w + 2*usb_clr, usb_overhang + usb_clr + 1]);
        }
        offset(delta = keepout) header_bodies_2d();
    }
}

module pin_hole() {
    translate([0, 0, -1]) cylinder(d = hole_d, h = stand_h + 2);
    translate([0, 0, stand_h - countersink])
        cylinder(d1 = hole_d, d2 = hole_d + 2*countersink + 0.01, h = countersink + 0.01);
    translate([0, 0, -0.01])
        cylinder(d1 = hole_d + 2*bottom_chamfer, d2 = hole_d, h = bottom_chamfer + 0.01);
}

// Stand coordinates: y increases toward the USB end so the model reads naturally
// from above.
module board_frame() { translate([0, BL]) mirror([0, 1]) children(); }

module stand() {
    difference() {
        linear_extrude(stand_h) rrect(-margin, -margin, BW + margin, BL + usb_margin, corner_r);

        board_frame() {
            for (p = pins) translate(p) pin_hole();

            if (top)
                translate([0, 0, stand_h - pocket_depth])
                    linear_extrude(pocket_depth + 1) pocket_2d();

            // board outline, engraved
            translate([0, 0, stand_h - engrave_depth])
                linear_extrude(engrave_depth + 1) difference() {
                    offset(delta = 0.6) square([BW, BL]);
                    offset(delta = 0.2) square([BW, BL]);
                }
        }

        // "USB" marker in the margin at the USB end
        translate([BW/2, BL + usb_margin - 2.0, stand_h - engrave_depth])
            linear_extrude(engrave_depth + 1)
                text("USB", size = 2.2, halign = "center", valign = "center",
                     font = "Liberation Sans:style=Bold");

        // variant label on the long side face
        translate([-margin + engrave_depth, (BL + usb_margin - margin)/2, stand_h/2])
            rotate([90, 0, -90]) linear_extrude(engrave_depth + 1)
                text(top ? "PICO 2  BODY TOP / PARTS DOWN" : "PICO 2  BODY BOTTOM / PARTS UP",
                     size = 2.4, halign = "center", valign = "center",
                     font = "Liberation Sans:style=Bold");
    }
}

module board_ghost() {
    z0 = stand_h + header_body_h;
    board_frame() {
        color("green", 0.5) translate([0, 0, z0]) cube([BW, BL, 1]);
        color("gray", 0.7)                        // micro-USB, roughly
            translate([BW/2 - usb_w/2, -usb_overhang, top ? z0 - 2.9 : z0 + 1])
                cube([usb_w, 5.6, 2.9]);
        for (p = pins) color("black")
            translate([p[0] - header_body_w/2, p[1] - header_body_w/2, stand_h])
                cube([header_body_w, header_body_w, header_body_h]);
    }
}

stand();
if (show_board) %board_ghost();
