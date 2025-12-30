// --- PARAMETERS ---
bed_size = 200;
$fn = 90;

// Chassis Dimensions
wheelbase = 130;  
arm_width = 34;   // Slightly wider to accommodate the hole grid
thickness = 3;    
fillet_radius = 25; // Bigger fillets for the "organic/tech" look

// Motor Mount Details
slot_width = 3.0; 
slot_length = 20;
slot_separation = 12; 

// Raspberry Pi Zero Mounting
pi_w = 23;        
pi_l = 58;        
pi_hole_dia = 2.6; 

// Grid System Parameters
grid_spacing = 10; // Standard 10mm spacing
m3_hole = 2.9;     // Loose fit for M3 screws

// --- MAIN RENDER ---

linear_extrude(height = thickness) {
    difference() {
        
        // 1. POSITIVE SHAPE (The Body)
        offset(r = -fillet_radius) offset(r = fillet_radius)
        union() {
            // Central Hub
            circle(r=35);
            
            // The Arms
            for(i = [45, 135, 225, 315]) {
                rotate([0, 0, i])
                hull() {
                    translate([10,0]) circle(r=arm_width/2); // Blend into hub
                    translate([wheelbase/sqrt(2), 0]) circle(r=arm_width/2);
                }
            }
        }

        // 2. NEGATIVE SHAPES (The Cutouts)
        
        // --- A. Raspberry Pi Zero Mount ---
        for (x_sign = [-1, 1], y_sign = [-1, 1]) {
             translate([x_sign*pi_l/2, y_sign*pi_w/2]) circle(d=pi_hole_dia);
             translate([x_sign*pi_w/2, y_sign*pi_l/2]) circle(d=pi_hole_dia); // Rotated option
        }
        
        // Center Wire Pass-through
        circle(r=12);

        // --- B. The "Reactor" Battery Strap Slots ---
        // Large slots near the center for velcro straps (holding the battery bank)
        for(i = [0, 90, 180, 270], dist=[28, 20]) {
            rotate([0, 0, i])
            translate([dist, 0])
            hull() {
                translate([0, 5]) circle(d=4);
                translate([0, -5]) circle(d=4);
            }
        }

        // --- C. Motor Slots (Critical) ---
        for(i = [45, 135, 225, 315]) {
            rotate([0, 0, i])
            translate([wheelbase/sqrt(2) - 0, 0]) {
                rotate([0,0,-i]) {
                translate([-slot_length/2, slot_separation/2])
                # hull() { circle(d=slot_width); translate([slot_length, 0]) circle(d=slot_width); }
                
                translate([-slot_length/2, -slot_separation/2])
                # hull() { circle(d=slot_width); translate([slot_length, 0]) circle(d=slot_width); }
                }
            }
        }

        // --- D. The "Future-Proof" Grid (M3 Holes & Lightening Slots) ---
        for(i = [45, 135, 225, 315]) {
            rotate([0, 0, i]) {
                // We run a loop starting from outside the hub up to the motor mounts
                for (dist = [34 : grid_spacing : wheelbase/sqrt(2) - 12]) {
                    
                    // 1. The "Side Rails" - M3 Mounting Grid
                    translate([dist, 12]) circle(d=m3_hole);
                    translate([dist, 6]) circle(d=m3_hole);
                    translate([dist, -6]) circle(d=m3_hole);
                    translate([dist, -12]) circle(d=m3_hole);
                    
                    // 2. The "Truss" - Central Lightening/Zip-tie Slots
                    // We make these slightly staggered or continuous for a "Tech" look
                    translate([dist, 0])
                    hull() {
                        translate([-2, 0]) circle(d=3); // Oval shape
                        translate([2, 0]) circle(d=3);
                    }
                }
            }
        }
    }
}