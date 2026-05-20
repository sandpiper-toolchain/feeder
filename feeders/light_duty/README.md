# light duty feeder

This feeder was designed to deliver rice grains for "rice pile" type experiments.

![light duty feeder assembly rendered](/feeders/light_duty/media/light_duty_rendered.png){height=420}

A driving design principle for the light duty feeder is extremely low cost.
This has been achieved by using an off-the-shelf plumbing part for the main feeder housing, and standard hardware and mounting configurations. 


This feeder may not be suitable for clastic sediments, due to the inherent strength of 3D-printed materials.
The design and print instructions are optimized for easy printing and maximum strength for FDM printing.  


## Bill of Materials

![exploded light duty feeder](/feeders/light_duty/media/light_duty_labeled.png){width=600}

* 1 x 1 inch schedule 40 PVC tee connector
* 1 x 608RS bearing
* 1 x M4 nut
* 1 x M4 by 5 mm set screw
* [a motor assembly](/motor_assemblies/) with 8 mm output shaft, and appropriate mounting screws
* 3D-printed components (see below)

You also will need standard tools, likely including Allen wrenches, a hacksaw, a screwdriver, etc.


## Instructions and build notes

### Build notes

* The `end_cap` has mounting holes for NEMA 17 and 23 stepper motors, as well as the AC motor listed in the motor assembly section. 
* The `chute` has a mounting point for a 608 bearing. The feeder may function fine without the bearing, but will have considerably more play in the auger shaft.
* The `auger` is designed for a motor assembly with an 8 mm D shaft.

### Printing

All components can be printed in material of your choice. 
PLA works well, but PETG or ABS may provide stronger components. 
Both textured and flat build plates will be fine. 
All parts can be printed with 15% infill, except the `auger`, which should be printed at 100% infill.

* The `auger` halves should be printed with the flat side down, and then glued together with CA glue. 
  * This part should be printed at 100% infill.
  * If you would like to print the `auger` in a resin printer, an unsplit auger .stl file is also provided.
* The `chute` should be printed on the bearing side. 
* The `end_cap` should be printed on motor side.
* The `hopper` should be printed on the wide end (i.e., upside down). 

### Assembly

After printing all components:
1. Using a saw, cut a small notch in end of one side of the long edge of the PVC tee, with the notch on the same side as the short side of the tee. The notch should be larger than the corresponding block on the `chute` (cut a ~7 mm  wide by ~11 mm deep notch); it is okay if the notch is slightly larger than needed creating some play, but try to keep it at tight as possible.
1. Insert the bearing into the back of the `chute`.
1. Insert the M4 nut into the back of the `auger`. You can use some CA glue to hold the nut in place, but it is not necessary.  
1. Attach the `end_cap` to motor face using appropriate screws and mounting holes.
1. Slide the `auger` onto the motor output shaft, and tighten M4 set screw onto flat of D output shaft.
1. Slide the `chute` over the `auger`, and carefully align block with notch in PVC tee and `auger` end with inner bearing hole. Some force may be required to seat the `auger` end into the inner bearing hole.
1. Insert the `hopper` into PVC tee.
1. Fill `hopper` with granular material, provide power to motor assembly. 
