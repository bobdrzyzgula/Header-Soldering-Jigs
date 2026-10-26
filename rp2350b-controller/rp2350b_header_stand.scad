// Header soldering stand for the RP2350B board in 3D_RP350B.step
// Written by Claude at Bob's direction.
//
// How it is used:
//   1. Drop the generic male headers into the stand, LONG pins down, so the
//      plastic bodies sit flat on the stand's top face.
//   2. Lay the board over the short pins and solder.
//   The holes hold every pin parallel; the board rests only on the header
//   bodies, so it ends up square to the pins.
//
// body_side = "bottom": header plastic under the board (the usual Pico-style
//                       mounting). Board goes on component side UP. Flat top.
// body_side = "top":    header plastic on the component side. Board goes on
//                       component side DOWN, so the pattern is mirrored and the
//                       top face is pocketed to clear the mounted parts.
//
// Print top face up (holes vertical). No supports needed.

/* [Main] */
body_side      = "bottom";   // [bottom, top]
hole_d         = 1.0;        // pin hole diameter (square 0.64 pin diagonal = 0.9)
stand_h        = 8.0;        // stand thickness = hole depth (holes go through)
margin         = 4.0;        // stand extends this far past the board outline
corner_r       = 2.0;

/* [Hole entry] */
countersink    = 0.4;        // chamfer depth at the top of each hole (eases insertion)
bottom_chamfer = 0.3;        // relieves elephant's-foot shrink of the holes

/* [Component pockets: body_side = "top" only] */
header_body_h  = 2.5;        // height of the header's plastic body
pocket_xy_clr  = 0.75;       // clearance around each component outline
pocket_extra_z = 1.0;        // extra depth beyond what the tallest part needs
pocket_min     = 1.0;        // never cut shallower than this
merge_gap      = 2.5;        // pockets closer than ~2x this are merged (no slivers)
keepout        = 0.75;       // solid margin kept around each header body footprint
header_body_w  = 2.54;       // footprint kept solid under each header body

/* [Markings] */
engrave_depth  = 0.5;
show_board     = false;      // preview the board/components ghost (not for export)

include <rp2350b_data.scad>

$fn = 24;

top = body_side == "top";
// Flip the board over its X axis when the plastic goes on the component side.
function fp(p) = top ? [p[0], 2*BOARD_YC - p[1]] : p;
function fpts(L) = [for (p = L) fp(p)];

pins = concat(OUTER_PINS, MID_PINS);
tallest = max([for (c = COMPONENTS) c[1]]);
pocket_depth = max(pocket_min, tallest - header_body_h + pocket_extra_z);

s0 = [BOARD_MIN[0] - margin, BOARD_MIN[1] - margin];
s1 = [BOARD_MAX[0] + margin, BOARD_MAX[1] + margin];

module rounded_rect(a, b, r) {
    translate([a[0] + r, a[1] + r]) offset(r = r)
        square([b[0] - a[0] - 2*r, b[1] - a[1] - 2*r]);
}

module header_bodies_2d() {
    for (p = fpts(pins)) translate(p) square(header_body_w, center = true);
}

module pockets_2d() {
    difference() {
        // closing operation: grow, merge, shrink back
        offset(delta = -merge_gap) offset(delta = merge_gap)
            for (c = COMPONENTS) offset(delta = pocket_xy_clr) polygon(fpts(c[2]));
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

module stand() {
    difference() {
        linear_extrude(stand_h) rounded_rect(s0, s1, corner_r);

        for (p = fpts(pins)) translate(p) pin_hole();

        if (top)
            translate([0, 0, stand_h - pocket_depth])
                linear_extrude(pocket_depth + 1) pockets_2d();

        // board outline, engraved so you can see which way the board goes
        translate([0, 0, stand_h - engrave_depth])
            linear_extrude(engrave_depth + 1) difference() {
                offset(delta = 0.6) rounded_rect(BOARD_MIN, BOARD_MAX, 0.01);
                offset(delta = 0.2) rounded_rect(BOARD_MIN, BOARD_MAX, 0.01);
            }

        // "USB" marker in the margin at the USB-C end (left edge in both variants)
        translate([s0[0] + margin/2 + 0.6, BOARD_YC, stand_h - engrave_depth])
            linear_extrude(engrave_depth + 1)
                rotate(90) text("USB", size = 2.2, halign = "center", valign = "center",
                                font = "Liberation Sans:style=Bold");

        // variant label on the front face
        translate([(s0[0] + s1[0])/2, s0[1] + engrave_depth, stand_h/2])
            rotate([90, 0, 0]) linear_extrude(engrave_depth + 1)
                text(top ? "BODY TOP / PARTS DOWN" : "BODY BOTTOM / PARTS UP",
                     size = 2.6, halign = "center", valign = "center",
                     font = "Liberation Sans:style=Bold");
    }
}

module board_ghost() {
    z0 = stand_h + header_body_h;           // board's facing surface
    color("green", 0.5) translate([0, 0, z0])
        linear_extrude(1.6) rounded_rect(BOARD_MIN, BOARD_MAX, 0.01);
    for (c = COMPONENTS)
        color("gray", 0.7)
            if (top) translate([0, 0, z0 - c[1]]) linear_extrude(c[1]) polygon(fpts(c[2]));
            else     translate([0, 0, z0 + 1.6]) linear_extrude(c[1]) polygon(c[2]);
    for (p = fpts(pins)) color("black") translate(concat(p, stand_h))
        translate([-header_body_w/2, -header_body_w/2, 0]) cube([header_body_w, header_body_w, header_body_h]);
}

stand();
if (show_board) %board_ghost();
