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
import FreeCADGui as CADGui

import SimTools as ST
import SimMakes as SM
import SimViewProvider as SV
import SimTaskPanels as SP

from PySide import QtCore

# =============================================================================
class CommandSimGlobalClass:
    """The simGlobal command definition"""
    #  -------------------------------------------------------------------------
    def GetResources(self):
        """Called by FreeCAD when 'CADGui.addCommand' is run in InitGui.py
        Returns a dictionary defining the icon, the menu text and the tooltip"""

        return {
            "Pixmap": SM.getIconPath("icons", "Icon2n.png"),
            "MenuText": QtCore.QT_TRANSLATE_NOOP("SimGlobalAlias", "Initialise PlanarMechSim"),
            "ToolTip": QtCore.QT_TRANSLATE_NOOP("SimGlobalAlias", "Initialises the PlanarMechSim workbench"),
        }
    #  -------------------------------------------------------------------------
    def IsActive(self):
        """Determine if the command/icon must be active or greyed out
        Only activate it if we have an Assembly model to use"""

        # Return True if we have an Assembly FreeCAD model document which is loaded and Active
        if CAD.ActiveDocument is None:
            CAD.Console.PrintErrorMessage("No active document is loaded into FreeCAD for PlanarMechSim to use")
            return False

        # Check that we at least have an Assembly Object
        Found = False
        for obj in CAD.ActiveDocument.Objects:
            if hasattr(obj, "Type") and obj.Type == 'Assembly':
                Found = True
                break
        if not Found:
            CAD.Console.PrintErrorMessage("No Assembly Model found for PlanarMechSim to use")
            return False

        # Check that we at least have two LinkGroup bodies
        Found = 0
        for obj in CAD.ActiveDocument.Objects:
            if hasattr(obj, "TypeId") and obj.TypeId == 'App::LinkGroup':
                Found += 1
        if Found < 2:
            CAD.Console.PrintErrorMessage("There must be at least two LinkGroups (SimBodyXX) for PlanarMechSim to use")
            return False

        # Check that we don't already have a simGlobal object
        for obj in CAD.ActiveDocument.Objects:
            if hasattr(obj, "Name") and obj.Name == "SimGlobal":
                return False

        return True
    #  -------------------------------------------------------------------------
    def Activated(self):
        """Called when the create simGlobal command is run by either pressing
        the tool Icon, or running it from one of the available menus.
        We create the SimGlobal and set it to be Active"""

        # This is where we create a new empty simGlobal
        SM.makeSimGlobal()
    #  -------------------------------------------------------------------------
    def __getstate__(self):
        return
    #  -------------------------------------------------------------------------
    def __setstate__(self, state):
        return
# =============================================================================
class CommandSimSolverClass:
    """The Sim Solver command definition"""
    #  -------------------------------------------------------------------------
    def GetResources(self):
        """Called by FreeCAD when 'CADGui.addCommand' is run in InitGui.py
        Returns a dictionary defining the icon, the menu text and the tooltip"""

        return {
            "Pixmap": SM.getIconPath("icons", "Icon7n.png"),
            "MenuText": QtCore.QT_TRANSLATE_NOOP("SimSolverAlias", "Run the analysis"),
            "ToolTip": QtCore.QT_TRANSLATE_NOOP("SimSolverAlias", "Run the Planar Mechanical Simulator analysis"),
        }
    #  -------------------------------------------------------------------------
    def IsActive(self):
        """Determine if the command/icon must be active or greyed out"""

        return ST.getallObjects() is not None
    #  -------------------------------------------------------------------------
    def Activated(self):
        """Called when the Solver command is run"""

        # Re-use any existing solver object
        for sObject in CAD.ActiveDocument.Objects:
            if "SimSolver" in sObject.Name:
                solverObject = sObject
                CADGui.ActiveDocument.setEdit(solverObject.Name)
                return

        # Make a new solver object
        SM.makeSimSolver("SimSolver")
        for sObject in CAD.ActiveDocument.Objects:
            if "SimSolver" in sObject.Name:
                solverObject = sObject
                CADGui.ActiveDocument.setEdit(solverObject.Name)
                return

        ST.Mess("Solver Object creation failed")
    #  -------------------------------------------------------------------------
    def __getstate__(self):
        return
    #  -------------------------------------------------------------------------
    def __setstate__(self, state):
        return
# =============================================================================
class CommandSimAnimationClass:
    """The Sim Animation command definition"""
    def __init__(self):

        self.SimDocument = CAD.ActiveDocument
        self.animationDocument = CAD.ActiveDocument

    #  -------------------------------------------------------------------------
    def GetResources(self):
        """Called by FreeCAD when 'CADGui.addCommand' is run in InitGui.py
        Returns a dictionary defining the icon, the menu text and the tooltip"""

        return {
            "Pixmap": SM.getIconPath("icons", "Icon8n.png"),
            "MenuText": QtCore.QT_TRANSLATE_NOOP("SimAnimationAlias", "Do Animation"),
            "ToolTip": QtCore.QT_TRANSLATE_NOOP("SimAnimationAlias", "Animates the motion of the bodies as determined by the analysis"),
        }

    #  -------------------------------------------------------------------------
    def IsActive(self):
        """Determine if there are already some results stored in the solver object
        i.e. Determine if the animate command/icon must be active or greyed out"""

        return ST.getallObjects().SimResultsValid
    #  -------------------------------------------------------------------------
    def Activated(self):
        """Called when the Animation command is run"""

        # Get the identity of the Sim document (which is the active document on entry)
        self.SimDocument = CAD.ActiveDocument

        # Set an existing "Animation" document active or create a new document if it does not exist yet
        if "Animation" in CAD.listDocuments():
            CAD.setActiveDocument("Animation")
        else:
            CAD.newDocument("Animation")

        self.animationDocument = CAD.ActiveDocument

        # Add the ground object to the animation view (and forget about it)
        groundObj = self.SimDocument.findObjects(Name="^LinkGroup$")[0]
        animObj = self.animationDocument.addObject("Part::FeaturePython", "Ani_SimGround")
        animObj.Shape = groundObj.Shape
        SV.ViewProviderSimAnimateClass(animObj.ViewObject)

        # Generate the list of bodies to be animated and
        # create an object for each, with their shapes, in the animationDocument
        solverObj = self.SimDocument.findObjects(Name="^SimSolver$")[0]
        for bodyName in solverObj.BodyNames:
            bodyObj = self.SimDocument.findObjects(Name="^" + bodyName + "$")[0]

            animObj = self.animationDocument.addObject("Part::FeaturePython", ("Ani_" + bodyName))
            # Add the shape to the newly created object
            animObj.Shape = bodyObj.Shape
            # Instantiate the class to handle the Gui stuff
            SV.ViewProviderSimAnimateClass(animObj.ViewObject)

        # Request the animation window zoom to be set to fit the entire system
        CADGui.SendMsgToActiveView("ViewFit")

        # Run and Edit the parameters by calling the task dialogue
        taskd = SP.TaskPanelSimAnimateClass(
            self.SimDocument,
            self.animationDocument,
        )
        CADGui.Control.showDialog(taskd)
# =============================================================================
