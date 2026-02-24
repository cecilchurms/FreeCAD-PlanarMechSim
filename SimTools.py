# ********************************************************************************
# *                                                                              *
# *   This program is free software; you can redistribute it and/or modify       *
# *   it under the terms of the GNU Lesser General Public License (LGPL)         *
# *   as published by the Free Software Foundation; either version 3 of          *
# *   the License, or (at your option) any later version.                        *
# *   for detail see the LICENCE text file.                                      *
# *                                                                              *
# *   This program is distributed in the hope that it will be useful,            *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of             *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                       *
# *   See the GNU Lesser General Public License for more details.                *
# *                                                                              *
# *   You should have received a copy of the GNU Lesser General Public           *
# *   License along with this program; if not, write to the Free Software        *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston,                      *
# *   MA 02111-1307, USA                                                         *
# *_____________________________________________________________________________ *
# *                                                                              *
# *        ##########################################################            *
# *     #### PlanarMechSim - FreeCAD WorkBench - Revision 1.0 (c) 2026: ####     *
# *        ##########################################################            *
# *                                                                              *
# *               This program suite is an expansion of the                      *
# *                  "Nikra-DAP" workbench for FreeCAD                           *
# *                                                                              *
# *                         Software Development:                                *
# *                     Cecil Churms <churms@gmail.com>                          *
# *                                                                              *
# *             It is based on the MATLAB code Complementary to                  *
# *                  Chapters 7 and 8 of the textbook:                           *
# *                                                                              *
# *                     "PLANAR MULTIBODY DYNAMICS                               *
# *         Formulation, Programming with MATLAB, and Applications"              *
# *                          Second Edition                                      *
# *                         by P.E. Nikravesh                                    *
# *                          CRC Press, 2018                                     *
# *                                                                              *
# *     The original project (Nikra-DAP) was the vision of Lukas du Plessis      *
# *                      <lukas.duplessis@uct.ac.za>                             *
# *              who facilitated its development from the start                  *
# *                                                                              *
# *                     With the advent of FreeCAD 1.x,                          *
# *        the Nikra-DAP software was no longer compatible with the new,         *
# *                    built-in, Assembly functionality.                         *
# *          Nikra-DAP thus underwent a major re-write and was enlarged          *
# *                into the Mechanical Simulator: "PlanarMechSim"                *
# *                                                                              *
# *              The initial stages of  Nikra-DAP  were supported by:            *
# *                 Engineering X, an international collaboration                *
# *                founded by the Royal Academy of Engineering and               *
# *                        Lloyd's Register Foundation.                          *
# *                                                                              *
# *                  An early version of Nikra-DAP was written by:               *
# *            Alfred Bogaers (EX-MENTE) <alfred.bogaers@ex-mente.co.za>         *
# *                          with contributions from:                            *
# *                 Dewald Hattingh (UP) <u17082006@tuks.co.za>                  *
# *                 Varnu Govender (UP) <govender.v@tuks.co.za>                  *
# *                                                                              *
# *                          Copyright (c) 2026                                  *
# *_____________________________________________________________________________ *
# *                                                                              *
# *             Please refer to the Documentation and README for                 *
# *         more information regarding this WorkBench and its usage              *
# *                                                                              *
# ********************************************************************************
import FreeCAD as CAD

from materialtools import cardutils
from PySide import QtGui, QtCore
import math
import numpy as np

Debug = False
#  -------------------------------------------------------------------------
MAXNUMJOINTTYPES = 2
JOINT_TYPE_DICTIONARY = {
                        "Revolute": 0,
                        "Revolute-Revolute": 1,
                        "Fixed": 2,
                        "Translation": 3,
                        "Translation-Revolute": 4,
                        "Disc": 5,
                        "Slider": 6,
                        "Distance": 7,
                        "RackPinion": 8,
                        "Gears": 9,
                        "Belt": 10,
                        "Ball": 11,
                        "Driven-Rotation": 12,
                        "Driven-Translation": 13,
                        "Cylindrical": 14,
                        "Parallel": 15,
                        "Screw": 16,
                        "Angle": 17,
                        "Perpendicular": 18,
                        "GroundedJoint": 19,
                        "Internal": 20,
                        "Undefined": 21,
                        }
MAXFORCES = 1
FORCE_TYPE_DICTIONARY = {"Gravity": 0,
                         "Spring": 1,
                         "Rotational Spring": 2,
                         "Linear Spring Damper": 3,
                         "Rotational Spring Damper": 4,
                         "Unilateral Spring Damper": 5,
                         "Constant Force Local to Body": 6,
                         "Constant Global Force": 7,
                         "Constant Torque about a Point": 8,
                         "Contact Friction": 9,
                         "Motor": 10,
                         "Motor with Air Friction": 11,
                         }
FORCE_TYPE_HELPER_TEXT = [
    "Universal force of attraction between all matter",
    "A device that stores energy when compressed or extended and exerts a force in the opposite direction",
    "A device that stores energy when twisted and exerts a torque in the opposite direction",
    "A device used to limit or retard linear vibration ",
    "Device used to limit movement and vibration caused by rotation",
    "A Device used to dampen vibration in only the one direction",
    "A constant force with direction relative to the Body coordinates",
    "A constant force in a specific global direction",
    "A constant torque about a point on a body",
    "Contact friction between two bodies",
    "A motor with characteristics defined by an equation",
    "A motor defined by an equation, but with air friction associated with body movement"]
#  -------------------------------------------------------------------------
def getallObjects():
    """Return the simGlobal object"""

    for simGlobal in CAD.ActiveDocument.Objects:
        if hasattr(simGlobal, "Name") and simGlobal.Name == "SimGlobal":
            return simGlobal
    return None
#  -------------------------------------------------------------------------
def updateCoGMoI(bodyGroupObj):
    """ Computes:
    1. The world centre of mass of each body in the SimBody
    based on the weighted sum of each solid's centre of mass
    2. The moment of inertia of the SimBody, based on the moment of Inertia for the
    solid through its CoG axis + solid mass * (perpendicular distance
    between the axis through the solid's CoG and the axis through the whole body's
    CoG) squared.   Both axes should be normal to the plane of movement and
    will hence be parallel if everything is OK.
    ****************************************************************************
    IMPORTANT:  FreeCAD and PlanarMechSim work internally with a mm-kg-s system
    ****************************************************************************
    """

    # Determine the vector to convert movement in the selected base plane to the X-Y plane
    xyzToXYRotation = CAD.Rotation(CAD.Vector(0, 0, 1), getallObjects().movementPlaneNormal)

    # Clear the variables for filling
    bodyGroupMass = 0
    bodyGroupVolume = 0
    bodyGroupCoG = CAD.Vector()
    massList = []
    subBodyMoIThroughCoGNormalToMovementPlaneList = []
    subBodyCentreOfGravityList = []

    # Run through all the subBodies in the bodyGroup
    for element in bodyGroupObj.ElementList:
        volume = element.Shape.Volume
        CoG = element.Shape.CenterOfGravity
        density = element.LinkedObject.ShapeMaterial.PhysicalProperties["Density"]

        # element.Shape.Volume returns value in mm3
        # Density stored internally as kg / mm3
        bodyGroupVolume += volume
        space = density.find(" ")
        if space != -1:
            density = float(density[:space])
        else:
            density = 1.0e-6

        # Density in kg/mm3
        # Mass in kg
        # density [kg/mm3] = mass [kg] / Volume [mm3]
        mass = density * volume
        bodyGroupMass += mass
        massList.append(mass)

        # Add the Centre of gravities to a list to use in parallel axis theorem
        subBodyCentreOfGravityList.append(xyzToXYRotation.toMatrix().multVec(CoG))
        # Squash any component of CoG in the z direction, onto the X-Y plane
        # Remember: [-1] is the last element of the list !!!
        subBodyCentreOfGravityList[-1].z = 0.0

        # MatrixOfInertia[MoI] around an axis through the CoG of the element
        # and normal to the MovementPlaneNormal
        if hasattr(element.Shape, "MatrixOfInertia"):
            moi = element.Shape.MatrixOfInertia
        elif hasattr(element.Shape, "SubShape") and hasattr(element.Shape.SubShape, "MatrixOfInertia") :
            moi = element.Shape.SubShape[0].MatrixOfInertia
        else:
            moi = CAD.Matrix()
        MoIVec = moi.multVec(getallObjects().movementPlaneNormal)

        # MoI calculated in [kg*mm^2]
        subBodyMoIThroughCoGNormalToMovementPlaneList.append(MoIVec.z * density)
        bodyGroupCoG += mass * subBodyCentreOfGravityList[-1]

    # Next element

    bodyGroupCoG /= bodyGroupMass
    setattr(bodyGroupObj, "worldCoG", bodyGroupCoG)

    bodyCentreOfGravityMovementPlane = xyzToXYRotation.toMatrix().multVec(bodyGroupCoG)
    bodyCentreOfGravityMovementPlane.z = 0.0

    setattr(bodyGroupObj, "masskg", bodyGroupMass)
    setattr(bodyGroupObj, "volumem3", bodyGroupVolume * 1.0e-9)
    setattr(bodyGroupObj, "densitykgpm3", bodyGroupMass / (bodyGroupVolume * 1.0e-9) )

    setattr(bodyGroupObj, "massg", bodyGroupMass * 1000.0)
    setattr(bodyGroupObj, "volumecm3", bodyGroupVolume * 1.0e-3)
    setattr(bodyGroupObj, "densitygpcm3", bodyGroupMass * 1.0e3 / (bodyGroupVolume * 1.0e-3) )

    # Using parallel axis theorem to compute the moment of inertia through the CoG
    # of the full body comprised of multiple shapes
    bodyGroupMoI = 0
    for MoIIndex in range(len(subBodyMoIThroughCoGNormalToMovementPlaneList)):
        if Debug:
            Mess("Sub-Body MoI: "+str(subBodyMoIThroughCoGNormalToMovementPlaneList[MoIIndex]))
        distanceBetweenAxes = (bodyCentreOfGravityMovementPlane - subBodyCentreOfGravityList[MoIIndex]).Length
        bodyGroupMoI += subBodyMoIThroughCoGNormalToMovementPlaneList[MoIIndex] + massList[MoIIndex] * (distanceBetweenAxes ** 2)
    setattr(bodyGroupObj, "momentOfInertia", bodyGroupMoI)

    if Debug:
        Mess("Body Total Mass [kg]:  "+str(bodyGroupMass))
        MessNoLF("Body Centre of Gravity [mm]:  ")
        PrintVec(bodyGroupCoG)
        Mess("Body moment of inertia [kg mm^2):  "+str(bodyGroupMoI))
        Mess("")
#  -------------------------------------------------------------------------
def findBodyPhi(bodyObj):
    """ Phi defined by the longest vector from CoG to a Joint
       The first body is ALWAYS the ground body
       and hence cannot be rotated away from 0.0 """

    if bodyObj.bodyIndex == 0:
        return 0.0

    maxNorm = 0.0
    largest = 0
    relCoG = CAD.Vector(0.0, 0.0, 0.0)
    for JointNumber in range(len(bodyObj.jointIndexList)):
        relCoG = bodyObj.PointPlacementList[JointNumber].Base - bodyObj.worldCoG
        if maxNorm < relCoG.Length:
            maxNorm = relCoG.Length
            largest = JointNumber
    # Handle the case where it is vertical
    if abs(relCoG[0]) < 1e-6:
        if relCoG[1] > 0.0:
            return np.pi / 2.0
        else:
            return np.pi
    else:
        relCoG = bodyObj.PointPlacementList[largest].Base - bodyObj.worldCoG
        return np.arctan2(relCoG[1], relCoG[0])
#  -------------------------------------------------------------------------
def translateToPlanarMechSimJointNames(allObjects, joint):
    """ Translate all the joint names into PlanarMechSim naming conventions """

    # Handle the joint to ground
    if hasattr(joint, "ObjectToGround"):
        setattr(joint, "SimJoint", "GroundedJoint")
        return

    # Double-check that the joint has a type - otherwise how did we get here?
    if hasattr(joint, "JointType"):

        # Joints which are still buggy
        if joint.JointType == "RackPinion":
            CAD.Console.PrintError("PlanarMechSim cannot simulate a Rack and Pinion joint yet\n")
            return

        # Joints currently not supported
        elif joint.JointType == "Driven-Rotation":
            CAD.Console.PrintError("PlanarMechSim cannot currently simulate a Driven-Rotation joint\n")
            return

        elif joint.JointType == "Driven-Translation":
            CAD.Console.PrintError("PlanarMechSim cannot currently simulate a Driven-Translation joint\n")
            return

        elif joint.JointType == "Angle":
            CAD.Console.PrintError("PlanarMechSim cannot currently simulate an Angle joint\n")
            return

        elif joint.JointType == "Gears":
            CAD.Console.PrintError("PlanarMechSim cannot currently simulate a Gears joint\n")
            return

        elif joint.JointType == "Belt":
            CAD.Console.PrintError("PlanarMechSim cannot currently simulate a Belt joint\n")
            return

        # Joints with names needing translation between Nikravesh and FreeCAD nomenclature
        elif joint.JointType == "Distance":
            # Set it temporarily as Rev-Rev and change to Trans-Rev later
            # if applicable
            setattr(joint, "SimJoint", "Revolute-Revolute")
            return

        elif joint.JointType == "Slider":
            setattr(joint, "SimJoint", "Translation")
            return

        # Joints which do not make sense in connection with motion in a plane
        elif joint.JointType == "Cylindrical":
            CAD.Console.PrintError("PlanarMechSim cannot simulate a Cylindrical joint\n")
            CAD.Console.PrintError("It makes no sense if motion is limited to be in a plane\n")
            return

        elif joint.JointType == "Parallel":
            CAD.Console.PrintError("PlanarMechSim cannot simulate a Parallel joint\n")
            CAD.Console.PrintError("All motion is already limited to be in a single plane\n")
            return

        elif joint.JointType == "Screw":
            CAD.Console.PrintError("PlanarMechSim cannot simulate a Screw joint\n")
            CAD.Console.PrintError("The translation axis and the rotation axis are parallel\n")
            return

        elif joint.JointType == "Perpendicular":
            CAD.Console.PrintError("PlanarMechSim cannot simulate a Perpendicular joint\n")
            CAD.Console.PrintError("It is not compatible with motion in a plane\n")
            return

        # Joints which are handled as-is
        elif joint.JointType == "Revolute":
            setattr(joint, "SimJoint", "Revolute")
            return

        # Check if a fixed joint just glues the body together
        # i.e. BOTH fixed joint halves are inside two sub-bodies of the SAME body
        elif joint.JointType == "Fixed":
            foundInternalJoint = False
            jointHEADname = joint.Reference1[0].Name
            jointTAILname = joint.Reference2[0].Name
            # Run through all the SimBodies
            # And find any one which has both parts of a fixed joint in the same body
            for SimBody in allObjects.Document.Objects:
                if hasattr(SimBody, "TypeId") and SimBody.TypeId == 'App::LinkGroup':
                    foundHEAD = False
                    foundTAIL = False
                    for element in SimBody.ElementList:
                        if element.Name == jointHEADname:
                            foundHEAD = True
                        if element.Name == jointTAILname:
                            foundTAIL = True
                    if foundHEAD and foundTAIL:
                        foundInternalJoint = True

            if foundInternalJoint:
                setattr(joint, "SimJoint", "Internal")
            else:
                setattr(joint, "SimJoint", "Fixed")
            return

        CAD.Console.PrintError("Somehow this is a joint that PlanarMechSim is not aware of\n")
    else:
        CAD.Console.PrintError("Somehow this joint has no Type definition\n")
#  -------------------------------------------------------------------------
def addObjectProperty(newobject, newproperty, initVal, newtype, *args):
    """Call addObjectProperty on the object if it does not yet exist"""

    # Only add it if the property does not exist there already
    added = False
    if newproperty not in newobject.PropertiesList:
        added = newobject.addProperty(newtype, newproperty, *args)
    if added:
        setattr(newobject, newproperty, initVal)
        return True
    else:
        return False
#  -------------------------------------------------------------------------
def CalculateRotationMatrix(phi):
    """ This function computes the rotational transformation matrix
    in the format of a 2X2 NumPy array"""

    return np.array([[np.cos(phi), -np.sin(phi)],
                     [np.sin(phi),  np.cos(phi)]])
#  -------------------------------------------------------------------------
def Mess(string):
    CAD.Console.PrintMessage(str(string)+"\n")
#  -------------------------------------------------------------------------
def MessNoLF(string):
    CAD.Console.PrintMessage(str(string))
#  -------------------------------------------------------------------------
def PrintVec(vec):
    CAD.Console.PrintMessage("[" + str(Round(vec.x)) + ":" + str(Round(vec.y)) + ":" + str(Round(vec.z)) + "]\n")
#  -------------------------------------------------------------------------
def PrintNp3D(arr):

    for x in arr:
        for y in x:
            s = "[ "
            for z in y:
                ss = str(Round(z))+"                 "
                s = s + ss[:12]
            s = s + " ]"
            CAD.Console.PrintMessage(s+"\n")
        CAD.Console.PrintMessage("\n")
#  -------------------------------------------------------------------------
def PrintNp2D(arr):

    for x in arr:
        s = "[ "
        for y in x:
            ss = str(Round(y))+"                 "
            s = s + ss[:12]
        s = s + " ]"
        CAD.Console.PrintMessage(s+"\n")
#  -------------------------------------------------------------------------
def PrintNp1D(LF, arr):

    s = "[ "
    for y in arr:
        ss = str(Round(y))+"                 "
        s = s + ss[:12]
    s = s + " ]"
    if LF:
        CAD.Console.PrintMessage(s+"\n")
    else:
        CAD.Console.PrintMessage(s+" ")
#  -------------------------------------------------------------------------
def PrintNp1Ddeg(LF, arr):

    s = "[ "
    for y in arr:
        ss = str(Round(y*180.0/math.pi))+"                 "
        s = s + ss[:12]
    s = s + " ]"
    if LF:
        CAD.Console.PrintMessage(s+"\n")
    else:
        CAD.Console.PrintMessage(s+" ")
#  -------------------------------------------------------------------------
def Round(num):

    if num >= 0.0:
        return int((100.0 * num + 0.5))/100.0
    else:
        return int((100.0 * num - 0.5))/100.0
#  -------------------------------------------------------------------------
def Rot90NumPy(a):

    aa = a.copy()
    bb = np.zeros((2,))
    bb[0], bb[1] = -aa[1], aa[0]
    return bb
#  -------------------------------------------------------------------------
def CADVecToNumPy(CADVec):

    a = np.zeros((2,))
    a[0] = CADVec.x
    a[1] = CADVec.y
    return a
#  -------------------------------------------------------------------------
