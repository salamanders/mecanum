include <Technic.scad>
include <BOSL2/std.scad>

//translate([-technic_beam_hole_spacing,0,0])

plate_height = 2;
neck_height = 6;

// square of 4 screw holes, measuring from the edges of the holes.
screw_outer_dist_x = 15.5;
screw_inner_dist_x = 8.5;

screw_outer_dist_y = 13.5;
screw_inner_dist_y = 6.5;

screw_d = 3.5;


union() {
translate([0,technic_height_in_mm/2,technic_beam_hole_spacing/2+neck_height-.4])
rotate([90,0,0])
technic_beam( length = 3 );

/*
color("green")
translate([screw_outer_dist_x/2, 0, neck_height/2])
cube([screw_inner_dist_x-4,technic_height_in_mm,neck_height], center=true);
*/


color("orange")
translate([screw_outer_dist_x/2, 0, neck_height/2])
cuboid(
    [screw_inner_dist_x-4,technic_height_in_mm,neck_height], rounding=-2,
    edges=[BOT], except=[LEFT,RIGHT],
    $fn=36
);


color("purple")
translate([screw_outer_dist_x/2, 0, neck_height/2])
cube([screw_outer_dist_x+2,screw_inner_dist_y-4,neck_height], center=true);


color("purple")
translate([screw_outer_dist_x/2, 0, neck_height/2])
cuboid(
    [screw_outer_dist_x+2,screw_inner_dist_y-4,neck_height], rounding=-2,
    edges=[BOT], except=[FRONT,BACK],
    $fn=36
);



translate([0,-screw_d - screw_inner_dist_y/2, -plate_height + 0.1])
difference() {
    color("blue")
    //translate([-screw_d,-screw_d,0])
    //cube([screw_outer_dist_x + 2*screw_d, screw_outer_dist_y + 2*screw_d, plate_height])
   translate([screw_outer_dist_x/2,screw_outer_dist_y/2,plate_height/2])
    
    cuboid([screw_outer_dist_x + 2*screw_d, screw_outer_dist_y + 2*screw_d, plate_height], rounding=3, except=[TOP,BOT]);
    ;
    
    
    
    

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
}