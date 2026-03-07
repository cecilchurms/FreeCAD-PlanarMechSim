# ********************************************************************************
# *                                                                              *
# *   This program is free software; you can redistribute it and/or modify       *
# *   it under the terms of the GNU General Public License V3.0 or later         *
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
# *                 An early version of Nikra-DAP was written by:                *
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
import FreeCAD
import FreeCADGui
from FreeCAD import Gui

global Debug

# =============================================================================
# InitGui.py
# 1. Connects the workbench to FreeCAD and FreeCADGui
# 2. Builds the graphical interface between the workbench and FreeCAD
# 3. Couples the graphical interface of FreeCAD with the functions of the workbench
# =============================================================================
class PlanarMechSim(Gui.Workbench):
    """This class encompasses the whole PlanarMechSim workbench"""
    #  -------------------------------------------------------------------------
    def __init__(self):
        """Called on startup of FreeCAD"""

        # We make use of getIconPath which must be located in a separate module [i.e. SimMakes.py in this case]
        # it simply returns os.path.join(os.path.dirname(__file__), iconDir, iconName)
        # We define this method in a separate module so that the __file__ variable is valid
        # which makes the program portable as to where in the file system it is located
        from SimMakes import getIconPath

        # Set up the text for the Sim workbench option, the PlanarMechSim icon, and the tooltip
        self.__class__.Icon = getIconPath("Resources/Icons", "Icon1n.png")
        self.__class__.MenuText = "PlanarMechSim"
        self.__class__.ToolTip = "Mechanical objects simulator workbench based on Nikravesh's solver"
    #  -------------------------------------------------------------------------
    def Initialize(self):
        """Called on the first selection of the PlanarMechSim Workbench
        and couples the main PlanarMechSim functions to the FreeCAD interface"""

        import SimCommands as SimCommands

        # Add the commands to FreeCAD's list of functions
        FreeCADGui.addCommand("SimGlobalAlias", SimCommands.CommandSimGlobalClass())
        FreeCADGui.addCommand("SimSolverAlias", SimCommands.CommandSimSolverClass())
        FreeCADGui.addCommand("SimAnimationAlias", SimCommands.CommandSimAnimationClass())

        # Create a toolbar item with the Sim commands (icons)
        self.appendToolbar("PlanarMechSim Commands", self.MakeCommandList())

        # Create a drop-down menu item for the menu bar
        self.appendMenu("PlanarMechSim", self.MakeCommandList())
    #  -------------------------------------------------------------------------
    def ContextMenu(self, recipient):
        """This is executed whenever the user right-clicks on screen
        'recipient'=='view' when mouse is in the VIEW window
        'recipient'=='tree' when mouse is in the TREE window
        We currently do no use either flag"""

        # Append the Sim commands to the existing context menu
        self.appendContextMenu("PlanarMechSim Commands", self.MakeCommandList())
    #  -------------------------------------------------------------------------
    def MakeCommandList(self):
        """Define a list of our aliases for all the Sim main functions"""

        return [
            "SimGlobalAlias",
            "SimSolverAlias",
            "Separator",
            "SimAnimationAlias"
        ]
    #  -------------------------------------------------------------------------
    def Activated(self):
        """Called when the PlanarMechSim workbench is run"""
    #  -------------------------------------------------------------------------
    def Deactivated(self):
        """This function is executed each time the PlanarMechSim workbench is stopped"""
    #  -------------------------------------------------------------------------
    def GetClassName(self):
        """This function is mandatory if this is a full FreeCAD workbench
        The returned string should be exactly 'Gui::PythonWorkbench'
        This enables FreeCAD to ensure that the stuff in its 'Mod' folder
        is a valid workbench and not just rubbish"""

        return "Gui::PythonWorkbench"
# =============================================================================
# Run when FreeCAD detects a workbench folder in its 'Mod' folder
# Add the workbench to the list of workbenches and initialize it
# =============================================================================
FreeCADGui.addWorkbench(PlanarMechSim())
