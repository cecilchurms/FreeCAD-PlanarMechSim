# PlanarMechSim

## A Planar Real-World Mechanical Simulator Workbench for FreeCAD&nbsp;1.1+

### For the Calculation and Simulation of the Real-World Dynamics of Planar Rigid-Body Mechanical Systems<br> [Previously "NikraDAP" for FreeCAD 0.x]</h3>

It is based on the DAP solver algorithm developed by P.E.&nbsp;Nikravesh in his book: <br><em>PLANAR MULTIBODY DYNAMICS: Formulation, Programming with MATLAB, and Applications</em>, 2nd Edition, *P.E.&nbsp;Nikravesh*, CRC&nbsp;Press, 2018<br><br>
<img width = '640' src = '../Media/QuadPendulum.gif'><br>
**Simulation of the <em>actual motion</em> of a quadruple pendulum using PlanarMechSim**

Given a mechanism which has been assembled using FreeCAD's built-in **Assembly** workbench, and which allows only motion of its components within the **x-y** plane under the force of gravity acting in the **-Y** direction, then the entire assembly can be fed into **PlanarMechSim** which will then calculate the development of the positions of all its constituent bodies as a function of time.  Once the calculations have been completed, the motion of the system can be viewed in the form of an animation of its actual movement displayed on the screen.  Alternatively, the user can request for a spread-sheet readable file to be written to disk which can be read into a spread-sheet of choice (<em>e.g.</em> Excel, LibreCalc) and the real-world motion of the system can be further analysed graphically or otherwise.

The spread-sheet file which is generated, contains data for each of the moving bodies of the system, including the position, orientation, velocity, and acceleration of their respective centres of mass, and their associated joints.  Furthermore, the reaction forces on its various joints (known as <em>lambdas</em>) are tabulated, as well as the kinetic and potential energies of each of the moving bodies.  All of these values are tabulated for the entire length of time, and at the time resolution which has been selected.

Note that this workbench does **NOT** perform the same function as FreeCAD's built-in simulator.  Whereas in FreeCAD's simulator, the user selects which joint moves, and the speed at which it moves, **PlanarMechSim** uses the **physics** governing the motion of each part, and the forces acting upon it, to determine its motion.  **PlanarMechSim** simulates the real-world motion of a real-world collection of bodies under the real-world conditions that the user has selected.

**PlanarMechSim** can handle various types of joints, as defined by the **Assembly** workbench, <em>viz.</em> **Fixed** joint, **Revolute** joint, **Revolute-Revolute** distance joints, **Translational (sliding)** joints, and **Revolute-Translational** distance (**pin-in-slot**) joints.  The rest of the joints which are defined by the **Assembly** workbench, which act within the plane, will be added in the near future.

# ---------------------------------------
Cecil Churms,<br>
Johannesburg,<br>
South Africa.<br><br>
Last updated: 3rd March 2026<br>
