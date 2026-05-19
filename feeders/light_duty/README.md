light duty feeder
=================

This feeder was designed to deliver rice grains for "rice pile" type experiments.

A driving design principle for the light duty feeder is extremely low cost.
This has been achieved by using an off-the-shelf plumbing part for the main feeder housing, and standard hardware and mounting configurations. 


This feeder may not be sutiable for clastic sediments, due to the inherent strength of 3D printed materials.
The design and print instructions are optimized for easy printing and maximum strength for FDM printing.  


Bill of Materials
-----------------

![exploded light duty feeder](/feeders/light_duty/media/light_duty_labeled.png)

* 1 x 1 inch schedule 40 PVC tee connector
* 1 x 608RS bearing
* SET SCREW AND NUT
* [a motor assembly](/motor_assemblies/)and appropriate mounting screws
* other 3D printed components (see below)

* you will need various allen wrenches, a small hacksaw, screwdriver, etc

Instructions and build notes
----------------------------

Build notes
^^^^^^^^^^^

* The `end_cap` has mounting holes for NEMA 17 and 23 stepper motors, as well as the AC motor listed in the motor assembly section. 
* The `chute` has a mounting point for a 608 bearing. The feeder may function fine without the bearing, but will have considerably more play in the auger shaft.
* The `auger` is designed for a motor assembly with an 8mm D shaft.

Printing
^^^^^^^^

All components can be printed in material of your choice. 
PLA works well, but PETG or ABS may provide stronger components. 
Both textured and flat build plates will be fine. 
All parts can be printed with 15% infill, except the auger, which should be printed at 100% infill.

* The auger halves should be printed with the flat side down, and then glued together with CA glue. 
  * This part should be printed at 100% infill.
  * If you would like to print the auger in a resin printer, an unsplit auger .stl file is also provided.
* Chute cap should be printed on bearing side. 
* End cap should be printed on motor side.
* Hopper should be printed on wide end (i.e., upside down funnel). 

Assembly
^^^^^^^^

After printing all components:
1. using a saw, cut a small notch in end of one side of the long edge of the PVC tee, with the notch on the same side as the short side of the tee.
1. insert the bearing into the back of the `chute`.
1. insert the MX nut into the back of the `auger`. 
1. attach `end_cap` to motor face using appropriate screws.
1. slide `auger` onto motor output shaft and tighten MX set screw.
1. slide `chute` over `auger` and align with notch in PVC tee. Some force may be required to seat the `auger` end into the bearing.
1. insert `hopper` into PVC tee.

