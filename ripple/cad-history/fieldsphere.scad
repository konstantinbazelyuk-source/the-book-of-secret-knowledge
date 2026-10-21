// Ripple FieldSphere v0.1. Units: mm. Open geometry source.
// Manufacture: 8 labelled handed corner hubs; 12 struts; optional 4 LED sleeves,
// 4 receiver sleeves; coil bobbin. All optical paths aim toward the CENTER.
// Coordinate convention: vertices of cube inscribed in a sphere of R=155.885 mm.
// Source/detector electronics and sensor PCB placement require user alignment.
$fn=56;
node = 90; hub_side=30; beam_side=11.8; socket_width=12.35;
// Socket opening at negative coordinate, stop at x = -2; rod inserts until ~-3.
module inward_socket(){
    translate([-15.1,-socket_width/2,-socket_width/2])
        cube([13.1,socket_width,socket_width]);
}
module align_z_to(v){
    len=sqrt(v[0]*v[0]+v[1]*v[1]+v[2]*v[2]);
    axis=[-v[1],v[0],0];
    angle=acos(v[2]/len);
    rotate(a=angle, v=axis) children();
}
module corner_hub(sx=1,sy=1,sz=1){
  scale([sx,sy,sz]) difference(){
    union(){
      cube([hub_side,hub_side,hub_side],center=true);
      // Flat outward radial alignment flange, purely optical enclosure anchor.
      align_z_to([1,1,1]) translate([0,0,17]) cylinder(d=18,h=3,center=true);
    }
    inward_socket();
    rotate([0,0,90]) inward_socket();
    rotate([0,-90,0]) inward_socket();
    // optical radial aperture. ALL optical paths must be terminated by detector/stop.
    align_z_to([1,1,1]) cylinder(d=6.1,h=60,center=true);
  }
}
module strut(){ // nominal 175.0 mm between the back walls of opposing hub sockets
  cube([175.0,beam_side,beam_side],center=true);
}

// Curved spherical rails. Each rail curves OUT from chord toward the
// circumscribed sphere; straight sockets at ends (|x|>=75 mm).
// Four handed variants: rail_pp(+y,+z), rail_pm, rail_mp, rail_mm.
function smooth(t)=3*t*t-2*t*t*t;
function crown(x)=20.227 * smooth(max(0,min(1,(75-abs(x))/75)));
module curved_rail(sy=1,sz=1){
  for(i=[0:34]) hull(){
    x1=-87.5+i*175/35; x2=-87.5+(i+1)*175/35;
    translate([x1,sy*crown(x1),sz*crown(x1)])cube([0.6,beam_side,beam_side],center=true);
    translate([x2,sy*crown(x2),sz*crown(x2)])cube([0.6,beam_side,beam_side],center=true);
  }
}

module led_sleeve(){
  // Friction-fit 5 mm LED into optical bore, user to adjust for print tolerance.
  difference(){
    union(){cylinder(d=6.0,h=16);translate([0,0,14]) cylinder(d=10,h=2);}
    translate([0,0,-0.5])cylinder(d=5.15,h=17);
  }
}
module detector_sleeve(){
  // 4 mm aperture in front of OPT101, mount PCB behind collar with tape/fixture.
  difference(){
    union(){cylinder(d=6.0,h=17);translate([0,0,14]) cylinder(d=15,h=3);}
    translate([0,0,-0.5])cylinder(d=3.2,h=19);
  }
}
module coil_bobbin(){
  // 100 turns of enamelled copper wire around outer 25mm nominal radius;
  // wind between flanges; coil effective radius must be measured after winding.
  difference(){
    union(){cylinder(d=50,h=11,center=true);
      for (z=[-7,7])translate([0,0,z])cylinder(d=59,h=3,center=true);
    }
    cylinder(d=38,h=25,center=true);
  }
}
module sensor_test_caddy(){
  // External plastic pad with 4 mounting holes (2.5mm) spaced approx 21mm.
  // Board outlines differ by manufacturer; inspect breakout before drilling.
  difference(){
    cube([30,30,3],center=true);
    for(x=[-10.5,10.5],y=[-10.5,10.5])
      translate([x,y,0]) cylinder(d=2.8,h=6,center=true);
  }
}
module assembly(){
  color("#f2b84d")
  for(x=[-1,1],y=[-1,1],z=[-1,1])translate([x*node,y*node,z*node])corner_hub(-x,-y,-z);
  color("#667d8b"){
    for(y=[-1,1],z=[-1,1])translate([0,y*node,z*node])curved_rail(y,z);
    for(x=[-1,1],z=[-1,1])translate([x*node,0,z*node])rotate([0,0,90])curved_rail(-x,z);
    for(x=[-1,1],y=[-1,1])translate([x*node,y*node,0])rotate([0,90,0])curved_rail(y,x);
  }
  // illustrative optical paths: LEDs/sensors must be shielded, not lasers.
  for(a=[-1,1],b=[-1,1]){
    color([0.8,0.15,0.1,0.17])
      align_z_to([1,a,b]) cylinder(d=1.5,h=311,center=true);
  }
  color("#3aa876") rotate([0,90,0])coil_bobbin();
}
part="assembly";
if(part=="assembly") assembly();
else if(part=="hub_ppp")corner_hub(1,1,1);
else if(part=="hub_ppm")corner_hub(1,1,-1);
else if(part=="hub_pmp")corner_hub(1,-1,1);
else if(part=="hub_pmm")corner_hub(1,-1,-1);
else if(part=="hub_mpp")corner_hub(-1,1,1);
else if(part=="hub_mpm")corner_hub(-1,1,-1);
else if(part=="hub_mmp")corner_hub(-1,-1,1);
else if(part=="hub_mmm")corner_hub(-1,-1,-1);
else if(part=="strut")strut(); // optional cubic scaffold, not primary build
else if(part=="rail_pp")curved_rail(1,1);
else if(part=="rail_pm")curved_rail(1,-1);
else if(part=="rail_mp")curved_rail(-1,1);
else if(part=="rail_mm")curved_rail(-1,-1);
else if(part=="led_sleeve")led_sleeve();
else if(part=="detector_sleeve")detector_sleeve();
else if(part=="coil_bobbin")coil_bobbin();
else if(part=="sensor_test_caddy")sensor_test_caddy();