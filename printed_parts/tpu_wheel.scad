// ==============================================
// AIRLESS TIRE - EXPOSED VANE TREAD
// ==============================================

/* [Dimensions] */
tire_width = 25;
axle_radius = 4;
hub_outer_radius = 16; 
spoke_outer_radius = 38; 
tire_outer_radius = 48; // The solid rim surface

/* [Tread Configuration] */
tread_extension = 1.5; // How far the vanes poke out (1.0 to 1.5mm is the sweet spot)

/* [Vane Configuration] */
num_vanes = 40; // Increased slightly to ensure smooth rolling on the tips
vane_thickness = 0.8; 
vane_angle = 45; 

$fn = 120;

// --- Helper Modules ---
module ring(height, r_outer, r_inner) {
    difference() {
        cylinder(h=height, r=r_outer, center=true);
        cylinder(h=height+1, r=r_inner, center=true);
    }
}

// ==============================================
// ZONE 1: HUB (Red)
// Intended Slicer Settings: 100% Solid Infill, high wall count.
// Function: Rigid connection to motor.
// ==============================================
module Zone1_Hub() {
    color("FireBrick") {
        ring(height=tire_width+0.02, r_outer=hub_outer_radius, r_inner=axle_radius);
    }
}

// ==============================================
// ZONE 2: COMPLIANT SPOKES (Blue)
// Intended Slicer Settings: 10% Gyroid Infill. 0 Top/Bottom Layers.
// Wall Thickness: If your slicer allows, set the infill line width slightly thinner (e.g., 100% of nozzle width, not more).
// Function: Shock absorption for rocks.
// "Infill/Perimeter Overlap". Increase it to 25-30%.
// Note: We start exactly where the hub ends.
// ==============================================
module Zone2_Spokes() {
    color("SteelBlue") {
        ring(height=tire_width+0.01, r_outer=spoke_outer_radius, r_inner=hub_outer_radius);
    }
}

// ==============================================
// ZONE 3: EXPOSED SHEAR VANES (Green)
// Intended Slicer Settings: ~40-50% Gyroid Infill. 
// You might want 2-3 top/bottom solid layers here for actual grip surface.
// Function: Distribute load evenly, prevent torsional wind-up, provide grip.
// Note: This is the "centimeter worth of vanes" and final layer combined.
// print slow: slow (20-30 mm/s).
// Enable "Avoid Crossing Perimeters" (Combing) to prevent stringing inside the chevron V's.
// ==============================================
module Zone3_ShearVanes() {
    color("ForestGreen") {
        union() {
            // 1. The "Drum" Skins (These hold the tire together)
            //    The Outer Skin is the "floor" that prevents mud/rocks from getting INSIDE the tire.
            ring(height=tire_width, r_outer=tire_outer_radius, r_inner=tire_outer_radius - 1.2);
            ring(height=tire_width, r_outer=spoke_outer_radius + 1.2, r_inner=spoke_outer_radius);
            
            //    Center Divider (Essential for stability)
            ring(height=0.8, r_outer=tire_outer_radius, r_inner=spoke_outer_radius);

            // 2. The Vanes (Piercing through the skin)
            intersection() {
                // BOUNDARY: We allow this to go PAST the tire_outer_radius by 'tread_extension'
                cylinder(h=tire_width, r=tire_outer_radius + tread_extension, center=true);
                
                // The Vane Geometry
                union() {
                    // Bottom Half Vanes
                    translate([0,0, -tire_width/4])
                    for (i = [0 : num_vanes-1]) {
                        rotate([0, 0, i * (360 / num_vanes)])
                        translate([(spoke_outer_radius + tire_outer_radius) / 2, 0, 0])
                        rotate([0, 0, vane_angle])
                        // Make cube slightly longer to ensure it reaches the new extension
                        cube([tire_outer_radius - spoke_outer_radius + 5, vane_thickness, tire_width/2], center=true);
                    }

                    // Top Half Vanes
                    translate([0,0, tire_width/4])
                    for (i = [0 : num_vanes-1]) {
                        rotate([0, 0, i * (360 / num_vanes)])
                        rotate([0, 0, (360 / num_vanes) * .3])
                        translate([(spoke_outer_radius + tire_outer_radius) / 2, 0, 0])
                        rotate([0, 0, -vane_angle])
                        cube([tire_outer_radius - spoke_outer_radius + 5, vane_thickness, tire_width/2], center=true);
                    }
                }
            }
        }
    }
}

// ==============================================
// DISPLAY
// ==============================================

Zone1_Hub();
Zone2_Spokes();
Zone3_ShearVanes();