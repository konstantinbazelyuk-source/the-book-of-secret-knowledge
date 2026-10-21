// KOKORO AC-FIRST / v1.0. Units: millimeters.
// Engineering envelope only. The 8 actuator CYLINDERS are volume placeholders,
// NOT selected motor hardware, and the Ca battery is not manufactured.
// Fixed-base upper-body robot: overall height 650mm. Includes no mobile legs.
$fn=48;
show_electronics=true;
show_bay=true;
base_w=340;base_d=270;base_h=170;
internal_bay_w=240;internal_bay_d=150;internal_bay_h=100;

module base(){
 color([.20,.23,.29]) difference(){
   translate([-base_w/2,-base_d/2,0]) cube([base_w,base_d,base_h]);
   // Real empty battery volume, not a second decorative cube inside solid plastic.
   translate([-internal_bay_w/2,-internal_bay_d/2,35]) cube([internal_bay_w,internal_bay_d,internal_bay_h]);
   // Removable-service access to rear, requiring later door/fastener design.
   translate([-internal_bay_w/2, internal_bay_d/2-0.1,35])
        cube([internal_bay_w, base_d/2-internal_bay_d/2+0.2,internal_bay_h]);
 }
 if(show_bay) color([.15,.75,.90,.65]) translate([-internal_bay_w/2,-internal_bay_d/2,35]) cube([internal_bay_w,internal_bay_d,internal_bay_h]);
 if(show_electronics) color([.18,.63,.40]) translate([-110,-100,138]) cube([220,40,4]); // reserved power electronics board strip, not a PCB
}
module torso(){color([.56,.62,.72]) translate([-120,-78,190]) cube([240,156,300]);}
module head(){
 color([.75,.78,.82]) translate([-60,-60,520]) cube([120,120,125]);
 color([.06,.08,.09]) translate([-52,-61,579]) cube([104,2,30]);
}
module shaft(x,y,z){color([.1,.42,.62]) translate([x,y,z]) rotate([90,0,0]) cylinder(d=44,h=35,center=true);}
module arm(s){
 // s +/-1: shoulder centers near x +/-145 at z 462; elbow z 315
 shaft(s*145,0,462);  // one motor-envelope of two per shoulder; nested axes require rework
 color([.70,.73,.78]) translate([s*150-22,-30,315]) cube([44,60,135]);
 shaft(s*150,0,310);
 color([.73,.75,.81]) translate([s*150-20,-25,172]) cube([40,50,125]);
}
base();torso();head();arm(-1);arm(1);
// 8 DOF target: 2 head + 2 per shoulder + 1 elbow per side = 8.
// Placeholders only and not interference-resolved. Actual mechanics require selected encoders,
// gearboxes, bearings, mounts, torque constraints, cable runs, thermal budgets and fabrication tolerances.