# PlanarMechSim

## A Planar Real-World Mechanical Simulator Workbench for FreeCAD&nbsp;1.1+

### For the Calculation and Simulation of the Real-World Dynamics of Planar Rigid-Body Mechanical Systems<br> [Previously "NikraDAP" for FreeCAD 0.x]</h3>

It is based on the DAP solver algorithm developed by P.E.&nbsp;Nikravesh in his book: <br><em>PLANAR MULTIBODY DYNAMICS: Formulation, Programming with MATLAB, and Applications</em>, 2nd Edition, *P.E.&nbsp;Nikravesh*, CRC&nbsp;Press, 2018<br><br>
<img width = '640' src = '../Media/QuadPendulum.gif'><br>
**Simulation of the <em>actual motion</em> of a quadruple pendulum using PlanarMechSim**

Given a mechanism which has been assembled using FreeCAD's built-in **Assembly** workbench, and which allows only motion of its components within the **x-y** plane under the force of gravity acting in the **-Y** direction, then the entire assembly can be fed into **PlanarMechSim** which will then calculate the development of the positions of all its constituent bodies as a function of time.  Once the calculations have been completed, the motion of the system can be viewed in the form of an animation of its actual movement displayed on the screen.  Alternatively, the user can request for a spread-sheet readable file to be written to disk which can be read into a spread-sheet of choice (<em>e.g.</em> Excel, LibreCalc) and the real-world motion of the system can be further analysed graphically or otherwise.

The spread-sheet file which is generated, contains data for each of the moving bodies of the system, including the position, orientation, velocity, and acceleration of their respective centres of mass, and their associated joints.  Furthermore, the reaction forces on its various joints (sometimes referred to as <em>lambdas</em>) are tabulated, as well as the kinetic and potential energies of each of the moving bodies.  All of these values are tabulated for the entire length of time, and at the time resolution which has been selected.

**PlanarMechSim** simulates the real-world motion of a real-world collection of bodies under the real-world conditions that the user has selected.  It does **NOT** perform the same function as FreeCAD's built-in simulator.  Whereas in FreeCAD's simulator, the user selects which joint moves, and the speed at which it moves, **PlanarMechSim** uses the **physics** governing the motion of each part, and the forces acting upon it, to determine its motion.  

As part of the calculations necessary to determine an accurate representation of the motion of all the sub-bodies in the mechanical system, **PlanarMechSim** calculates the mass, volume, centre of mass (also referred to as <em>centre of gravity</em>) and the moment of inertia through the centre of mass of each of the sub-bodies.  To determine these values accurately, the density of each part of the sub-body must be known.  However, the density of each sub-part is set in FreeCAD by simply specifying the <em>material</em> from which it is made. [Right-click on the body name in the model tree, and select the <em>Material</em> option in the drop-down menu which appears.]  Thus if the material property of each of the sub-bodies was specified when they were created, (as good practice necessitates), the motion of a sub-body will be physically correct, even if it comprises components of even widely differing densities.  Furthermore, as a result of these tedious calculations being done automatically, **PlanarMechSim** can even be used as a quick centre-of-mass and moment-of-inertia calculator.  The values can easily be viewed in the <em>Properties</em> (or <em>Data</em>) window of the sub-body once the **PlanarMechSim** initialise icon [![initialise Icon](../Icons/PlanarMechSim1.png)] has been selected.

## Future Plans

**PlanarMechSim** can handle various types of joints, as defined by the **Assembly** workbench, <em>viz.</em>

» **Fixed** joint,

» **Revolute** joint,

» **Revolute-Revolute** distance joints,

» **Translational (sliding)** joints, and

» **Revolute-Translational** distance (**pin-in-slot**) joints.

The rest of the joints which are defined by the **Assembly** workbench, which act within the plane, will be added in the near future.

The only external force which **PlanarMechSim** currently makes allowance for, is the force of gravity in the **-Y** direction.  However, the implementation of other forces built into the system, such as springs and dampers, is in the pipe-line.  It will also soon be possible to energise the system with periodic inputs, which will enable the important study of resonances.

<div align = 'center' >
<img width = '200' src = '../Media/Child.jpg' /><br>
Watch this space --- PlanarMechSim is growing
</div>


# ---------------------------------------
Cecil Churms,<br>
Johannesburg,<br>
South Africa.<br><br>
Document last updated: 4th March 2026<br>
