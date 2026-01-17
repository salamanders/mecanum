include <Technic.scad>

//translate([-technic_beam_hole_spacing,0,0])


// square of 4 screw holes, measuring from the edges of the holes.
screw_outer_dist_x = 15.5;
screw_inner_dist_x = 8.5;

screw_outer_dist_y = 13.5;
screw_inner_dist_y = 6.5;

screw_d = 3.5;

translate([0,technic_height_in_mm/2,technic_beam_hole_spacing/2])
rotate([90,0,0])
technic_beam( length = 3 );

color("green")
translate([screw_outer_dist_x/2, 0, -.1])
cube([screw_outer_dist_x,screw_inner_dist_y-1,2], center=true);

translate([0,-screw_d - screw_inner_dist_y/2, -1.5])
difference() {
    color("blue")
    translate([-screw_d,-screw_d,0])
    cube([screw_outer_dist_x + 2*screw_d, screw_outer_dist_y + 2*screw_d, 1]);

    translate([0,0,-1]) {
        translate([screw_d/2, screw_d/2, 0])
        cylinder(h=5, d=screw_d);

        translate([screw_d/2, screw_outer_dist_y - screw_d/2, 0])
        cylinder(h=5, d=screw_d);

        translate([screw_outer_dist_x - screw_d/2, screw_d/2, 0])
        cylinder(h=5, d=screw_d);

        translate([screw_outer_dist_x - screw_d/2, screw_outer_dist_y - screw_d/2, 0])
        cylinder(h=5, d=screw_d);
    }
}