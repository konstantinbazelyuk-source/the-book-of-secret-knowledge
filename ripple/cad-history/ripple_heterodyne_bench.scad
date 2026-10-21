/*
Ripple Heterodyne v0.1 -- printable, nominal hardware support structures.
Units mm. Optics are NOT included in STL exports. Tune fits with test prints.
All part-local origins lie on top of the base; assembly() positions on 210 mm base.
Copyright 2026, released under MIT license.
*/
$fn = 60;
part = "assembly"; // override with -D 'part="name"'
W=210; H=210; BASE_T=6;
bs=[92,100];
// Through holes for M3 bolts at all mounts, registered to printed fixtures.
mounts = concat(
  [for (yy=[-10,10]) [33,100+yy]],
  [for (xx=[-9,9],yy=[-9,9]) [bs[0]+xx,bs[1]+yy]],
  [for (xx=[-14,14]) [bs[0]+xx,163]],
  [for (xx=[-12,12]) [bs[0]+xx,30]],
  [for (xx=[-9,9]) [bs[0]+xx,53]],
  [for (xx=[139,193],yy=[-24,24]) [xx,100+yy]]
);

module crosshole_x(d,l=150){rotate([0,90,0]) cylinder(h=l,d=d,center=true);}
module crosshole_y(d,l=150){rotate([90,0,0]) cylinder(h=l,d=d,center=true);}
module holes_z(points,d=3.4){for (p=points) translate([p[0],p[1],-1]) cylinder(h=100,d=d);}
module base_plate(){
  difference(){
    cube([W,H,BASE_T]);
    for (xy=mounts)
      if (xy[1] == 163 && (xy[0] == bs[0]-14 || xy[0] == bs[0]+14))
        hull() {
          translate([xy[0],xy[1]-5,-1]) cylinder(h=BASE_T+2,d=3.4);
          translate([xy[0],xy[1]+5,-1]) cylinder(h=BASE_T+2,d=3.4);
        }
      else translate([xy[0],xy[1],-1]) cylinder(h=BASE_T+2,d=3.4);
    for (xy=[[7,7],[W-7,7],[7,H-7],[W-7,H-7]])
      translate([xy[0],xy[1],-1]) cylinder(h=BASE_T+2,d=4.5);
    // shallow alignment reference for beam axes, engraved into upper surface
    translate([5,99.5,BASE_T-0.55]) cube([199,1,0.7]);
    translate([91.5,5,BASE_T-0.55]) cube([1,199,0.7]);
  }
}
module cube_cradle(){
  // 10mm 50:50 NPBS cube. Bottom face z=19 => beam z=24 locally (30 overall)
  difference(){
    union(){
      translate([-12,-12,0]) cube([24,24,4]);
      translate([-6,-6,4]) cube([12,12,15]);
      // corner-only retainers; never cover central clear apertures
      for (x=[-5.7,5.7],y=[-5.7,5.7])
        translate([x,y,19]) cube([2,2,3],center=true);
    }
    holes_z([[-9,-9],[-9,9],[9,-9],[9,9]]);
  }
}
module laser_cradle(){
  difference(){
    union(){
      translate([-16,-14,0]) cube([32,28,4]);
      translate([-13,-9,4]) cube([26,18,23]);
    }
    holes_z([[0,-10],[0,10]]);
    translate([0,0,24]) crosshole_x(12.4,40);
    // open cradle top so a 12mm laser cylinder drops in from above
    translate([-17,-6.2,24]) cube([34,12.4,20]);
    // transverse openings accept zip-tie straps around module
    for(x=[-9,9]) translate([x-1.6,-14,9]) cube([3.2,28,2.4]);
  }
}
module detector_rail(){
  // Fixture for a 30x30x1.6 mm perfboard carrying a DIP OPT101 oriented into +Y.
  difference(){
    union(){
      translate([-17,-10,0]) cube([34,20,4]);
      for(x=[-17,12]) translate([x,4,4]) cube([5,6,39]);
      translate([-17,4,4]) cube([34,6,7]);
    }
    holes_z([[-12,0],[12,0]]);
    // standing card channel, y is thickness direction
    translate([-16,5.7,10]) cube([32,1.9,34]);
    translate([-13,4.5,9]) cube([26,4.0,2]);
  }
}
module nd_filter_holder(){
  // 12.7mm unmounted absorptive OD ~3 filter, 1.5-2.5mm thick; manually secure.
  // Optical beam travels along Y. Filter installed through open top into a
  // shallow circular channel (keep retainer off clear aperture).
  difference(){
    union(){
      translate([-15,-8,0]) cube([30,16,4]);
      translate([-9,-4,4]) cube([18,8,36]);
    }
    holes_z([[-9,0],[9,0]]);
    translate([0,0,24]) crosshole_y(7,12);
    // sliding pocket 13mm across X, slot 2.7mm along Y
    translate([-6.55,-1.35,17]) cube([13.1,2.7,25]);
    // bottom circular rim is retained outside the optical hole
  }
}
module fixed_mirror_back(){
  // Rear plate and foot; front mirror carrier is adjusted with 3 M3x25 + 3 springs.
  difference(){
    union(){
      translate([-21,-15,0]) cube([42,30,5]);
      translate([-20,8,5]) cube([40,4,41]);
      // two buttresses
      for(x=[-18,15]) translate([x,0,5]) cube([3,12,18]);
    }
    holes_z([[-14,0],[14,0]]);
    for(p=[[-15,11],[15,11],[0,41]])
      translate([p[0],10,p[1]]) crosshole_y(3.4,9);
  }
}
module mirror_carrier(){
  // Front surface mirror 20 x 20 x 2 mm bonded to recess on -Y face.
  // Rear M3 spring stack to backer. Nuts accessible from front outside optical area.
  difference(){
    translate([-19,-5,6]) cube([38,4,40]);
    translate([-10.2,-5.05,14]) cube([20.4,0.85,20.4]);
    for(p=[[-15,11],[15,11],[0,41]]){
      translate([p[0],-3,p[1]]) crosshole_y(3.4,8);
      // shallow nut capture accessible from -Y
      translate([p[0],-5.1,p[1]]) rotate([90,0,0]) cylinder(d=6.4,h=2.8,$fn=6,center=true);
    }
  }
}
module rail_support(){
  difference(){
    union(){
      translate([-6,-28,0]) cube([12,56,25]);
      for(y=[-26,20]) translate([-6,y,0]) cube([12,6,4]);
    }
    holes_z([[0,-24],[0,24]]);
    for(y=[-18,0,18]) translate([0,y,12]) crosshole_x(y==0 ? 6.8:6.3,15);
    // rod securing pilot holes from top: drill/tap to suit plastic / inserts
    for(y=[-18,18]) translate([0,y,16.5]) cylinder(h=10,d=2.7);
  }
}
module slider_carriage(){
  // Two 6mm guide rods in LM6UU bearings (6 ID/12 OD/19 long) and M6x1 screw.
  // Moving mirror plane nominally x=-15 local (global x=149 at carriage x=164).
  difference(){
    union(){
      translate([-14,-29,0]) cube([28,58,24]);
      // front mirror flat; reflected beam approaches along +X so mirror faces -X.
      translate([-17,-13,15]) cube([4,26,27]);
    }
    for (y=[-18,0,18])
      translate([0,y,12]) crosshole_x(y==0 ? 6.8 : 12.15,38);
    // side-load M6 nut chamber at x=-3..+3; top access, retained with cover
    translate([0,0,12]) rotate([0,90,0]) cylinder(h=7,d=11.8,$fn=6,center=true);
    translate([-3.6,-6.5,12]) cube([7.2,13,15]);
    // M3 cover screws use drilled self-tap pilot holes
    for (x=[-9,9]) translate([x,0,20]) cylinder(h=8,d=2.7);
    // mirror inset 20.4 x 20.4, z=24 (local), toward incoming -X
    translate([-17.1,-10.2,13.8]) cube([0.9,20.4,20.4]);
  }
}
module nut_cover(){
  difference(){
    translate([-14,-9,0]) cube([28,18,3]);
    for(x=[-9,9]) translate([x,0,-1]) cylinder(h=5,d=3.4);
  }
}
module crank_knob(){
  // M6x1 shaft end: locked by two M6 nuts either side or epoxy (do not free-spin).
  difference(){
    union(){
      cylinder(h=10,d=26);
      for (k=[0:7]) rotate([0,0,k*45]) translate([12,0,0]) cylinder(h=10,d=5);
    }
    translate([0,0,-1]) cylinder(h=12,d=6.3);
  }
}
module bolts_visual(){
  for(m=mounts) translate([m[0],m[1],BASE_T]) color("silver") cylinder(d=3,h=3);
}
module optics_visual(){
  color([.32,.7,1,.35]) translate([92,100,BASE_T+24]) cube([10,10,10],center=true); // visual-only cube
  // ray routes at z=30
  color([1,0.2,0.15,.7]){
    translate([33,100,30]) rotate([0,90,0]) cylinder(d=1,h=116);
    translate([92,31,30]) rotate([-90,0,0]) cylinder(d=1,h=132);
  }
}
module assembly(){
  color("slategray") base_plate();
  translate([33,100,BASE_T]) color("royalblue") laser_cradle();
  translate([92,100,BASE_T]) color("orange") cube_cradle();
  translate([92,163,BASE_T]) color("royalblue") fixed_mirror_back();
  translate([92,163,BASE_T]) color("seagreen") mirror_carrier();
  translate([92,30,BASE_T]) color("royalblue") detector_rail();
  translate([92,53,BASE_T]) color("orchid") nd_filter_holder();
  for(x=[139,193]) translate([x,100,BASE_T]) color("royalblue") rail_support();
  translate([164,100,BASE_T]) color("seagreen") slider_carriage();
  translate([164,100,BASE_T+24]) color("orange") nut_cover();
  for(y=[82,118]) translate([166,y,BASE_T+12]) color("lightsteelblue") crosshole_x(6,66);
  translate([180,100,BASE_T+12]) color("silver") crosshole_x(6,100);
  translate([219,100,BASE_T+12]) rotate([0,90,0]) color("orange") crank_knob();
  optics_visual();
}
if(part=="base_plate") base_plate();
else if(part=="cube_cradle") cube_cradle();
else if(part=="laser_cradle") laser_cradle();
else if(part=="detector_rail") detector_rail();
else if(part=="fixed_mirror_back") fixed_mirror_back();
else if(part=="nd_filter_holder") nd_filter_holder();
else if(part=="mirror_carrier") mirror_carrier();
else if(part=="rail_support") rail_support();
else if(part=="slider_carriage") slider_carriage();
else if(part=="nut_cover") nut_cover();
else if(part=="crank_knob") crank_knob();
else assembly();