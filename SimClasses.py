# ********************************************************************************
# *                                                                              *
# *   This program is free software; you can redistribute it and/or modify       *
# *   it under the terms of the GNU General Public License v3.0 only             *
# *   as published by the Free Software Foundation                               *
# *   for detail see the LICENCE text file.                                      *
# *                                                                              *
# *   This program is distributed in the hope that it will be useful,            *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of             *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                       *
# *   See the GNU Lesser General Public License for more details.                *
# *                                                                              *
# *   You should have received a copy of the GNU General Public v3.0             *
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
# *                   An early version of Nikra-DAP was written by:              *
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
import FreeCADGui as CADGui
import SimTools as ST

# =============================================================================
class SimGlobalClass:
    """The Sim analysis simGlobal class"""
    #  -------------------------------------------------------------------------
    def __init__(self, allObjects):
        """Initialise on entry"""

        allObjects.Proxy = self

        self.addPropertiesToObject(allObjects)
        self.populateJointProperties(allObjects)
    #  -------------------------------------------------------------------------
    def onDocumentRestored(self, allObjects):

        self.addPropertiesToObject(allObjects)
    #  -------------------------------------------------------------------------
    def addPropertiesToObject(self, allObjects):
        """Run by '__init__'  and 'onDocumentRestored' to initialise the Sim system parameters"""

        # ----------------------------------------
        # Add properties to the simGlobal object
        ST.addObjectProperty(allObjects, "movementPlaneNormal", CAD.Vector(0, 0, 1),"App::PropertyVector", "", "Defines the movement plane in this PlanarMechSim run")
        ST.addObjectProperty(allObjects, "gravityVector",CAD.Vector(0.0, -9810.0, 0.0),"App::PropertyVector", "", "Gravitational acceleration Components")
        ST.addObjectProperty(allObjects, "gravityValid",True,"App::PropertyBool",   "", "Flag to verify that the gravity Vector is applicable")
        ST.addObjectProperty(allObjects, "SimResultsValid",False,"App::PropertyBool", "", "Flag that the calculation has been performed successfully")

        # ----------------------------------------
        # Add properties to joints in the joint group which was created by Assembly workbench
        self.jointGroup = CAD.ActiveDocument.findObjects(Name="^Joints$")[0].Group

        JointNumber = -1
        for joint in self.jointGroup:
            # Tag each joint with an index number
            JointNumber += 1
            # Add these two properties to this joint (for all the joints)
            ST.addObjectProperty(joint, "JointNumber", JointNumber, "App::PropertyInteger", "Bodies and constraints", "Index of the joint")
            # Start out with an undefined type - which will be changed if the joint has a valid joint type
            ST.addObjectProperty(joint, "SimJoint", "Undefined", "App::PropertyString", "Bodies and constraints", "Type of joint as seen by the simulator")

            # Add these properties to only joints having a valid PlanarMechSim joint type
            if hasattr(joint, "JointType") and ST.JOINT_TYPE_DICTIONARY[joint.JointType] <= ST.MAXNUMJOINTTYPES:
                # Transfer a copy of the JointType property to the SimJoint property
                setattr(joint, "SimJoint" , joint.JointType)

                # Add these required properties to each of the joints we will handle
                ST.addObjectProperty(joint, "Bi", -1, "App::PropertyInteger", "JointPoints", "The index of the body containing the head of the joint")
                ST.addObjectProperty(joint, "Pi", -1, "App::PropertyInteger", "JointPoints", "The index of the head point in the body")
                ST.addObjectProperty(joint, "Bj", -1, "App::PropertyInteger", "JointPoints", "The index of the body containing the tail of the joint")
                ST.addObjectProperty(joint, "Pj", -1, "App::PropertyInteger", "JointPoints", "The index of the tail point in the body")

                ST.addObjectProperty(joint, "bodyHeadUnit", CAD.Vector(), "App::PropertyVector", "JointPoints", "The unit vector at the head of the joint")
                ST.addObjectProperty(joint, "bodyTailUnit", CAD.Vector(), "App::PropertyVector", "JointPoints", "The unit vector at the tail of the joint")
                ST.addObjectProperty(joint, "headInPlane", False, "App::PropertyBool", "JointPoints", "If the head unit vector lies in the x-y plane")
                ST.addObjectProperty(joint, "tailInPlane", False, "App::PropertyBool", "JointPoints", "If the tail unit vector lies in the x-y plane")

                ST.addObjectProperty(joint, "nBodies", -1, "App::PropertyInteger", "Bodies and constraints", "Number of moving bodies involved")
                ST.addObjectProperty(joint, "mConstraints", -1, "App::PropertyInteger", "Bodies and constraints", "Number of rows (constraints)")
                ST.addObjectProperty(joint, "fixDof", False, "App::PropertyBool", "Bodies and constraints", "Fix the Degrees of Freedom")
                ST.addObjectProperty(joint, "FunctType", -1, "App::PropertyInteger", "Function Driver", "Analytical function type")
                ST.addObjectProperty(joint, "rowStart", -1, "App::PropertyInteger", "Bodies and constraints", "Row starting index")
                ST.addObjectProperty(joint, "rowEnd", -1, "App::PropertyInteger", "Bodies and constraints", "Row ending index")

                ST.addObjectProperty(joint, "lengthLink", 1.0, "App::PropertyFloat", "", "Link length")
                ST.addObjectProperty(joint, "phi0", 0.0, "App::PropertyFloat", "", "Original rotational angle")
                ST.addObjectProperty(joint, "x0", 0.0, "App::PropertyFloat", "", "Original x position")

        # ----------------------------------------
        # Add properties to all the linked bodies
        bodyIndex = -1
        for bodyGroup in allObjects.Document.Objects:
            if hasattr(bodyGroup, "TypeId") and bodyGroup.TypeId == 'App::LinkGroup':
                # Tag each body with its unique number
                bodyIndex += 1
                bodyGroup.Label = "SimBody"+str(bodyIndex)
                ST.addObjectProperty(bodyGroup, "bodyIndex", bodyIndex, "App::PropertyInteger", "SimBody", "Centre of gravity")
                ST.addObjectProperty(bodyGroup, "worldCoG", CAD.Vector(), "App::PropertyVector", "SimBody", "Centre of gravity")
                ST.addObjectProperty(bodyGroup, "worldDot", CAD.Vector(), "App::PropertyVector", "X Y Z Phi", "Time derivative of x y z")
                ST.addObjectProperty(bodyGroup, "phi", 0.0, "App::PropertyFloat", "X Y Z Phi", "Angular velocity of phi")
                ST.addObjectProperty(bodyGroup, "phiDot", 0.0, "App::PropertyFloat", "X Y Z Phi", "Angular velocity of phi")

                ST.addObjectProperty(bodyGroup, "densitygpcm3", 1.0, "App::PropertyFloat", "SimBody", "Density in g/cm3")
                ST.addObjectProperty(bodyGroup, "densitykgpm3", 1.0, "App::PropertyFloat", "SimBody", "Density in kg/m3")

                ST.addObjectProperty(bodyGroup, "volumecm3", 1.0, "App::PropertyFloat", "SimBody", "Volume in cm3")
                ST.addObjectProperty(bodyGroup, "volumem3", 1.0, "App::PropertyFloat", "SimBody", "Volume in m3")
                ST.addObjectProperty(bodyGroup, "massg", 1.0, "App::PropertyFloat", "SimBody", "Mass in g")
                ST.addObjectProperty(bodyGroup, "masskg", 1.0, "App::PropertyFloat", "SimBody", "Mass in kg")
                ST.addObjectProperty(bodyGroup, "momentOfInertia", 0.1, "App::PropertyFloat", "SimBody", "Moment of inertia in kg mm^2")

                # Add space for all the joints in the body to the SimBody
                ST.addObjectProperty(bodyGroup, "jointNameList", [], "App::PropertyStringList", "JointPoints", "The name of the joint object")
                ST.addObjectProperty(bodyGroup, "jointTypeList", [], "App::PropertyStringList", "JointPoints", "The type of joint (Rev, Trans etc)")
                ST.addObjectProperty(bodyGroup, "jointIndexList", [], "App::PropertyIntegerList", "JointPoints", "The type of joint (Rev, Trans etc)")
                ST.addObjectProperty(bodyGroup, "PointPlacementList", [], "App::PropertyPlacementList", "JointPoints", "Placement of the joint point")

                # Tentatively calculate the CoG etc
                ST.updateCoGMoI(bodyGroup)
        # Next bodyGroup

        # ----------------------------------------
        # Add properties to the forces

        # For now, we will only add a gravity force
        self.forceList = CAD.ActiveDocument.findObjects(Name="^SimForce")
        if self.forceList == []:
            CAD.ActiveDocument.addObject("Part::FeaturePython", "SimForce")
            self.forceList = CAD.ActiveDocument.findObjects(Name="^SimForce")

        forceIndex = -1
        for forceObj in self.forceList:
            if hasattr(forceObj, "Name") and forceObj.Name == "SimForce":
                forceIndex += 1
                ST.addObjectProperty(forceObj, "forceIndex", forceIndex, "App::PropertyInteger", "", "Index of the forceObject")
                ST.addObjectProperty(forceObj, "forceType", "Gravity", "App::PropertyString", "", "Type of the actuator/force")

                ST.addObjectProperty(forceObj, "bodyForceHeadName", "", "App::PropertyString", "Bodies", "Name of the head body")
                ST.addObjectProperty(forceObj, "bodyForceHeadLabel", "", "App::PropertyString", "Bodies", "Label of the head body")
                ST.addObjectProperty(forceObj, "bodyForceHeadIndex", -1, "App::PropertyInteger", "Bodies", "Index of the head body in the NumPy array")
                
                ST.addObjectProperty(forceObj, "pointForceHeadName", "", "App::PropertyString", "Points", "Name of the first point of the force")
                ST.addObjectProperty(forceObj, "pointForceHeadLabel", "", "App::PropertyString", "Points", "Label of the first point of the force")
                ST.addObjectProperty(forceObj, "pointForceHeadIndex", -1, "App::PropertyInteger", "Points", "Index of the first point of the force in the NumPy array")
                
                ST.addObjectProperty(forceObj, "bodyForceTailName", "", "App::PropertyString", "Bodies", "Name of the tail body")
                ST.addObjectProperty(forceObj, "bodyForceTailLabel", "", "App::PropertyString", "Bodies", "Label of the tail body")
                ST.addObjectProperty(forceObj, "bodyForceTailIndex", -1, "App::PropertyInteger", "Bodies", "Index of the tail body in the NumPy array")
                
                ST.addObjectProperty(forceObj, "pointForceTailName", "", "App::PropertyString", "Points", "Name of the second point of the force")
                ST.addObjectProperty(forceObj, "pointForceTailLabel", "", "App::PropertyString", "Points", "Label of the second point of the force")
                ST.addObjectProperty(forceObj, "pointForceTailIndex", 0, "App::PropertyInteger", "Points", "Index of the second point of the force in the NumPy array")
                
                ST.addObjectProperty(forceObj, "Stiffness", 0.0, "App::PropertyFloat", "Values", "Spring Stiffness")
                ST.addObjectProperty(forceObj, "LengthAngle0", 0.0, "App::PropertyFloat", "Values", "Un-deformed Length/Angle")
                ST.addObjectProperty(forceObj, "DampingCoeff", 0.0, "App::PropertyFloat", "Values", "Damping coefficient")
                ST.addObjectProperty(forceObj, "constLocalForce", CAD.Vector(), "App::PropertyVector", "Values", "Constant force in local frame")
                ST.addObjectProperty(forceObj, "constWorldForce", CAD.Vector(), "App::PropertyVector", "Values", "Constant force in x-y frame")
                ST.addObjectProperty(forceObj, "constTorque", 0.0, "App::PropertyFloat", "Values", "Constant torque in x-y frame")
        # Next forceObj
        self.numForces = forceIndex

    #  -------------------------------------------------------------------------
    def populateJointProperties(self, allObjects):

        # Empty the four lists associated with each of the SimBodies
        for SimBody in allObjects.Document.Objects:
            if hasattr(SimBody, "TypeId") and SimBody.TypeId == 'App::LinkGroup':
                # Initialise parameters
                SimBody.jointIndexList = []
                SimBody.jointTypeList = []
                SimBody.jointNameList = []
                SimBody.PointPlacementList = []

        # We populate the properties JOINT by JOINT
        JointNumber = -1
        for joint in self.jointGroup:
            JointNumber += 1
            #if hasattr(joint, "Placement1"):
            #    ST.MessNoLF("Placement1: "+joint.Name)
            #    ST.MessNoLF(" - ")
            #    ST.Mess(joint.Placement1)
            #if hasattr(joint, "Placement2"):
            #    ST.MessNoLF("Placement2: "+joint.Name)
            #    ST.MessNoLF(" - ")
            #    ST.Mess(joint.Placement2)

            # Set the SimJoint property with a new name where applicable
            # e.g. Fixed joints which are internal to a body become internal joints
            ST.translateToPlanarMechSimJointNames(allObjects, joint)

            # Now only consider joints for which PlanarMechSim has code to handle them
            if hasattr(joint, "SimJoint") and ST.JOINT_TYPE_DICTIONARY[joint.SimJoint] <= ST.MAXNUMJOINTTYPES:
                # Initialise unit vectors to zero
                joint.bodyHeadUnit = CAD.Vector()
                joint.bodyTailUnit = CAD.Vector()

                # We will call the first one we have found the head and the second one the tail
                Head = True

                # We now search through all the SimBodies for references to this joint
                SimBodyIndex = -1
                for SimBody in allObjects.Document.Objects:
                    # Only look at the SimBody objects
                    if hasattr(SimBody, "TypeId") and SimBody.TypeId == 'App::LinkGroup':
                        SimBodyIndex += 1
                        # Find if this joint is present inside a sub-body
                        # in the element list of this SimBody
                        for subBody in SimBody.ElementList:
                            foundThisJoint = False
                            # Start out with null placement and unit vector
                            thisPlacement = CAD.Placement()
                            if joint.Reference1[0].Name == subBody.Name:
                                thisPlacement = joint.Placement1
                                foundThisJoint = True
                            elif joint.Reference2[0].Name == subBody.Name:
                                thisPlacement = joint.Placement2
                                foundThisJoint = True

                            # Found this joint in this SimBody
                            # So record that in the SimBody's joint lists
                            if foundThisJoint:
                                # add the Joint Index
                                t = SimBody.jointIndexList
                                t.append(JointNumber)
                                SimBody.jointIndexList = t

                                # add the Joint Type
                                t = SimBody.jointTypeList
                                t.append(joint.SimJoint)
                                SimBody.jointTypeList = t

                                # add the Joint Name
                                t = SimBody.jointNameList
                                t.append(joint.Name)
                                SimBody.jointNameList = t

                                # and apply its placement to the joint placement
                                # to calculate the world placement of the joint point
                                body = CAD.ActiveDocument.findObjects(Name="^" + subBody.Name + "$")[0]

                                placed = body.Placement * thisPlacement
                                t = SimBody.PointPlacementList
                                t.append(placed)
                                SimBody.PointPlacementList = t

                                unitVec = placed.Rotation.multVec(CAD.Vector(0.0, 0.0, 1.0)).normalize()

                                # Store the values of the joint and point object into the SimBody
                                # currently the last item in the jointIndexList
                                # Do this differently for the Head and the Tail
                                if Head:
                                    joint.Bi = SimBodyIndex
                                    joint.Pi = len(SimBody.jointIndexList) - 1
                                    joint.bodyHeadUnit = unitVec
                                    joint.headInPlane = abs(unitVec.z) < 0.1
                                    Head = False
                                else:
                                    joint.Bj = SimBodyIndex
                                    joint.Pj = len(SimBody.jointIndexList) - 1
                                    joint.bodyTailUnit = unitVec
                                    joint.tailInPlane = abs(unitVec.z) < 0.1
                                    # Check (and alter) if we are actually a Translation-Revolute joint
                                    if joint.SimJoint == "Revolute-Revolute":
                                        if joint.headInPlane or joint.tailInPlane:
                                            joint.SimJoint = "Translation-Revolute"
                            # end of if foundThisJoint
                        # Next subBody
                # Next SimBody
            # end of if it has SimJoint attribute
        # Next Joint
# =============================================================================
class SimSolverClass:
    #  -------------------------------------------------------------------------
    def __init__(self, solverObject):
        """Initialise on instantiation of a new Sim solver object"""

        solverObject.Proxy = self

        self.addPropertiesToObject(solverObject)
    #  -------------------------------------------------------------------------
    def onDocumentRestored(self, solverObject):
        self.addPropertiesToObject(solverObject)
    #  -------------------------------------------------------------------------
    def addPropertiesToObject(self, solverObject):
        """Initialise all the properties of the solver object"""

        ST.addObjectProperty(solverObject, "FileName",        "",    "App::PropertyString",     "", "FileName to save data under")
        ST.addObjectProperty(solverObject, "Directory",       "",    "App::PropertyString",     "", "Directory to save data")
        ST.addObjectProperty(solverObject, "Accuracy",        3.0,   "App::PropertyFloat",      "", "Length of the Analysis")
        ST.addObjectProperty(solverObject, "TimeLength",      10.0,  "App::PropertyFloat",      "", "Length of the Analysis")
        ST.addObjectProperty(solverObject, "SolverType",      "RK45","App::PropertyString",     "", "Type of solver in LAPACK")
        ST.addObjectProperty(solverObject, "DeltaTime",       0.01,  "App::PropertyFloat",      "", "Length of time steps")
        ST.addObjectProperty(solverObject, "BodyNames",       [],    "App::PropertyStringList", "", "List of Body Names")
        #  -------------------------------------------------------------------------
# =============================================================================
