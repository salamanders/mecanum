include <Technic.scad>
include <BOSL2/std.scad>

plate_height = 2;
neck_height = 6;
conn_h = 20; // Extended height to reach across the 30-degree tilt

// Square of 4 screw holes, measuring from the edges of the holes.
screw_outer_dist_x = 15.5;
screw_inner_dist_x = 8.5;

screw_outer_dist_y = 13.5;
screw_inner_dist_y = 6.5;

screw_d = 3.5;

technic_pin_connector_outer_diameter = 7.36 + 1;
technic_pin_connector_shoulder_wall_thickness = 0.6 + 0.5;

//technic_pin_connector_outer_diameter = 9.36;
//technic_pin_connector_shoulder_wall_thickness = 1.6;

union() {
    // Yellow Technic Beam
    translate([4.5,0,0])
    translate([0, technic_height_in_mm/2, technic_beam_hole_spacing/2 + neck_height - 0.4])
    rotate([90,0,0])
    technic_beam(length = 3);

    // Connectors: Built on top of the rotated plate surface and trimmed flat at neck_height
    difference() {
        rotate([0,30,0]) {
            // Orange Connector
            color("orange")
            translate([screw_outer_dist_x/2, 0, 0.1 + conn_h/2])
            cuboid(
                [screw_inner_dist_x - 4, technic_height_in_mm, conn_h], 
                rounding = -2,
                edges = [BOT], 
                except = [LEFT, RIGHT],
                $fn = 36
            );

            // Purple Connectors
            p_adjust = -1.0;
            
            color("purple")
            translate([screw_outer_dist_x/2, 0, 0.1 + conn_h/2])
            cube([screw_outer_dist_x + p_adjust, screw_inner_dist_y - 4, conn_h], center = true);

            color("purple")
            translate([screw_outer_dist_x/2, 0, 0.1 + conn_h/2])
            cuboid(
                [screw_outer_dist_x + p_adjust, screw_inner_dist_y - 4, conn_h], 
                rounding = -3,
                edges = [BOT], 
                except = [FRONT, BACK],
                $fn = 36
            );
        }

        // Trim any connector material extending above the top neck line (Z >= neck_height)
        translate([0, 0, neck_height + 25])
        cube([100, 100, 50], center = true);
    }

    // Blue Plate
    rotate([0,30,0])
    translate([0, -screw_d - screw_inner_dist_y/2, -plate_height + 0.1])
    difference() {
        color("blue")
        translate([screw_outer_dist_x/2, screw_outer_dist_y/2, plate_height/2])
        cuboid(
            [screw_outer_dist_x + 2*screw_d, screw_outer_dist_y + 2*screw_d, plate_height], 
            rounding = 3, 
            except = [TOP, BOT]
        );

        translate([0, 0, -1]) {
            translate([screw_d/2, screw_d/2, 0])
            cylinder(h = 5, d = screw_d);

            translate([screw_d/2, screw_outer_dist_y - screw_d/2, 0])
            cylinder(h = 5, d = screw_d);

            translate([screw_outer_dist_x - screw_d/2, screw_d/2, 0])
            cylinder(h = 5, d = screw_d);

            translate([screw_outer_dist_x - screw_d/2, screw_outer_dist_y - screw_d/2, 0])
            cylinder(h = 5, d = screw_d);
        }
    }
}