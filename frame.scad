// --- PARAMETERS ---
// Your printer bed size limit (safeguard)
bed_size = 200;
$fn = 90;

// Chassis Dimensions
wheelbase = 130;  // Distance between wheel centers (side to side & front to back)
arm_width = 35;   // Width of the X arms
thickness = 3;    // Thickness of the main plate
fillet_radius = 20; // Radius of the curve between arms (Strength!)

// Motor Mount Details
// Slots allow for "guessing" the bracket hole spacing
slot_width = 3.2; // Fits M3 screws loose
slot_length = 25;
slot_separation = 18; // Distance between the two parallel slots

// Raspberry Pi Zero W Mounting (Standard Dimensions)
pi_w = 23;        // Hole spacing short side
pi_l = 58;        // Hole spacing long side
pi_hole_dia = 2.6;// M2.5 screws

// Zip Tie Slots for wire management
zip_w = 4;
zip_l = 10;

// --- MAIN RENDER ---

// We build the entire 2D profile first, then extrude it once
linear_extrude(height = thickness) {
    difference() {
        
        // 1. THE POSITIVE SHAPE (With Fillets)
        // The offset(r=-x) offset(r=x) technique rounds internal corners
        offset(r = -fillet_radius) offset(r = fillet_radius)
        union() {
            for(i = [45, 135, 225, 315]) {
                hull() {
                    circle(r=25); // Center Hub
                    rotate([0, 0, i])
                    translate([wheelbase/sqrt(2), 0])
                    circle(r=arm_width/2); // Arm End
                }
            }
        }

        // 2. THE NEGATIVE SHAPES (Holes)
        
        // Pi Zero Mounting Holes
        for (x_sign = [-1, 1], y_sign = [-1, 1]) {
             translate([x_sign*pi_l/2, y_sign*pi_w/2]) circle(d=pi_hole_dia);
             // Also adding the "Rotate 90" variant from your original code just in case
             translate([x_sign*pi_w/2, y_sign*pi_l/2]) circle(d=pi_hole_dia);
        }

        // Center Wire Cutout
        circle(r=8);

        // Motor Mounting Slots
        for(i = [45, 135, 225, 315]) {
            rotate([0, 0, i])
            translate([wheelbase/sqrt(2) - 5, 0]) {
                // Slot 1
                translate([-slot_length/2, slot_separation/2])
                hull() {
                    circle(d=slot_width);
                    translate([slot_length, 0]) circle(d=slot_width);
                }
                // Slot 2
                translate([-slot_length/2, -slot_separation/2])
                hull() {
                    circle(d=slot_width);
                    translate([slot_length, 0]) circle(d=slot_width);
                }
            }
        }

        // Zip Tie Slots
        for(i = [45, 135, 225, 315]) {
            rotate([0, 0, i])
            translate([40, 0]) {
                hull() {
                    translate([0, 5]) circle(d=zip_w);
                    translate([0, -5]) circle(d=zip_w);
                }
            }
        }
    }
}
