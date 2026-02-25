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

import os
import time
import numpy as np
from scipy.integrate import solve_ivp
import math

import SimTools as ST

Debug = False
# =============================================================================
class SimMainC:
    """Instantiated when the 'solve' button is clicked in the task panel"""
    #  -------------------------------------------------------------------------
    def __init__(self, simEnd, simDelta, Accuracy, correctInitial):

        # Make the parameters passed via the __init__ function
        # global to the class
        self.simEnd = simEnd
        self.simDelta = simDelta
        self.correctInitial = correctInitial

        # Dictionary of the pointers for Dynamic calling of the Acceleration functions
        self.dictAccelerationFunctions = {
            0: self.Revolute_gamma,
            1: self.Fixed_gamma,
            2: self.Translation_gamma,
            3: self.Revolute_Revolute_gamma,
            4: self.Translation_Revolute_gamma,
            5: self.Disc_gamma,
        }
        # Dictionary of the pointers for Dynamic calling of the constraint functions
        self.dictconstraintFunctions = {
            0: self.Revolute_constraint,
            1: self.Fixed_constraint,
            2: self.Translation_constraint,
            3: self.Revolute_Revolute_constraint,
            4: self.Translation_Revolute_constraint,
            5: self.Disc_constraint,
        }

        # Dictionary of the pointers for Dynamic calling of the Jacobian functions
        self.dictJacobianFunctions = {
            0: self.Revolute_Jacobian,
            1: self.Fixed_Jacobian,
            2: self.Translation_Jacobian,
            3: self.Revolute_Revolute_Jacobian,
            4: self.Translation_Revolute_Jacobian,
            5: self.Disc_Jacobian,
        }

        # Store the required accuracy figures
        self.relativeTolerance = 10 ** (-Accuracy)
        self.absoluteTolerance = 10 ** (-Accuracy-4)

        # Counter of function evaluations
        self.Counter = 0

        # We get the objects and set global constants
        # Main container
        self.simGlobalObj = CAD.ActiveDocument.findObjects(Name="^SimGlobal$")[0]

        # Solver
        self.solverObj = CAD.ActiveDocument.findObjects(Name="^SimSolver$")[0]

        # Bodies
        self.bodyGroup = CAD.ActiveDocument.findObjects(Name="^LinkGroup")
        self.numBodies = len(self.bodyGroup)
        self.numMovBodiesx3 = (self.numBodies-1) * 3

        # Joints
        self.jointGroup = CAD.ActiveDocument.findObjects(Name="^Joints$")[0].Group
        self.numJoints = len(self.jointGroup)

        # Forces
        self.forceList = CAD.ActiveDocument.findObjects(Name="^SimForce")
        self.numForces = len(self.forceList)

        # Set a variable to flag whether we have reached the end error-free
        # It will be available to SimSolver as an instance variable
        self.initialised = False

        # Get the plane normal rotation matrix from SimGlobal
        # This will rotate all the coordinates in the model, to be in the X-Y plane
        self.xyzToXYRotation = CAD.Rotation(CAD.Vector(0.0, 0.0, 1.0), self.simGlobalObj.movementPlaneNormal)

        # Find the maximum number of points in any of the bodies
        # We will need this so we can initialise large enough NumPy arrays
        maxNumPoints = 0
        for bodyObj in self.bodyGroup:
            if maxNumPoints < len(bodyObj.jointIndexList):
                maxNumPoints = len(bodyObj.jointIndexList)

        # ********************************************************************************

        # Initialise the size of all the NumPy arrays and fill with zeros

        # Parameters for each body
        self.NPMasskg = np.zeros((self.numBodies,), dtype=np.float64)
        self.NPmomentOfInertia = np.zeros((self.numBodies,), dtype=np.float64)
        self.NPWeight = np.zeros((self.numBodies, 2,), dtype=np.float64)
        self.NPsumForces = np.zeros((self.numBodies, 2,), dtype=np.float64)
        self.NPsumMoments = np.zeros((self.numBodies,), dtype=np.float64)
        self.NPbody_r = np.zeros((self.numBodies, 2,), dtype=np.float64)
        self.NPbody_r90 = np.zeros((self.numBodies, 2,), dtype=np.float64)
        self.NPbody_drdt = np.zeros((self.numBodies, 2,), dtype=np.float64)
        self.NPbody_drdt90 = np.zeros((self.numBodies, 2,), dtype=np.float64)
        self.NPbody_d2rdt2 = np.zeros((self.numBodies, 2,), dtype=np.float64)
        self.NPbody_phi = np.zeros((self.numBodies,), dtype=np.float64)
        self.NPbody_dphidt = np.zeros((self.numBodies,), dtype=np.float64)
        self.NPbody_d2phidt2 = np.zeros((self.numBodies,), dtype=np.float64)
        self.NPRotMatrixPhi = np.zeros((self.numBodies, 2, 2,), dtype=np.float64)
        self.NPnumJointPointsInBody = np.zeros((self.numBodies,), dtype=np.integer)

        self.NPphi0 = np.zeros(self.numJoints, dtype=np.float64)
        self.NPd0 = np.zeros((self.numJoints, 2), dtype=np.float64)

        self.NPpotEnergyZeroPoint = np.zeros((self.numBodies,), dtype=np.float64)

        # Parameters for each point within a body, for each body
        # Vector from CoG to the point in body local coordinates
        self.NPpoint_sXiEta = np.zeros((self.numBodies, maxNumPoints, 2,), dtype=np.float64)
        # Vector from CoG to the point in world coordinates
        self.NPpoint_s = np.zeros((self.numBodies, maxNumPoints, 2,), dtype=np.float64)
        self.NPpoint_s90 = np.zeros((self.numBodies, maxNumPoints, 2,), dtype=np.float64)
        self.NPpoint_dsdt = np.zeros((self.numBodies, maxNumPoints, 2,), dtype=np.float64)
        # Vector from the origin to the point in world coordinates
        self.NPpoint_r = np.zeros((self.numBodies, maxNumPoints, 2,), dtype=np.float64)
        self.NPpoint_r90 = np.zeros((self.numBodies, maxNumPoints, 2,), dtype=np.float64)
        self.NPpoint_drdt = np.zeros((self.numBodies, maxNumPoints, 2,), dtype=np.float64)

        # Unit vector (if applicable) of the first body of the joint in body local coordinates
        self.NPunit_i_XiEta = np.zeros((self.numJoints, 2,), dtype=np.float64)
        # Unit vector (if applicable) of the first body of the joint in world coordinates
        self.NPunit_i = np.zeros((self.numJoints, 2,), dtype=np.float64)
        self.NPunit_i90 = np.zeros((self.numJoints, 2,), dtype=np.float64)
        self.NPunit_i_vel = np.zeros((self.numJoints, 2,), dtype=np.float64)
        self.NPunit_i_vel90 = np.zeros((self.numJoints, 2,), dtype=np.float64)

        # Second unit vector (if applicable) of the second body of the joint in body local coordinates
        self.NPunit_j_XiEta = np.zeros((self.numJoints, 2,), dtype=np.float64)
        # second unit vector (if applicable) of the second body of the joint in world coordinates
        self.NPunit_j = np.zeros((self.numJoints, 2,), dtype=np.float64)
        self.NPunit_j90 = np.zeros((self.numJoints, 2,), dtype=np.float64)
        self.NPunit_j_vel = np.zeros((self.numJoints, 2,), dtype=np.float64)
        self.NPunit_j_vel90 = np.zeros((self.numJoints, 2,), dtype=np.float64)

        self.NPforceArray = np.zeros((self.numMovBodiesx3,), dtype=np.float64)

        # Transfer all the 3D stuff into the NumPy arrays
        bodyIndex = -1
        for bodyObj in self.bodyGroup:
            bodyIndex += 1
            self.NPnumJointPointsInBody[bodyIndex] = len(bodyObj.jointIndexList)

            # Re-Calculate the body CoG and MoI
            ST.updateCoGMoI(bodyObj)

            # All Mass and moment of inertia stuff
            self.NPMasskg[bodyIndex] = bodyObj.masskg
            self.NPmomentOfInertia[bodyIndex] = bodyObj.momentOfInertia
            npVec = ST.CADVecToNumPy(self.simGlobalObj.gravityVector * bodyObj.masskg)
            self.NPWeight[bodyIndex] = npVec

            # The coordinates of the CoG in world coordinates
            # are the world coordinates of the body
            # All points in the body are relative to this point

            # World
            CoG = bodyObj.worldCoG
            npCoG = ST.CADVecToNumPy(CoG)
            self.NPbody_r[bodyIndex, 0:2] = npCoG
            self.NPbody_r90[bodyIndex, 0:2] = ST.Rot90NumPy(npCoG)

            # WorldDot
            npvec = ST.CADVecToNumPy(bodyObj.worldDot)
            self.NPbody_drdt[bodyIndex, 0:2] = npvec
            self.NPbody_drdt90[bodyIndex, 0:2] = ST.Rot90NumPy(npvec)

            # WorldDotDot
            self.NPbody_d2rdt2[bodyIndex, 0:2] = np.zeros((1, 2))

            # The angle phi which the body makes with the x-axis
            self.NPbody_phi[bodyIndex] = ST.findBodyPhi(bodyObj)

            # The phiDot axis vector is by definition perpendicular to the movement plane,
            # so we don't have to do any rotating from the phiDot value set in bodyObj
            self.NPbody_dphidt[bodyIndex] = bodyObj.phiDot

            # We will now calculate the rotation matrix
            # and use it to find the local coordinates of the points
            self.NPRotMatrixPhi[bodyIndex] = ST.CalculateRotationMatrix(self.NPbody_phi[bodyIndex])

            for pointIndex in range(len(bodyObj.jointIndexList)):
                # Point Local - vector from body CoG to the point, in body local (LCS) coordinates
                npVec = ST.CADVecToNumPy(bodyObj.PointPlacementList[pointIndex].Base)
                self.NPpoint_r[bodyIndex, pointIndex] = npVec
                self.NPpoint_r90[bodyIndex, pointIndex] = ST.Rot90NumPy(npVec)

                # Point Vector - vector from body CoG to the point in world coordinates
                npVec -= npCoG
                self.NPpoint_s[bodyIndex, pointIndex, 0:2] = npVec
                self.NPpoint_s90[bodyIndex][pointIndex] = ST.Rot90NumPy(npVec)

                # Local coordinates of the point in Eta/Xi frame
                self.NPpoint_sXiEta[bodyIndex, pointIndex, 0:2] = npVec @ self.NPRotMatrixPhi[bodyIndex]

                # Point Vector Dot
                self.NPpoint_dsdt[bodyIndex][pointIndex] = np.zeros((1, 2))

                # Point World Dot
                self.NPpoint_drdt[bodyIndex][pointIndex] = np.zeros((1, 2))

            # Next pointIndex
        # Next bodyObj

        # Print out what we have populated for debugging
        if Debug:
            ST.Mess("Body Labels -- Body Names")
            for bodyObj in self.bodyGroup:
                ST.Mess(bodyObj.Label+" - "+bodyObj.Name)
            ST.Mess("Mass: [g]")
            ST.PrintNp1D(True, self.NPMasskg * 1.0e3)
            ST.Mess("")
            ST.Mess("Mass: [kg]")
            ST.PrintNp1D(True, self.NPMasskg)
            ST.Mess("")
            ST.Mess("Moment of Inertia: [kg mm^2]")
            ST.PrintNp1D(True, self.NPmomentOfInertia)
            ST.Mess("")
            ST.Mess("Weight Vector: [kg mm /s^2 = mN]")
            ST.PrintNp2D(self.NPWeight)
            ST.Mess("")
            ST.Mess("Sum Forces: [kg.mm/s^2 = mN]")
            ST.PrintNp2D(self.NPsumForces)
            ST.Mess("")
            ST.Mess("Sum Moments: [N.mm]")
            ST.PrintNp1D(True, self.NPsumMoments)
            ST.Mess("")
            ST.Mess("World [vector r]: [mm relative to CoG]")
            ST.PrintNp2D(self.NPbody_r)
            ST.Mess("")
            ST.Mess("WorldDot [dr/dt]: [mm/s]")
            ST.PrintNp2D(self.NPbody_drdt)
            ST.Mess("")
            ST.Mess("phi: [deg]")
            ST.PrintNp1Ddeg(True, self.NPbody_phi)
            ST.Mess("")
            ST.Mess("phiDot [dphi/dt]: [deg/sec]")
            ST.PrintNp1Ddeg(True, self.NPbody_dphidt)
            ST.Mess("")
            ST.Mess("Rotation Matrix:")
            ST.PrintNp3D(self.NPRotMatrixPhi)
            ST.Mess("")
            ST.Mess("Number of Joint points in body:")
            ST.PrintNp1D(True, self.NPnumJointPointsInBody)
            ST.Mess("")
            ST.Mess("PointLocal [s(Xi) s(Eta)]: [mm]")
            ST.PrintNp3D(self.NPpoint_sXiEta)
            ST.Mess("")
            ST.Mess("Vector from CoG to point in World coordinates [s-point]: [mm]")
            ST.PrintNp3D(self.NPpoint_s)
            ST.Mess("")
            ST.Mess("Vector from Origin to point in World Coordinates [r-point]: [mm]")
            ST.PrintNp3D(self.NPpoint_r)
            ST.Mess("")
            ST.Mess("Velocity of Vector from Origin to point [dr-point/dt]:")
            ST.PrintNp3D(self.NPpoint_drdt)
            ST.Mess("")

        # Make an array with the respective body Mass and moment of inertia
        self.NPMassArray = np.zeros(self.numMovBodiesx3)
        for bodyIndex in range(1, len(self.bodyGroup)):
            self.NPMassArray[(bodyIndex-1)*3:bodyIndex*3] = (
                self.NPMasskg[bodyIndex],
                self.NPMasskg[bodyIndex],
                self.NPmomentOfInertia[bodyIndex])

        # Transfer the joint UNIT vector coordinates to the NumPy arrays
        JointNumber = -1
        for joint in self.jointGroup:
            JointNumber += 1

            # Ignore the joints without defined code
            if hasattr(joint, "SimJoint") and ST.JOINT_TYPE_DICTIONARY[joint.SimJoint] <= ST.MAXNUMJOINTTYPES:
                # Unit vector on Head body in world coordinates
                self.NPunit_i[JointNumber] = joint.bodyHeadUnit[:2]
                self.NPunit_i90[JointNumber] = ST.Rot90NumPy(self.NPunit_i[JointNumber])
                self.NPunit_i_vel[JointNumber] = CAD.Vector()[:2]
                self.NPunit_i_vel90[JointNumber] = CAD.Vector()[:2]

                # Unit vector on the Head body in body local coordinates
                self.NPunit_i_XiEta[JointNumber] = joint.bodyHeadUnit[:2] @ self.NPRotMatrixPhi[bodyIndex]

                # Unit vector on Tail body in world coordinates
                self.NPunit_j[JointNumber] = joint.bodyTailUnit[:2]
                self.NPunit_j90[JointNumber] = ST.Rot90NumPy(self.NPunit_j[JointNumber])
                self.NPunit_j_vel[JointNumber] = CAD.Vector()[:2]
                self.NPunit_j_vel90[JointNumber] = CAD.Vector()[:2]

                # Unit vector on the Tail body in body local coordinates
                self.NPunit_j_XiEta[JointNumber] = joint.bodyTailUnit[:2] @ self.NPRotMatrixPhi[bodyIndex]

        # Next joint

        if Debug:
            ST.PrintNp2D(self.NPunit_i)
            ST.PrintNp2D(self.NPunit_j)
            ST.PrintNp2D(self.NPunit_i_XiEta)
            ST.PrintNp2D(self.NPunit_j_XiEta)

        # Assign number of constraints and number of bodies
        # to each defined joint according to its type
        JointNumber = -1
        for joint in self.jointGroup:
            JointNumber += 1
            # Only allow joints currently included in the code
            if hasattr(joint, "SimJoint") and ST.JOINT_TYPE_DICTIONARY[joint.SimJoint] <= ST.MAXNUMJOINTTYPES:

                # ***********************************************
                # Revolute joint
                if joint.SimJoint == "Revolute":
                    if joint.FunctType == -1:
                        joint.mConstraints = 2
                        joint.nBodies = 2
                        if joint.fixDof is True:
                            joint.mConstraints = 3
                            # Set the initial angle phi0 
                            if joint.Bi == 0:
                                self.NPphi0[joint.JointNumber] = -self.NPbody_phi[joint.Bj]
                            elif joint.Bj == 0:
                                self.NPphi0[joint.JointNumber] = self.NPbody_phi[joint.Bi]
                            else:
                                self.NPphi0[joint.JointNumber] = (
                                        self.NPbody_phi[joint.Bi] 
                                        - self.NPbody_phi[joint.Bj])

                # ***********************************************
                elif joint.SimJoint == "Fixed":
                    joint.mConstraints = 3
                    joint.nBodies = 2
                    if joint.Bi == 0:
                        V = -self.NPRotMatrixPhi[joint.Bj].T @ self.NPbody_r[joint.Bj]
                        self.NPphi0[joint.JointNumber] = -self.NPbody_phi[joint.Bj]
                    elif joint.Bj == 0:
                        V = self.NPbody_r[joint.Bi]
                        self.NPphi0[joint.JointNumber] = self.NPbody_phi[joint.Bi]
                    else:
                        V = self.NPRotMatrixPhi[joint.Bj].T @ (self.NPbody_r[joint.Bi] -
                                                                          self.NPbody_r[joint.Bj])
                        self.NPphi0[joint.JointNumber] = self.NPbody_phi[joint.Bi] - \
                                        self.NPbody_phi[joint.Bj]
                    self.NPd0[joint.JointNumber, 0] = V[0]
                    self.NPd0[joint.JointNumber, 1] = V[1]

                # ***********************************************
                elif joint.SimJoint == "Translation":
                    joint.mConstraints = 2
                    joint.nBodies = 2
                    if joint.fixDof is True:
                        joint.mConstraints = 3
                        if joint.Bi == 0:
                            vec = (+ self.NPpoint_r[joint.Bi, joint.Pi]
                                   - self.NPbody_r[joint.Bj]
                                   - self.NPRotMatrixPhi[joint.Bj] @ self.NPpoint_sXiEta[joint.Bj, joint.Pj])
                        elif joint.Bj == 0:
                            vec = (- self.NPpoint_r[joint.Bj, joint.Pj]
                                   + self.NPbody_r[joint.Bi]
                                   + self.NPRotMatrixPhi[joint.Bi] @ self.NPpoint_sXiEta[joint.Bi, joint.Pi])
                        else:
                            vec = (+ self.NPbody_r[joint.Bi]
                                   + self.NPRotMatrixPhi[joint.Bi] @ self.NPpoint_sXiEta[joint.Bi, joint.Pi]
                                   - self.NPbody_r[joint.Bj]
                                   - self.NPRotMatrixPhi[joint.Bj] @ self.NPpoint_sXiEta[joint.Bj, joint.Pj])
                        joint.phi0 = np.sqrt(vec.dot(vec))

                # ***********************************************
                elif joint.SimJoint == "Revolute-Revolute":
                    joint.mConstraints = 1
                    joint.nBodies = 2
                    joint.lengthLink = joint.Distance.Value

                # ***********************************************
                elif joint.SimJoint == "Translation-Revolute":
                    joint.mConstraints = 1
                    joint.nBodies = 2
                    joint.lengthLink = joint.Distance.Value

                # ***********************************************
                elif joint.SimJoint == "Disc":
                    joint.mConstraints = 2
                    joint.nBodies = 1
                    joint.phi0 = self.NPbody_phi[joint.Bj]
                    joint.x0 = self.NPbody_r[joint.Bj, 0]
                else:
                    CAD.Console.PrintError("Unknown Joint Type - this should never occur" + str(joint.SimJoint) + "\n")
            # end of is valid SimJoint
        # Next Joint Object

        # Add up all the numbers of constraints and allocate row start and end pointers
        self.numConstraints = 0
        for joint in self.jointGroup:
            if hasattr(joint, "SimJoint") and ST.JOINT_TYPE_DICTIONARY[joint.SimJoint] <= ST.MAXNUMJOINTTYPES:
                joint.rowStart = self.numConstraints
                joint.rowEnd = self.numConstraints + joint.mConstraints
                self.numConstraints = joint.rowEnd

        # Return with a flag to show we have reached the end of init error-free
        self.initialised = True

    #  -------------------------------------------------------------------------
    def MainSolve(self):
        ###########################################
        # CLEAN UP ERRONEOUS INPUTS BEFORE STARTING
        ###########################################
        
        # Correct for initial conditions consistency if requested
        if self.numConstraints != 0 and self.correctInitial:
            if self.correctInitialConditions() is False:
                CAD.Console.PrintError("Initial Conditions not successfully calculated")
                return

        # Determine any redundancy between constraints
        Jacobian = self.GetJacobian()
        if Debug:
            ST.Mess("Jacobian calculated to determine rank of solution")
            ST.PrintNp2D(Jacobian)
        matrixRank = np.linalg.matrix_rank(Jacobian)
        if matrixRank < self.numConstraints:
            CAD.Console.PrintError('The constraints exhibit Redundancy\n')
            return

        # Velocity correction
        velArrayNp = np.zeros((self.numMovBodiesx3,), dtype=np.float64)
        # Move velocities to the corrections array
        for bodyIndex in range(1, self.numBodies):
            velArrayNp[(bodyIndex-1) * 3: bodyIndex*3] = \
                self.NPbody_drdt[bodyIndex, 0], \
                self.NPbody_drdt[bodyIndex, 1], \
                self.NPbody_dphidt[bodyIndex]
        # Solve for velocity at time = 0
        # Unless the joint is Driven-Revolute or Driven-Translation
        # RHSVel = [0,0,...]   (i.e. a list of zeros)
        solution = np.linalg.solve(Jacobian @ Jacobian.T, (Jacobian @ velArrayNp)) # ToDo - self.RHSVel(0))
        deltaVel = -Jacobian.T @ solution
        if Debug:
            ST.Mess("Velocity Array: ")
            ST.PrintNp1D(True, velArrayNp)
            ST.Mess("Velocity Correction Solution: ")
            ST.PrintNp1D(True, solution)
            ST.Mess("Delta velocity: ")
            ST.PrintNp1D(True, deltaVel)
            
        # Move corrected velocities back into the system
        for bodyIndex in range(1, self.numBodies):
            self.NPbody_drdt[bodyIndex, 0] += deltaVel[(bodyIndex-1)*3]
            self.NPbody_drdt[bodyIndex, 1] += deltaVel[(bodyIndex-1)*3 + 1]
            self.NPbody_dphidt[bodyIndex] += deltaVel[(bodyIndex-1)*3 + 2]
        # Report corrected coordinates and velocities
        if Debug:
            ST.Mess("Corrected Positions: [mm]")
            ST.PrintNp2D(self.NPbody_r)
            ST.Mess("Corrected Phi:")
            ST.PrintNp1Ddeg(True, self.NPbody_phi)
            ST.Mess("Corrected Velocities [mm/s]:")
            ST.PrintNp2D(self.NPbody_drdt)
            ST.Mess("Corrected Angular Velocities:")
            ST.PrintNp1Ddeg(True, self.NPbody_dphidt)

        ##############################
        # START OF THE SOLUTION PROPER
        ##############################
        # Pack coordinates and velocities into the NumPy NParray
        NParray = np.zeros((self.numMovBodiesx3 * 2,), dtype=np.float64)
        index1 = 0
        index2 = self.numMovBodiesx3
        for bodyIndex in range(1, self.numBodies):
            NParray[index1:index1+2] = self.NPbody_r[bodyIndex]
            NParray[index1+2] = self.NPbody_phi[bodyIndex]
            NParray[index2:index2+2] = self.NPbody_drdt[bodyIndex]
            NParray[index2+2] = self.NPbody_dphidt[bodyIndex]
            index1 += 3
            index2 += 3

        # Set up the list of time intervals over which to integrate
        self.Tspan = np.arange(0.0, self.simEnd, self.simDelta)

        # ###################################################################################
        # Matrix Integration Function
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html
        # ###################################################################################
        # scipy.integrate.solve_ivp
        # INPUTS:
        #       fun,                      Function name
        #       t_span,                   (startTime, endTime)
        #       y0,                       Initial values array [NParray]
        #       method='RK45',            RK45 | RK23 | DOP853 | Radau | BDF | LSODA
        #       t_eval=None,              times to evaluate at
        #       dense_output=False,       continuous solution or not
        #       events=None,              events to track
        #       vectorized=False,         whether fun is vectorized (i.e. parallelized)
        #       args=None,
        #       first_step=None,          none means algorithm chooses
        #       max_step=inf,             default is inf
        #       rtol=1e-3, atol=1e-6      relative and absolute tolerances
        #       jacobian,                 required for Radau, BDF and LSODA
        #       jac_sparsity=None,        to help algorithm when it is sparse
        #       lband=inf, uband=inf,     lower and upper bandwidth of Jacobian
        #       min_step=0                minimum step (required for LSODA)
        # RETURNS:
        #       t                         time array
        #       y                         values array
        #       sol                       instance of ODESolution (when dense_output=True)
        #       t_events                  array of event times
        #       y_events                  array of values at the event_times
        #       nfev                      number of times the rhs was evaluated
        #       njev                      number of times the Jacobian was evaluated
        #       nlu                       number of LU decompositions
        #       status                    -1 integration step failure | +1 termination event | 0 Successful
        #       message                   Human readable error message
        #       success                   True if 0 or +1 above
        # ###################################################################################

        # Integrate the equations: 
        #   <Dynamics function> 
        #   (<start time>, <end time>) 
        #   <position & velocity array> 
        #   <times at which to evaluate> 
        #   <relative Tolerance> 
        #   <absolute Tolerance>
        startTime = time.time()
        solution = solve_ivp(self.Dynamics,
                             (0.0, self.simEnd),
                             NParray,
                             method = self.solverObj.SolverType,
                             t_eval=self.Tspan,
                             rtol=self.relativeTolerance,
                             atol=self.absoluteTolerance)
        self.elapsedTime = time.time() - startTime

        # Output the positions/angles velocities results file
        self.PosFILE = open(os.path.join(self.solverObj.Directory, "SimAnimation.csv"), 'w')
        Sol = solution.y.T
        for tick in range(len(solution.t)):
            self.PosFILE.write(str(solution.t[tick])+" ")
            for body in range(1, self.numBodies):
                self.PosFILE.write(str(Sol[tick, body * 6 - 6]) + " ")
                self.PosFILE.write(str(Sol[tick, body * 6 - 5]) + " ")
                self.PosFILE.write(str(Sol[tick, body * 6 - 4]) + " ")
                self.PosFILE.write(str(Sol[tick, body * 6 - 3]) + " ")
                self.PosFILE.write(str(Sol[tick, body * 6 - 2]) + " ")
                self.PosFILE.write(str(Sol[tick, body * 6 - 1]) + " ")
            self.PosFILE.write("\n")
        self.PosFILE.close()

        # Save the most important stuff into the solver object
        BodyNames = []
        for bodyObject in self.bodyGroup:
            BodyNames.append(bodyObject.Name)
        self.solverObj.BodyNames = BodyNames
        self.solverObj.DeltaTime = self.simDelta

        # Flag that the results are valid
        ST.getallObjects().SimResultsValid = True

        if self.solverObj.FileName != "-":
            self.outputResults(solution.t, solution.y.T)
            
    ##########################################
    #   This is the end of the actual solution
    #    The rest are all called subroutines
    ##########################################
    #  -------------------------------------------------------------------------
    def Dynamics(self, tick, NParray):
        """The Dynamics function which takes a 1D NParray 
        consisting of all the body world 3vectors concatenated to body velocity 3vectors
        and applies the physics of its movement to it,
        returning with a new NPDotArray
        """
        if Debug:
            ST.Mess("Input to 'Dynamics'")
            ST.PrintNp1D(True, NParray)

        # Unpack NParray into world coordinate and world velocity sub-arrays
        # [X, Y, phi, ..... velX, velY, phidot .....]
        index1 = 0
        index2 = self.numMovBodiesx3
        for bodyIndex in range(1, self.numBodies):
            self.NPbody_r[bodyIndex, 0] = NParray[index1]
            self.NPbody_r[bodyIndex, 1] = NParray[index1+1]
            self.NPbody_phi[bodyIndex] = NParray[index1+2]
            self.NPbody_drdt[bodyIndex, 0] = NParray[index2]
            self.NPbody_drdt[bodyIndex, 1] = NParray[index2+1]
            self.NPbody_dphidt[bodyIndex] = NParray[index2+2]
            index1 += 3
            index2 += 3

        if Debug:
            ST.Mess("Dynamics - World CoG:")
            ST.PrintNp2D(self.NPbody_r)
            ST.Mess("Dynamics - Phi:")
            ST.PrintNp1Ddeg(True, self.NPbody_phi)
            ST.Mess("Dynamics - Velocity CoG:")
            ST.PrintNp2D(self.NPbody_drdt)
            ST.Mess("Dynamics - Angular Velocity:")
            ST.PrintNp1Ddeg(True, self.NPbody_dphidt)

        # Update the point stuff accordingly
        self.updatePointPositions()
        self.updatePointVelocities()

        # generate an array of currently applied forces
        self.makeForceArray()

        # find the accelerations ( a = F / m )
        accel = []
        # If we have no constraints, the bodies just move subject to the forces
        if self.numConstraints == 0:
            for index in range(self.numMovBodiesx3):
                accel.append = self.NPforceArray[index]/self.NPMasskg[index]
                
        # We go through this process if we have any constraints
        else:
            Jacobian = self.GetJacobian()
            if Debug:
                ST.Mess("Dynamics - Jacobian")
                ST.PrintNp2D(Jacobian)

            # Create the Jacobian-Mass-Jacobian matrix
            # [ diagonal masses ---- negative Jacobian transpose ]
            # [    |                             |               ]
            # [  Jacobian      ------          Zeros             ]
            numBodPlusConstr = self.numMovBodiesx3 + self.numConstraints
            JacMasJac = np.zeros((numBodPlusConstr, numBodPlusConstr), dtype=np.float64)
            JacMasJac[0: self.numMovBodiesx3, 0: self.numMovBodiesx3] = np.diag(self.NPMassArray)
            JacMasJac[self.numMovBodiesx3:, 0: self.numMovBodiesx3] = Jacobian
            JacMasJac[0: self.numMovBodiesx3, self.numMovBodiesx3:] = -Jacobian.T
            if Debug:
                ST.Mess("Dynamics - Jacobian-MassDiagonal-JacobianT Array")
                ST.PrintNp2D(JacMasJac)

            # get r-h-s of acceleration constraints at this time
            rhsAccel = self.RHSAcc(tick)
            if Debug:
                ST.Mess("Dynamics - rhsAccel:")
                ST.PrintNp1D(True, rhsAccel)
                
            # Combine Force Array and rhs of Acceleration constraints into one 1D array
            rhs = np.zeros((numBodPlusConstr,), dtype=np.float64)
            rhs[0: self.numMovBodiesx3] = self.NPforceArray
            rhs[self.numMovBodiesx3:] = rhsAccel
            if Debug:
                ST.Mess("Dynamics - rhs:")
                ST.PrintNp1D(True, rhs)
                
            # Solve the JacMasJac augmented with the rhs
            solvedVector = np.linalg.solve(JacMasJac, rhs)
            
            # First half of solution are the acceleration values
            accel = solvedVector[: self.numMovBodiesx3]
            
            # Second half is Lambda which is reported in the output results routine
            self.Lambda = solvedVector[self.numMovBodiesx3:]
            if Debug:
                ST.Mess("Dynamics - Accelerations: ")
                ST.PrintNp1D(True, accel)
                ST.Mess("Dynamics - Lambda: ")
                ST.PrintNp1D(True, self.Lambda)
                ST.Mess("#"*80)

        # Transfer the velocity/accelerations into the
        # worldCoGDotDot/phiDotDot and DotArray/DotDotArray
        # [velX, velY, phidot, ..... accX, accY, phidotdot .....]
        NPDotArray = np.zeros((self.numMovBodiesx3 * 2,), dtype=np.float64)
        for bodyIndex in range(1, self.numBodies):
            accelIndex = (bodyIndex-1) * 3
            self.NPbody_d2rdt2[bodyIndex] = accel[accelIndex], accel[accelIndex + 1]
            self.NPbody_d2phidt2[bodyIndex] = accel[accelIndex + 2]
            
        index1 = 0
        index2 = self.numMovBodiesx3
        for bodyIndex in range(1, self.numBodies):
            NPDotArray[index1:index1+2] = self.NPbody_drdt[bodyIndex]
            NPDotArray[index1+2] = self.NPbody_dphidt[bodyIndex]
            NPDotArray[index2:index2+2] = self.NPbody_d2rdt2[bodyIndex]
            NPDotArray[index2+2] = self.NPbody_d2phidt2[bodyIndex]
            index1 += 3
            index2 += 3

        # Increment number of function evaluations
        self.Counter += 1

        return NPDotArray
    #  -------------------------------------------------------------------------
    def correctInitialConditions(self):
        """This function corrects the supplied initial conditions by making
        the body coordinates and velocities consistent with the constraints"""

        # Try Newton-Raphson iteration for n up to 20
        for n in range(20):
            # Update the points positions
            self.updatePointPositions()

            # Evaluate Deltaconstraint of the constraints at time=0
            Deltaconstraint = self.Getconstraints(0)
            if Debug:
                ST.Mess("Delta constraints Result:")
                ST.PrintNp1D(True, Deltaconstraint)
                
            # Evaluate Jacobian
            Jacobian = self.GetJacobian()
            if Debug:
                ST.Mess("Correction Jacobian:")
                ST.PrintNp2D(Jacobian)

            # Determine any redundancy between constraints
            redundant = np.linalg.matrix_rank(Jacobian) 
            if redundant < self.numConstraints:
                CAD.Console.PrintError('The constraints exhibit Redundancy while correcting initial conditions\n')
                return False

            # We have successfully converged if the ||Deltaconstraint|| is very small
            DeltaconstraintLengthSq = 0
            for index in range(self.numConstraints):
                DeltaconstraintLengthSq += Deltaconstraint[index] ** 2
            if Debug:
                ST.Mess("Total constraint Error: " + str(math.sqrt(DeltaconstraintLengthSq)))

            if DeltaconstraintLengthSq < 1.0e-16:
                return True

            # Solve for the new corrections
            solution = np.linalg.solve(Jacobian @ Jacobian.T, Deltaconstraint)
            delta = - Jacobian.T @ solution
            # Correct the estimates
            for bodyIndex in range(1, self.numBodies):
                self.NPbody_r[bodyIndex, 0] += delta[(bodyIndex-1)*3]
                self.NPbody_r[bodyIndex, 1] += delta[(bodyIndex-1)*3+1]
                self.NPbody_phi[bodyIndex] += delta[(bodyIndex-1)*3+2]
                
        CAD.Console.PrintError("Newton-Raphson Correction failed to converge\n\n")
        return True
    #  -------------------------------------------------------------------------
    def updatePointPositions(self):
        """Here we update the positions as the bodies move and rotate"""

        for bodyIndex in range(1, self.numBodies):

            # Compute the Rotation Matrix
            self.NPRotMatrixPhi[bodyIndex] = ST.CalculateRotationMatrix(self.NPbody_phi[bodyIndex])

            if Debug:
                ST.Mess("Update Point Positions:")
                ST.MessNoLF("In Xi-Eta Coordinates           ")
                ST.MessNoLF("Relative to CoG                 ")
                ST.MessNoLF("Relative to CoG Rotated 90      ")
                ST.Mess("World Coordinates               ")
            for pointIndex in range(self.NPnumJointPointsInBody[bodyIndex]):
                pointVector = self.NPRotMatrixPhi[bodyIndex] @ self.NPpoint_sXiEta[bodyIndex, pointIndex]
                self.NPpoint_s[bodyIndex, pointIndex] = pointVector
                self.NPpoint_s90[bodyIndex][pointIndex] = ST.Rot90NumPy(pointVector)
                self.NPpoint_r[bodyIndex, pointIndex] = self.NPbody_r[bodyIndex] + pointVector
                if Debug:
                    ST.PrintNp1D(False, self.NPpoint_sXiEta[bodyIndex][pointIndex])
                    ST.MessNoLF("   ")
                    ST.PrintNp1D(False, self.NPpoint_s[bodyIndex][pointIndex])
                    ST.MessNoLF("   ")
                    ST.PrintNp1D(False, self.NPpoint_s90[bodyIndex][pointIndex])
                    ST.MessNoLF("   ")
                    ST.PrintNp1D(True, self.NPpoint_r[bodyIndex][pointIndex])
        # Next bodyIndex
    #  -------------------------------------------------------------------------
    def updatePointVelocities(self):

        for bodyIndex in range(1, self.numBodies):
            for pointIndex in range(self.NPnumJointPointsInBody[bodyIndex]):
                deltaVelVector = self.NPpoint_s90[bodyIndex, pointIndex] * self.NPbody_dphidt[bodyIndex]
                self.NPpoint_dsdt[bodyIndex, pointIndex] = deltaVelVector
                self.NPpoint_drdt[bodyIndex, pointIndex] = self.NPbody_drdt[bodyIndex] + deltaVelVector
        # for forceObj in self.NPforceObjList:
        #   if forceObj.forceType != 0:
        #        if forceObj.Bi != 0:
        #            forceObj.FUnitHeadWorldDot = ST.Rot90NumPy(forceObj.FUnitHeadWorld) * self.NPbody_dphidt[forceObj.Bi]
    #  -------------------------------------------------------------------------
    def Getconstraints(self, tick):
        """Returns a numConstraints-long vector which contains the current deviation
        from the defined constraints"""

        deltaConstraintNp = np.zeros((self.numConstraints,), dtype=np.float64)
        
        # Call the applicable function which is pointed to by the constraint function dictionary
        for joint in self.jointGroup:
            if hasattr(joint, "SimJoint") and ST.JOINT_TYPE_DICTIONARY[joint.SimJoint] <= ST.MAXNUMJOINTTYPES:
                constraint = self.dictconstraintFunctions[ST.JOINT_TYPE_DICTIONARY[joint.SimJoint]](joint, tick)
                deltaConstraintNp[joint.rowStart: joint.rowEnd] = constraint

        return deltaConstraintNp
    #  =========================================================================
    def GetJacobian(self):
        """Returns the Jacobian matrix numConstraints X (3 x numMovBodies)"""

        Jacobian = np.zeros((self.numConstraints, self.numMovBodiesx3,))
        for joint in self.jointGroup:
            if ST.JOINT_TYPE_DICTIONARY[joint.SimJoint] <= ST.MAXNUMJOINTTYPES:
                # Call the applicable function which is pointed to by the Jacobian dictionary
                JacobianHead, JacobianTail = self.dictJacobianFunctions[ST.JOINT_TYPE_DICTIONARY[joint.SimJoint]](joint)
                # Fill in the values in the Jacobian
                if joint.Bi != 0:
                    columnHeadStart = (joint.Bi-1) * 3
                    columnHeadEnd = joint.Bi * 3
                    Jacobian[joint.rowStart: joint.rowEnd, columnHeadStart: columnHeadEnd] = JacobianHead
                if joint.Bj != 0:
                    columnTailStart = (joint.Bj-1) * 3
                    columnTailEnd = joint.Bj * 3
                    Jacobian[joint.rowStart: joint.rowEnd, columnTailStart: columnTailEnd] = JacobianTail
        return Jacobian
    #  =========================================================================
    def RHSAcc(self, tick):
        """Returns a numConstraints-long vector containing gamma"""

        # Determine the Right-Hand-Side of the acceleration equation (gamma)
        rhsAcc = np.zeros((self.numConstraints,), dtype=np.float64)

        # Call the applicable function which is pointed to by the Acceleration function dictionary
        for joint in self.jointGroup:
            if ST.JOINT_TYPE_DICTIONARY[joint.SimJoint] <= ST.MAXNUMJOINTTYPES:
                #if joint.SimJoint == "Revolute" and joint.FunctType != -1:
                #    setattr(joint, "SimJoint", "Driven-Revolute")
                gamma = self.dictAccelerationFunctions[ST.JOINT_TYPE_DICTIONARY[joint.SimJoint]](joint, tick)
                rhsAcc[joint.rowStart: joint.rowEnd] = gamma

        return rhsAcc
    #  -------------------------------------------------------------------------
    def RHSVel(self, tick):

        # ==================================
        # Matlab Code from Nikravesh: DAP_BC
        # ==================================
        #     rhs = zeros(nConst,1);
        # for JointNumber = 1:nJ
        #    switch (Joints(JointNumber).type);
        #        case {'rel-rot'}
        #            [fun, fun_d, fun_dd] = functs(Joints(JointNumber).iFunct, t);
        #            f = fun_d;
        #            rhs(Joints(JointNumber).rows:Joints(JointNumber).rowe) = f;
        #        case {'rel-tran'}
        #            [fun, fun_d, fun_dd] = functs(Joints(JointNumber).iFunct, t);
        #            f = fun*fun_d;
        #            rhs(Joints(JointNumber).rows:Joints(JointNumber).rowe) = f;
        #    end
        # end
        # ==================================
        # Call the applicable Driven-Revolute or Driven-Translation function where applicable
        rhsVelNp = np.zeros((self.numConstraints,), dtype=np.float64)

        return rhsVelNp
    #  =========================================================================
    def Revolute_constraint(self, joint, tick):
        """Evaluate the constraints for a Revolute joint"""

        constraintNp = self.NPpoint_r[joint.Bi, joint.Pi] - self.NPpoint_r[joint.Bj, joint.Pj]

        if Debug:
            ST.Mess('Revolute Constraint:')
            ST.MessNoLF('    Point I: ')
            ST.PrintNp1D(True, self.NPpoint_r[joint.Bi, joint.Pi])
            ST.MessNoLF('    Point J: ')
            ST.PrintNp1D(True, self.NPpoint_r[joint.Bj, joint.Pj])
            ST.MessNoLF('    Difference Vector: ')
            ST.PrintNp1D(True, constraintNp)

        if joint.fixDof:
            if joint.Bi == 0:
                constraintNp = np.array([constraintNp[0],
                                         constraintNp[1],
                                         (-self.NPbody_phi[joint.Bj] - self.NPphi0[joint.JointNumber])])
            elif joint.Bj == 0:
                constraintNp = np.array([constraintNp[0],
                                         constraintNp[1],
                                         (self.NPbody_phi[joint.Bi] - self.NPphi0[joint.JointNumber])])
            else:
                constraintNp = np.array([constraintNp[0],
                                         constraintNp[1],
                                         (self.NPbody_phi[joint.Bi]
                                          - self.NPbody_phi[joint.Bj]
                                          - self.NPphi0[joint.JointNumber])])
        return constraintNp
    #  -------------------------------------------------------------------------
    def Revolute_Jacobian(self, joint):
        """ Evaluate the Jacobian for a Revolute joint """

        if joint.fixDof is False:
            JacobianHead = np.array([
                [1.0, 0.0, self.NPpoint_s90[joint.Bi, joint.Pi, 0]],
                [0.0, 1.0, self.NPpoint_s90[joint.Bi, joint.Pi, 1]]])
            JacobianTail = np.array([
                [-1.0, 0.0, -self.NPpoint_s90[joint.Bj, joint.Pj, 0]],
                [0.0, -1.0, -self.NPpoint_s90[joint.Bj, joint.Pj, 1]]])
        else:
            JacobianHead = np.array([
                [1.0, 0.0, self.NPpoint_s90[joint.Bi, joint.Pi, 0]],
                [0.0, 1.0, self.NPpoint_s90[joint.Bi, joint.Pi, 1]],
                [0.0, 0.0, 1.0]])
            JacobianTail = np.array([
                [-1.0, 0.0, -self.NPpoint_s90[joint.Bj, joint.Pj, 0]],
                [0.0, -1.0, -self.NPpoint_s90[joint.Bj, joint.Pj, 1]],
                [0.0, 0.0, -1.0]])
        if Debug:
            ST.Mess("Jacobian Head")
            ST.PrintNp2D(JacobianHead)
            ST.Mess("Jacobian Tail")
            ST.PrintNp2D(JacobianTail)

        return JacobianHead, JacobianTail
    #  -------------------------------------------------------------------------
    def Revolute_gamma(self, joint, tick):
        """ Evaluate gamma for a Revolute joint """

        if joint.Bi == 0:
            gammai = np.array([0.0, 0.0])
        else:
            gammai = -ST.Rot90NumPy(self.NPpoint_dsdt[joint.Bi, joint.Pi]) * \
                     self.NPbody_dphidt[joint.Bi]

        if joint.Bj == 0:
            gammaj = np.array([0.0, 0.0])
        else:
            gammaj = ST.Rot90NumPy(self.NPpoint_dsdt[joint.Bj, joint.Pj]) * \
                     self.NPbody_dphidt[joint.Bj]

        gamma = gammai + gammaj

        if joint.fixDof:
            gamma = np.array([gamma[0], gamma[1], 0.0])

        return gamma
    #  =========================================================================
    def Revolute_Revolute_constraint(self, joint, tick):
        """ Evaluate the constraints for a Revolute-Revolute joint """

        diff = self.NPpoint_r[joint.Bi, joint.Pi] - self.NPpoint_r[joint.Bj, joint.Pj]

        return np.array([(diff.dot(diff) - joint.lengthLink ** 2) / 2.0])
    #  -------------------------------------------------------------------------
    def Revolute_Revolute_Jacobian(self, joint):
        """ Evaluate the Jacobian for a Revolute-Revolute joint """

        diff = self.NPpoint_r[joint.Bi, joint.Pi] - self.NPpoint_r[joint.Bj, joint.Pj]
        jointUnitVec = diff / joint.lengthLink

        JacobianHead = np.array([jointUnitVec[0], jointUnitVec[1], jointUnitVec.dot(self.NPpoint_s90[joint.Bi, joint.Pi])])
        JacobianTail = np.array([-jointUnitVec[0], -jointUnitVec[1], -jointUnitVec.dot(self.NPpoint_s90[joint.Bj, joint.Pj])])

        return JacobianHead, JacobianTail
    #  -------------------------------------------------------------------------
    def Revolute_Revolute_gamma(self, joint, tick):
        """ Evaluate gamma for a Revolute-Revolute joint """
        """
        Nikravesh:
        Pi = Joints(Ji).iPindex;
        Pj = Joints(Ji).jPindex;
        Bi = Joints(Ji).iBindex;
        Bj = Joints(Ji).jBindex;
        
        d = Points(Pi).rP - Points(Pj).rP;
        d_d = Points(Pi).rP_d - Points(Pj).rP_d;
        L = Joints(Ji).L;
        
        u = d / L;
        u_d = d_d / L;

        f = - u_d' * d_d;

    if Bi == 0
        f = f + u' * s_rot(Points(Pj).sP_d) * Bodies(Bj).p_d;
    elseif Bj == 0:
        f = f - u' * s_rot(Points(Pi).sP_d) * Bodies(Bi).p_d;
    else
        f = f - u' * (s_rot(Points(Pi).sP_d*Bodies(Bi).p_d - Points(Pj).sP_d * Bodies(Bj).p_d));
    end
    """
        diff = self.NPpoint_r[joint.Bi, joint.Pi] - self.NPpoint_r[joint.Bj, joint.Pj]
        diffDot = self.NPpoint_drdt[joint.Bi, joint.Pi] - self.NPpoint_drdt[joint.Bj, joint.Pj]
        jointUnitVec = diff / joint.lengthLink
        jointUnitVecDot = diffDot / joint.lengthLink

        gamma = -jointUnitVecDot.dot(diffDot)

        if joint.Bi == 0:
            gammai = 0.0
        else:
            gammai = ST.Rot90NumPy(jointUnitVec).dot(self.NPpoint_dsdt[joint.Bi, joint.Pi] *
                                                    self.NPbody_dphidt[joint.Bi])

        if joint.Bj == 0:
            gammaj = 0.0
        else:
            gammaj = ST.Rot90NumPy(jointUnitVec).dot(-self.NPpoint_dsdt[joint.Bj, joint.Pj] * self.NPbody_dphidt[joint.Bj])

        return gamma + gammai + gammaj
    #  =========================================================================
    def Fixed_constraint(self, joint, tick):
        """ Evaluate the constraints for a Fixed joint """

        if joint.Bi == 0:
            return np.array([-(self.NPbody_r[joint.Bj] +
                               self.NPRotMatrixPhi[joint.Bj] @ self.NPd0[joint.JointNumber]),
                             -self.NPbody_phi[joint.Bj] - self.NPphi0[joint.JointNumber]])
        elif joint.Bj == 0:
            return np.array([self.NPbody_r[joint.Bi] - self.NPd0[joint.JointNumber],
                             self.NPbody_phi[joint.Bi] - self.NPphi0[joint.JointNumber]])
        else:
            return np.array([self.NPbody_r[joint.Bi] -
                             (self.NPbody_r[joint.Bj] +
                              self.NPRotMatrixPhi[joint.Bj] @ self.NPd0[joint.JointNumber]),
                             self.NPbody_phi[joint.Bi] -
                             self.NPbody_phi[joint.Bj] -
                             self.NPphi0[joint.JointNumber]])
    #  -------------------------------------------------------------------------
    def Fixed_Jacobian(self, joint):
        """ Evaluate the Jacobian for a Fixed joint """

        JacobianHead = np.array([[1.0, 0.0, 0.0],
                                 [0.0, 1.0, 0.0],
                                 [0.0, 0.0, 1.0]])
        JacobianTail = np.array([[-1.0, 0.0, 0.0],
                                 [0.0, -1.0, 0.0],
                                 [0.0, 0.0, -1.0]])
        if joint.Bj != 0:
            tailVector = ST.Rot90NumPy(self.NPRotMatrixPhi[joint.Bj] @ self.NPd0[joint.JointNumber])
            JacobianTail = np.array([[-1.0, 0.0, -tailVector[0]],
                                     [0.0, -1.0, -tailVector[1]],
                                     [0.0, 0.0, -1.0]])
        return JacobianHead, JacobianTail
    #  -------------------------------------------------------------------------
    def Fixed_gamma(self, joint, tick):
        """ Evaluate gamma for a Fixed joint """

        if joint.Bj != 0:
            tailVector = -self.NPRotMatrixPhi[joint.Bj] @ (self.NPd0[joint.JointNumber] *
                                                          (self.NPbody_dphidt[joint.Bj]**2))
            return np.array([tailVector[0], tailVector[1], 0.0])
        else:
            return np.array([0.0, 0.0, 0.0])
    #  =========================================================================
    def Translation_constraint(self, joint, tick):
        """ Evaluate the constraints for a Translation joint """

        jointUnitJRot = self.NPunit_j90[joint.JointNumber]
        jointUnitIVec = self.NPunit_i[joint.JointNumber]

        diff = self.NPpoint_r[joint.Bi, joint.Pi] - self.NPpoint_r[joint.Bj, joint.Pj]

        if Debug:
            ST.Mess('Translation Constraint:')
            ST.MessNoLF('    Unit I Vector: ')
            ST.PrintNp1D(True, jointUnitIVec)
            ST.MessNoLF('    Unit J Vector Rotated: ')
            ST.PrintNp1D(True, jointUnitJRot)
            ST.MessNoLF('    World I: ')
            ST.PrintNp1D(True, self.NPpoint_r[joint.Bi, joint.Pi])
            ST.MessNoLF('    World J: ')
            ST.PrintNp1D(True, self.NPpoint_r[joint.Bj, joint.Pj])
            ST.MessNoLF('    Difference vector: ')
            ST.PrintNp1D(True, diff)

        if joint.fixDof is False:
            if Debug:
                ST.MessNoLF('    Unit J vector Rotated . diff: ')
                ST.Mess(jointUnitJRot.dot(diff))
                ST.MessNoLF('    Unit J vector Rotated . Unit I Vector: ')
                ST.Mess(jointUnitJRot.dot(jointUnitIVec))

            return np.array([jointUnitJRot.dot(diff),
                             jointUnitJRot.dot(jointUnitIVec)])
        else:
            return np.array(
                [jointUnitJRot.dot(diff),
                 jointUnitJRot.dot(jointUnitIVec),
                 (jointUnitIVec.dot(diff) - joint.phi0) / 2])

    #  -------------------------------------------------------------------------
    def Translation_Jacobian(self, joint):
        """ Evaluate the Jacobian for a Translation joint """

        jointUnitJVec = self.NPunit_j[joint.JointNumber]
        jointUnitJRot = self.NPunit_j90[joint.JointNumber]
        diff = self.NPpoint_r[joint.Bi, joint.Pi] - self.NPpoint_r[joint.Bj, joint.Pj]

        if joint.fixDof is False:
            JacobianHead = np.array([[jointUnitJRot[0], jointUnitJRot[1],
                                      jointUnitJVec.dot(self.NPpoint_s[joint.Bi, joint.Pi])],
                                     [0.0, 0.0, 1.0]])
            JacobianTail = np.array([[-jointUnitJRot[0], -jointUnitJRot[1],
                                      -jointUnitJVec.dot(self.NPpoint_s[joint.Bj, joint.Pj] + diff)],
                                     [0.0, 0.0, -1.0]])
        else:
            JacobianHead = np.array([[jointUnitJRot[0], jointUnitJRot[1],
                                      jointUnitJVec.dot(self.NPpoint_s[joint.Bi, joint.Pi])],
                                     [0.0, 0.0, 1.0],
                                     [jointUnitJVec[0], jointUnitJVec[1],
                                      jointUnitJVec.dot(self.NPpoint_s90[joint.Bi, joint.Pi])]])
            JacobianTail = np.array([[-jointUnitJRot[0], -jointUnitJRot[1],
                                      -jointUnitJVec.dot(self.NPpoint_s[joint.Bj, joint.Pj] + diff)],
                                     [0.0, 0.0, -1.0],
                                     [-jointUnitJVec[0], -jointUnitJVec[1],
                                      -jointUnitJVec.dot(self.NPpoint_s90[joint.Bj, joint.Pj])]])
        return JacobianHead, JacobianTail

    #  -------------------------------------------------------------------------
    def Translation_gamma(self, joint, tick):
        """ Evaluate gamma for a Translation joint """

        jointUnitJDotVec = self.NPunit_j_vel[joint.JointNumber]
        jointUnitJDotRot = ST.Rot90NumPy(jointUnitJDotVec)
        if joint.Bi == 0 or joint.Bj == 0:
            f2 = 0
        else:
            f2 = jointUnitJDotVec.dot(self.NPbody_r[joint.Bi] - self.NPbody_r[joint.Bj]) * \
                 self.NPbody_dphidt[joint.Bi] - \
                 2 * jointUnitJDotRot.dot(self.NPbody_drdt[joint.Bi] - self.NPbody_drdt[joint.Bj])

        if joint.fixDof is False:
            return np.array([f2, 0.0])
        else:
            diff = self.NPpoint_r[joint.Bi, joint.Pi] - \
                   self.NPpoint_r[joint.Bj, joint.Pj]
            diffDot = self.NPpoint_drdt[joint.Bi, joint.Pi] - \
                      self.NPpoint_drdt[joint.Bj, joint.Pj]
            jointUnitVec = diff/joint.phi0
            jointUnitVecDot = diffDot/joint.phi0
            f3 = -jointUnitVecDot.dot(diffDot)
            if joint.Bi == 0:
                f3 += jointUnitVec.dot(ST.Rot90NumPy(self.NPpoint_dsdt[joint.Bj, joint.Pj]) *
                                       self.NPbody_dphidt[joint.Bj])
            elif joint.Bj == 0:
                f3 -= jointUnitVec.dot(ST.Rot90NumPy(self.NPpoint_dsdt[joint.Bi, joint.Pi]) *
                                       self.NPbody_dphidt[joint.Bi])
            else:
                f3 -= jointUnitVec.dot(ST.Rot90NumPy(self.NPpoint_dsdt[joint.Bi, joint.Pi] *
                                                     self.NPbody_dphidt[joint.Bi] -
                                                     self.NPpoint_dsdt[joint.Bj, joint.Pj] *
                                                     self.NPbody_dphidt[joint.Bj]))
            return np.array([f2, 0.0, f3])

    #  =========================================================================
    def Translation_Revolute_constraint(self, joint, tick):
        """ Evaluate the constraints for a Translation-Revolute joint """

        diff = self.NPpoint_r[joint.Bi, joint.Pi] - self.NPpoint_r[joint.Bj, joint.Pj]

        return np.array([self.NPunit_i[joint.Bi].dot(diff) - joint.lengthLink])
    #  -------------------------------------------------------------------------
    def Translation_Revolute_Jacobian(self, joint):
        """ Evaluate the Jacobian for a Translation-Revolute joint """

        jointUnitVec = self.NPunit_i[joint.JointNumber]
        jointUnitVecRot = self.NPunit_i90[joint.JointNumber]
        diff = self.NPpoint_r[joint.Bi, joint.Pi] - self.NPpoint_r[joint.Bj, joint.Pj]

        JacobianHead = np.array([jointUnitVecRot[0], jointUnitVecRot[1],
                                 jointUnitVec.dot(self.NPpoint_s[joint.Bi, joint.Pi] - diff)])
        JacobianTail = np.array([-jointUnitVecRot[0], -jointUnitVecRot[1],
                                 -jointUnitVec.dot(self.NPpoint_s[joint.Bj, joint.Pj])])

        return JacobianHead, JacobianTail
    #  -------------------------------------------------------------------------
    def Translation_Revolute_gamma(self, joint, tick):
        """ Evaluate gamma for a Translation-Revolute joint """

        jointUnitVec = self.NPunit_i[joint.JointNumber]
        jointUnitVecDot = self.NPunit_i_vel[joint.JointNumber]

        diff = self.NPpoint_r[joint.Bi, joint.Pi] - self.NPpoint_r[joint.Bj, joint.Pj]
        diffDot = self.NPpoint_drdt[joint.Bi, joint.Pi] - self.NPpoint_drdt[joint.Bj, joint.Pj]

        if joint.Bi == 0:
            gammai = 0.0
        else:
            gammai = jointUnitVecDot.dot(diff * self.NPbody_dphidt[joint.Bi] + 2 * ST.Rot90NumPy(diffDot)) - \
                     jointUnitVec.dot(self.NPpoint_dsdt[joint.Bi, joint.Pi] * self.NPbody_dphidt[joint.Bi])

        if joint.Bj == 0:
            gammaj= 0.0
        else:
            gammaj = jointUnitVec.dot(self.NPpoint_dsdt[joint.Bj, joint.Pj] * self.NPbody_dphidt[joint.Bj])

        return gammai + gammaj
    #  =========================================================================
    def Disc_constraint(self, joint, tick):
        """ Evaluate the constraints for a Disc/wheel/pinion joint """

        return np.array([(self.NPbody_r[joint.Bj, 1] - joint.Distance.Value),
                         ((self.NPbody_r[joint.Bj, 0] - joint.x0) +
                          joint.Distance.Value * (self.NPbody_phi[joint.Bj] - joint.phi0))])
    #  -------------------------------------------------------------------------
    def Disc_Jacobian(self, joint):
        """ Evaluate the Jacobian for a Disc joint """

        JacobianHead = np.array([[0.0, 1.0, 0.0],
                                 [1.0, 0.0, joint.Distance]])

        return JacobianHead, JacobianHead
    #  -------------------------------------------------------------------------
    def Disc_gamma(self, joint, tick):
        """ Evaluate gamma for a Disc joint """

        return np.array([0.0, 0.0])
    #  =========================================================================
    def makeForceArray(self):

        # Reset all forces and moments to zero
        for bodyIndex in range(1, self.numBodies):
            self.NPsumForces[bodyIndex] = np.zeros((2,), dtype=np.float64)
            self.NPsumMoments[bodyIndex] = np.zeros((1,), dtype=np.float64)

        # Add up all the body force vectors for all the bodies
        forceIndex = -1
        for forceObj in self.forceList:
            forceIndex += 1

            # ==================================
            # Gravity force
            if forceObj.forceType == "Gravity":
                for bodyIndex in range(1, self.numBodies):
                    self.NPsumForces[bodyIndex] += self.NPWeight[bodyIndex]
            else:
                CAD.Console.PrintError("Unknown Force type - this should never occur\n")
        # Next force object

        # ==================================
        # The force array has three values for every body
        # x and y are the sum of forces and z is the sum of moments
        for bodyIndex in range(1, self.numBodies):
            self.NPforceArray[(bodyIndex - 1) * 3: bodyIndex * 3 - 1] = self.NPsumForces[bodyIndex]
            self.NPforceArray[bodyIndex * 3 - 1] = self.NPsumMoments[bodyIndex]

        if Debug:
            ST.Mess("Force Array:  ")
            ST.PrintNp1D(True, self.NPforceArray)

    #  =========================================================================
    def outputResults(self, timeValues, uResults):

        # Compute body accelerations, Lagrange multipliers, coordinates and
        #    velocity of all points, kinetic and potential energies,
        #             at every reporting time interval
        self.solverObj = CAD.ActiveDocument.findObjects(Name="^SimSolver$")[0]
        fileName = self.solverObj.Directory+"/"+self.solverObj.FileName+".csv"
        SimResultsFILE = open(fileName, 'w')
        numTicks = len(timeValues)

        ##################################################################3
        # THE HEADINGS
        # Create the vertical headings list
        # To write each body name into the top row of the spreadsheet,
        # would make some columns very big by default
        # So body names and point names are also written vertically in
        # The column before the body/point data is written
        VerticalHeaders = []
        # Write the column headers horizontally
        for threeLines in ["first", "second", "third"]:
            ColumnCounter = 0
            if threeLines == "first":
                SimResultsFILE.write("Time: ")
            elif threeLines == "second":
                SimResultsFILE.write(self.solverObj.SolverType+" ")
            else:
                SimResultsFILE.write(str(int(self.elapsedTime)) + " ")
            # Bodies Headings
            bodyIndex = -1
            for bodyObj in self.bodyGroup:
                bodyIndex += 1
                if bodyIndex != 0:
                    if threeLines == "first":
                        VerticalHeaders.append(bodyObj.Label)
                        SimResultsFILE.write("B" + str(bodyIndex))
                        SimResultsFILE.write(" x y phi phi dx dy dphi dphi d2x d2y d2phi d2phi ")
                    elif threeLines == "second":
                        SimResultsFILE.write(" - - - (rad) (deg) dt dt dt(r) dt(d) dt2 dt2 dt2(r) dt2(d) ")
                    else:
                        SimResultsFILE.write(VerticalHeaders[ColumnCounter] + " -"*12 + " ")
                    ColumnCounter += 1
                    # Points Headings
                    for JointNumber in range(self.NPnumJointPointsInBody[bodyIndex]):
                        if threeLines == "first":
                            VerticalHeaders.append(bodyObj.jointNameList[JointNumber])
                            SimResultsFILE.write("J" + str(JointNumber+1) + " x y dx dy ")
                        elif threeLines == "second":
                            SimResultsFILE.write("- - - dt dt ")
                        else:
                            SimResultsFILE.write(VerticalHeaders[ColumnCounter] + " -"*4 + " ")
                        ColumnCounter += 1
            # Next bodyObj

            # Lambda Headings
            if self.numConstraints > 0:
                bodyIndex = -1
                for bodyObj in self.bodyGroup:
                    bodyIndex += 1
                    if bodyIndex !=0:
                        if threeLines == "first":
                            VerticalHeaders.append(bodyObj.Label)
                            SimResultsFILE.write("Lam" + str(bodyIndex) + " x y ")
                        elif threeLines == "second":
                            SimResultsFILE.write("- - - ")
                        else:
                            SimResultsFILE.write(VerticalHeaders[ColumnCounter] + " - - ")
                        ColumnCounter += 1

            # Kinetic Energy Headings
            bodyIndex = -1
            for bodyObj in self.bodyGroup:
                bodyIndex += 1
                if bodyIndex !=0:
                    if threeLines == "first":
                        VerticalHeaders.append(bodyObj.Label)
                        SimResultsFILE.write("K" + str(bodyIndex) + " Lin Ang ")
                    elif threeLines == "second":
                        SimResultsFILE.write("- Kin Kin ")
                    else:
                        SimResultsFILE.write(VerticalHeaders[ColumnCounter] + " - - ")
                    ColumnCounter += 1

            # Potential Energy Headings
            forceIndex = -1
            for forceObj in self.forceList:
                forceIndex += 1
                if forceObj.forceType == "Gravity":
                    bodyIndex = -1
                    for bodyObj in self.bodyGroup:
                        bodyIndex += 1
                        if bodyIndex != 0:
                            if threeLines == "first":
                                VerticalHeaders.append(bodyObj.Label)
                                SimResultsFILE.write("Pot" + str(bodyIndex) + " - ")
                            elif threeLines == "second":
                                SimResultsFILE.write("- - ")
                            else:
                                SimResultsFILE.write(VerticalHeaders[ColumnCounter] + " - ")
                            ColumnCounter += 1

            # Energy Totals Headings
            if threeLines == "first":
                SimResultsFILE.write("Total Total\n")
            elif threeLines == "second":
                SimResultsFILE.write("Kinet Poten\n")
            else:
                SimResultsFILE.write(" - - \n")
        # Next threeLines

        ##################################################################3
        # THE DATA
        # Do the calculations for each point in time
        # Plus an extra one at time=-1 (with no printing)
        # The t=-1 enables us to calculate a zero-point potential energy
        VerticalCounter = 0
        TickRange = range(-1, numTicks)
        for timeIndex in TickRange:
            if timeIndex >= 0:
                tick = timeValues[timeIndex]
            else:
                tick = timeValues[0]
            ColumnCounter = 0

            # Do the Dynamics on the uResults at this tick
            if timeIndex >= 0:
                self.Dynamics(tick, uResults[timeIndex])

            # Write Time
            if timeIndex >= 0:
                SimResultsFILE.write(str(tick) + " ")

            # Write All the Bodies position, positionDot, positionDotDot
            for bodyIndex in range(1, self.numBodies):
                if timeIndex >= 0:
                    # Write Body Name vertically
                    if VerticalCounter < len(VerticalHeaders[ColumnCounter]):
                        character = VerticalHeaders[ColumnCounter][VerticalCounter]
                        if character in "0123456789":
                            SimResultsFILE.write("'" + character + "' ")
                        else:
                            SimResultsFILE.write(character + " ")
                    else:
                        SimResultsFILE.write("- ")

                    ColumnCounter += 1
                    # X Y
                    SimResultsFILE.write(str(self.NPbody_r[bodyIndex])[1:-1] + " ")
                    # Phi (rad)
                    SimResultsFILE.write(str(self.NPbody_phi[bodyIndex]) + " ")
                    # Phi (deg)
                    SimResultsFILE.write(str(self.NPbody_phi[bodyIndex] * 180.0 / math.pi) + " ")
                    # Xdot Ydot
                    SimResultsFILE.write(str(self.NPbody_drdt[bodyIndex])[1:-1] + " ")
                    # PhiDot (rad)
                    SimResultsFILE.write(str(self.NPbody_dphidt[bodyIndex]) + " ")
                    # PhiDot (deg)
                    SimResultsFILE.write(str(self.NPbody_dphidt[bodyIndex] * 180.0 / math.pi) + " ")
                    # Xdotdot Ydotdot
                    SimResultsFILE.write(str(self.NPbody_d2rdt2[bodyIndex])[1:-1] + " ")
                    # PhiDotDot (rad)
                    SimResultsFILE.write(str(self.NPbody_d2phidt2[bodyIndex]) + " ")
                    # PhiDotDot (deg)
                    SimResultsFILE.write(str(self.NPbody_d2phidt2[bodyIndex] * 180.0 / math.pi) + " ")
                # End of if timeIndex >= 0

                # Write all the points position and positionDot in the body
                for index in range(self.NPnumJointPointsInBody[bodyIndex]):
                    if timeIndex >= 0:
                        # Write Point Name vertically
                        if VerticalCounter < len(VerticalHeaders[ColumnCounter]):
                            character = VerticalHeaders[ColumnCounter][VerticalCounter]
                            if character in "0123456789":
                                SimResultsFILE.write("'" + character + "' ")
                            else:
                                SimResultsFILE.write(character + " ")
                        else:
                            SimResultsFILE.write("- ")

                        ColumnCounter += 1
                        # Point X Y
                        SimResultsFILE.write(str(self.NPpoint_r[bodyIndex, index])[1:-1] + " ")
                        # Point Xdot Ydot
                        SimResultsFILE.write(str(self.NPpoint_drdt[bodyIndex, index])[1:-1] + " ")
                    # end of if timeIndex >= 0

            # Next bodyIndex

            # Write the Lambdas
            if self.numConstraints > 0:
                if timeIndex >= 0:
                    # Lambda
                    for bodyIndex in range(self.numBodies-1):
                        # Write the Body Name vertically
                        if VerticalCounter < len(VerticalHeaders[ColumnCounter]):
                            character = VerticalHeaders[ColumnCounter][VerticalCounter]
                            if character in "0123456789":
                                SimResultsFILE.write("'" + character + "' ")
                            else:
                                SimResultsFILE.write(character + " ")
                        else:
                            SimResultsFILE.write("- ")

                        ColumnCounter += 1
                        SimResultsFILE.write(str(self.Lambda[bodyIndex*2]) + " " + str(self.Lambda[bodyIndex*2 + 1]) + " ")
                # end of if timeIndex >= 0

            # Compute kinetic and potential energies in micro-Joules
            # REMEMBER: we work in mm-kg-s system
            totKinEnergy = 0
            for bodyIndex in range(1, self.numBodies):
                # Kinetic Energy 1/2 mv^2 + 1/2 I omega^2
                linKinEnergy = 0.5 * (
                             self.NPMassArray[(bodyIndex - 1) * 3] *
                            (self.NPbody_drdt[bodyIndex, 0] ** 2 +
                             self.NPbody_drdt[bodyIndex, 1] ** 2))
                angKinEnergy = 0.5 * (
                            self.NPMassArray[(bodyIndex - 1) * 3 + 2] *
                            self.NPbody_dphidt[bodyIndex] ** 2)

                if timeIndex >= 0:
                    # Body Name vertically
                    if VerticalCounter < len(VerticalHeaders[ColumnCounter]):
                        character = VerticalHeaders[ColumnCounter][VerticalCounter]
                        if character in "0123456789":
                            SimResultsFILE.write("'" + character + "' ")
                        else:
                            SimResultsFILE.write(character + " ")
                    else:
                        SimResultsFILE.write("- ")
                    ColumnCounter += 1
                    SimResultsFILE.write(str(linKinEnergy) + " ")
                    SimResultsFILE.write(str(angKinEnergy) + " ")
                # end of if timeIndex >= 0

                totKinEnergy += linKinEnergy + angKinEnergy
            # Next bodyIndex

            # Currently, calculate only gravitational potential energy
            # Calculate it at t=0 (time index == -1) so that we have a zero reference
            totPotEnergy = 0
            forceIndex = -1
            for forceObj in self.forceList:
                forceIndex += 1
                # Potential Energy
                if forceObj.forceType == "Gravity":
                    for bodyIndex in range(1, self.numBodies):
                        potEnergy = -self.NPWeight[bodyIndex].dot(self.NPbody_r[bodyIndex])
                        if timeIndex == -1:
                            self.NPpotEnergyZeroPoint[bodyIndex] = potEnergy
                        else:
                            potEnergy -= self.NPpotEnergyZeroPoint[bodyIndex]
                            totPotEnergy += potEnergy

                            # Body Name vertically
                            if VerticalCounter < len(VerticalHeaders[ColumnCounter]):
                                character = VerticalHeaders[ColumnCounter][VerticalCounter]
                                if character in "0123456789":
                                    SimResultsFILE.write("'" + character + "' ")
                                else:
                                    SimResultsFILE.write(character + " ")
                            else:
                                SimResultsFILE.write("- ")
                            ColumnCounter += 1

                            SimResultsFILE.write(str(potEnergy) + " ")
                # End of if force is gravity
            # next forceObject

            if timeIndex == -1:
                VerticalCounter = 0
            else:
                SimResultsFILE.write(str(totKinEnergy) + " ")
                SimResultsFILE.write(str(totPotEnergy) + " ")
                SimResultsFILE.write("\n")
                VerticalCounter += 1
        # Next timeIndex

        # Print out the joint errors
        SimResultsFILE.write("\n")
        SimResultsFILE.write("Error: \n")
        for twoLines in ["first", "second"]:
            if twoLines == "first":
                SimResultsFILE.write("ABS: ")
            else:
                SimResultsFILE.write("REL: ")
            bodyIndex = -1
            for bodyObj in self.bodyGroup:
                bodyIndex += 1
                if bodyIndex > 0:
                    SimResultsFILE.write("- - - - - - - - - - - - - ")

                    # Write all the points position and positionDot in the body
                    for JointNumber in range(self.NPnumJointPointsInBody[bodyIndex]):
                        SimResultsFILE.write("- ")
                        # Find the same joint in the other body
                        otherIndex = -1
                        for otherBody in self.bodyGroup:
                            otherIndex += 1
                            if bodyIndex != otherIndex:
                                for otherJoint in range(self.NPnumJointPointsInBody[otherIndex]):
                                    if bodyObj.jointNameList[JointNumber] == otherBody.jointNameList[otherJoint]:
                                        diff1 = math.fabs(self.NPpoint_r[bodyIndex, JointNumber][0] - \
                                                self.NPpoint_r[otherIndex, otherJoint][0])
                                        if twoLines == "second":
                                            diff1 /= math.fabs(self.NPpoint_r[bodyIndex, JointNumber][0] + \
                                                    self.NPpoint_r[otherIndex, otherJoint][0])
                                            diff1 *= 50

                                        diff2 = math.fabs(self.NPpoint_r[bodyIndex, JointNumber][1] - \
                                               self.NPpoint_r[otherIndex, otherJoint][1])
                                        if twoLines == "second":
                                            diff2 /= math.fabs(self.NPpoint_r[bodyIndex, JointNumber][1] + \
                                                   self.NPpoint_r[otherIndex, otherJoint][1])
                                            diff2 *= 50

                                        diff3 = math.fabs(self.NPpoint_drdt[bodyIndex, JointNumber][0] - \
                                               self.NPpoint_drdt[otherIndex, otherJoint][0])
                                        if twoLines == "second":
                                            diff3 /= math.fabs(self.NPpoint_drdt[bodyIndex, JointNumber][0] + \
                                                   self.NPpoint_drdt[otherIndex, otherJoint][0])
                                            diff3 *= 50

                                        diff4 = math.fabs(self.NPpoint_drdt[bodyIndex, JointNumber][1] - \
                                               self.NPpoint_drdt[otherIndex, otherJoint][1])
                                        if twoLines == "second":
                                            diff4 /= math.fabs(self.NPpoint_drdt[bodyIndex, JointNumber][1] + \
                                                   self.NPpoint_drdt[otherIndex, otherJoint][1])
                                            diff4 *= 50

                                        SimResultsFILE.write(str(diff1) + " ")
                                        SimResultsFILE.write(str(diff2) + " ")
                                        SimResultsFILE.write(str(diff3) + " ")
                                        SimResultsFILE.write(str(diff4) + " ")
                                # next otherJoint
                        # next otherBody
            # Next bodyObj
            SimResultsFILE.write("\n")
        # Next twoLines

        SimResultsFILE.close()
    #  =========================================================================
