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
# *         Nikra-DAP thus underwent a major re-write and was enlarged           *
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

import SimMain

from PySide import QtGui, QtCore
import Part
import math
import numpy as np
from os import path, getcwd
from PySide.QtWidgets import QApplication, QTableWidget, QTableWidgetItem

Debug = False
# =============================================================================
class TaskPanelSimSolverClass:
    """Taskpanel for Executing Sim Solver User Interface"""
    #  -------------------------------------------------------------------------
    def __init__(self, solverTaskObject):
        """Run on first instantiation of a TaskPanelSimSolver class"""

        self.solverTaskObject = solverTaskObject
        solverTaskObject.Proxy = self

        # Get the directory name to store results in
        if solverTaskObject.Directory == "":
            solverTaskObject.Directory = getcwd()

        # Load the taskDialog form information
        ui_path = path.join(path.dirname(__file__), "TaskPanelSimSolver.ui")
        self.form = CADGui.PySideUic.loadUi(ui_path)

        # Set up actions on the solver button
        self.form.solveButton.clicked.connect(self.solveButtonClicked_Callback)

        # Set the time in the form
        self.form.endTime.setValue(self.solverTaskObject.TimeLength)
        self.form.reportingTime.setValue(self.solverTaskObject.DeltaTime)

        # Set the file name and directory
        self.form.checkRK45.stateChanged.connect(self.solverType_Callback())
        self.form.checkRK23.stateChanged.connect(self.solverType_Callback())
        self.form.checkDOP853.stateChanged.connect(self.solverType_Callback())
        self.form.outputDirectory.setText(self.solverTaskObject.Directory)
        self.form.outputFileName.setText(self.solverTaskObject.FileName)
        self.form.browseFileDirectory.clicked.connect(self.getFolderDirectory_Callback)

        # Set the accuracy in the form
        self.form.Accuracy.setValue(self.solverTaskObject.Accuracy)

        # Default is to output only the animation data
        self.form.outputAnimOnly.toggled.connect(self.outputAnimOnlyCheckboxChanged_Callback)
        self.form.outputAnimOnly.setEnabled(True)
        self.form.outputAnimOnly.setChecked(True)

    #  -------------------------------------------------------------------------
    def accept(self):
        """Run when we press the OK button"""

        self.solverTaskObject.DeltaTime = self.form.reportingTime.value()
        self.solverTaskObject.TimeLength = self.form.endTime.value()
        self.solverTaskObject.FileName = self.form.outputFileName.text()
        self.solverTaskObject.Accuracy = self.form.Accuracy.value()
        self.solverType_Callback()

        # Close the dialog
        Document = CADGui.getDocument(self.solverTaskObject.Document)
        Document.resetEdit()

    #  -------------------------------------------------------------------------
    def outputAnimOnlyCheckboxChanged_Callback(self):
        if self.form.outputAnimOnly.isChecked():
            self.form.outputFileLabel.setDisabled(True)
            self.form.outputFileName.setDisabled(True)
            self.form.browseFileDirectory.setDisabled(True)
            self.form.outputDirectoryLabel.setDisabled(True)
            self.form.outputDirectory.setDisabled(True)
        else:
            self.form.outputFileLabel.setEnabled(True)
            self.form.outputFileName.setEnabled(True)
            self.form.browseFileDirectory.setEnabled(True)
            self.form.outputDirectoryLabel.setEnabled(True)
            self.form.outputDirectory.setEnabled(True)
            #self.solverTaskObject.Accuracy = 9
            self.form.Accuracy.setValue(self.solverTaskObject.Accuracy)
    #  -------------------------------------------------------------------------
    def solveButtonClicked_Callback(self):
        """Call the MainSolve() method in the SimMainC class"""

        self.solverType_Callback()
        # Change the solve button to red with 'Solving' on it
        self.form.solveButton.setDisabled(True)
        self.form.solveButton.setText("Solving")

        # Do some arithmetic to allow the repaint to happen
        # before the frame becomes unresponsive due to the big maths
        self.form.solveButton.repaint()
        self.form.solveButton.update()

        # Do a Delay to give the colour time
        t = 0.0
        for f in range(1000000):
            t += f/10.0

        self.form.solveButton.repaint()
        self.form.solveButton.update()

        # return the parameters in the form to the Main Solver
        self.solverTaskObject.Directory = self.form.outputDirectory.text()
        if self.form.outputAnimOnly.isChecked():
            self.solverTaskObject.FileName = "-"
        else:
            self.solverTaskObject.FileName = self.form.outputFileName.text()

        self.solverTaskObject.TimeLength = self.form.endTime.value()
        self.solverTaskObject.DeltaTime = self.form.reportingTime.value()
        self.solverTaskObject.Accuracy = self.form.Accuracy.value()

        # Instantiate the SimMainC class and run the solver
        self.SimMainC_Instance = SimMain.SimMainC(self.solverTaskObject.TimeLength,
                                                     self.solverTaskObject.DeltaTime,
                                                     self.solverTaskObject.Accuracy,
                                                     self.form.correctInitial.isChecked())
        if self.SimMainC_Instance.initialised is True:
            self.SimMainC_Instance.MainSolve()

        # Return the solve button to green with 'Solve' on it
        self.form.solveButton.setText("Solve")
        self.form.solveButton.setEnabled(True)

        # Close the dialog
        Document = CADGui.getDocument(self.solverTaskObject.Document)
        Document.resetEdit()

    #  -------------------------------------------------------------------------
    def getFolderDirectory_Callback(self):
        """Request the directory where the .csv result files will be written"""

        self.solverTaskObject.Directory = QtGui.QFileDialog.getExistingDirectory()
        self.form.outputDirectory.setText(self.solverTaskObject.Directory)
    #  -------------------------------------------------------------------------
    def solverType_Callback(self):
        """Change the LAPACK solver type"""

        if self.form.checkRK45.isChecked():
            self.solverTaskObject.SolverType = "RK45"
        elif self.form.checkRK23.isChecked():
            self.solverTaskObject.SolverType = "RK23"
        elif self.form.checkDOP853.isChecked():
            self.solverTaskObject.SolverType = "DOP853"

    #  -------------------------------------------------------------------------
    def solverTypeRK23_Callback(self):
        """Change the LAPACK solver type"""

        if self.form.checkRK23.isChecked():
            self.form.checkRK45.setChecked(False)
            self.form.checkRK23.setChecked(True)
            self.form.checkDOP853.setChecked(False)
            self.solverTaskObject.SolverType = "RK23"

    #  -------------------------------------------------------------------------
    def solverTypeDOP853_Callback(self):
        """Change the LAPACK solver type"""

        if self.form.checkDOP853.isChecked():
            self.form.checkRK45.setChecked(False)
            self.form.checkRK23.setChecked(False)
            self.form.checkDOP853.setChecked(True)
            self.solverTaskObject.SolverType = "DOP853"

    #  -------------------------------------------------------------------------
    def getStandardButtons(self):
        """ Set which button will appear at the top of the TaskDialog [Called from FreeCAD]"""

        return QtGui.QDialogButtonBox.Close
    #  -------------------------------------------------------------------------
    def __getstate__(self):
        return
    #  -------------------------------------------------------------------------
    def __setstate__(self, state):
        return

# ==============================================================================
class TaskPanelSimAnimateClass:
    """Taskpanel for Running an animation"""
    #  -------------------------------------------------------------------------
    def __init__(self, SimDocument, animationDocument):
        """Run on first instantiation of a TaskPanelSimAnimate class"""

        # Transfer the called parameters to the instance variables
        for solver in SimDocument.Objects:
            if hasattr(solver, "Name") and solver.Name == "SimSolver":
                self.solverObj = solver
                break

        self.SimDocument = SimDocument
        self.animationDocument = animationDocument

        # Here we get the list of objects from the animation document
        self.animationBodyObjects = CAD.ActiveDocument.Objects

        # Set play back period to mid-range
        self.playBackPeriod = 100  # msec

        # Load the Sim Animate ui form
        ui_Path = path.join(path.dirname(__file__), "TaskPanelSimAnimate.ui")
        self.form = CADGui.PySideUic.loadUi(ui_Path)

        # Define callback functions when changes are made in the dialog
        self.form.horizontalSlider.valueChanged.connect(self.moveObjects_Callback)
        self.form.startButton.clicked.connect(self.playStart_Callback)
        self.form.stopButton.clicked.connect(self.stopStop_Callback)
        self.form.playSpeed.valueChanged.connect(self.changePlaySpeed_Callback)

        # Fetch the animation object for all the bodies and place in a list
        self.animationBodyObj = []
        for animationBodyName in self.solverObj.BodyNames:
            self.animationBodyObj.append(self.animationDocument.findObjects(Name="^Ani_"+animationBodyName+"$")[0])

        # Load the calculated values of positions/angles from the results file
        self.Positions = np.loadtxt(path.join(self.solverObj.Directory, "SimAnimation.csv"))
        self.nTimeSteps = len(self.Positions.T[0])
        if Debug:
            ST.Mess("Positions")
            ST.PrintNp2D(self.Positions)

        # Positions matrix is:
        # timeValue : body1X body1Y body1phi : body2X body2Y body2phi : ...
        # next time tick

        # Shift all the values relative to the starting position of each body
        startTick = self.Positions[0, :]
        self.startX = []
        self.startY = []
        self.startPhi = []
        for aniBody in range(1, len(self.solverObj.BodyNames)):
            self.startX.append(startTick[aniBody * 3 - 2])
            self.startY.append(startTick[aniBody * 3 - 1])
            self.startPhi.append(startTick[aniBody * 3])
        for tick in range(self.nTimeSteps):
            thisTick = self.Positions[tick, :]
            for aniBody in range(1, len(self.solverObj.BodyNames)):
                thisTick[aniBody * 3 - 2 ] -= self.startX[aniBody-1]
                thisTick[aniBody * 3 - 1 ] -= self.startY[aniBody-1]
                thisTick[aniBody * 3 ] -= self.startPhi[aniBody-1]
            self.Positions[tick, :] = thisTick
        if Debug:
            ST.Mess("Diff Positions")
            ST.PrintNp2D(self.Positions)

        # Set up the timer parameters
        self.timer = QtCore.QTimer()
        self.timer.setInterval(self.playBackPeriod)
        self.timer.timeout.connect(self.onTimerTimeout_Callback)  # callback function after each tick

        # Set up the values displayed on the dialog
        self.form.horizontalSlider.setRange(0, self.nTimeSteps - 1)
        self.form.timeStepLabel.setText("0.000s of {0:5.3f}s".format(self.solverObj.TimeLength))
    #  -------------------------------------------------------------------------
    def reject(self):
        """Run when we press the Close button
        Closes document and sets the active document
        back to the solver document"""

        CADGui.Control.closeDialog()
        CAD.setActiveDocument(self.SimDocument.Name)
        CAD.closeDocument(self.animationDocument.Name)
    #  -------------------------------------------------------------------------
    def playStart_Callback(self):
        """Start the Qt timer when the play button is pressed"""

        self.timer.start()
    #  -------------------------------------------------------------------------
    def stopStop_Callback(self):
        """Stop the Qt timer when the stop button is pressed"""

        self.timer.stop()
    #  -------------------------------------------------------------------------
    def onTimerTimeout_Callback(self):
        """Increment the tick position in the player, looping, if requested"""

        tickPosition = self.form.horizontalSlider.value()
        tickPosition += 1
        if tickPosition >= self.nTimeSteps:
            if self.form.loopCheckBox.isChecked():
                tickPosition: int = 0
            else:
                self.timer.stop()

        # Update the slider in the dialog
        self.form.horizontalSlider.setValue(tickPosition)
    #  -------------------------------------------------------------------------
    def changePlaySpeed_Callback(self, newSpeed):
        """Alter the playback period by a factor of 1/newSpeed"""

        self.timer.setInterval(self.playBackPeriod * (1.0 / newSpeed))
    #  -------------------------------------------------------------------------
    def moveObjects_Callback(self, tick):
        """Move all the bodies to their pose at this clock tick"""

        self.form.timeStepLabel.setText(
            "{0:5.3f}s of {1:5.3f}s".format(
                tick * self.solverObj.DeltaTime,
                self.solverObj.TimeLength
            )
        )

        thisTick = self.Positions[tick, :]
        for aniBody in range(1, len(self.solverObj.BodyNames)):
            X = thisTick[aniBody * 3 - 2]
            Y = thisTick[aniBody * 3 - 1]
            Phi = thisTick[aniBody * 3 - 0]
            if Debug:
                ST.Mess("X: "+str(X)+" Y: "+str(Y)+" Phi: "+str(Phi))

            self.animationBodyObj[aniBody].Placement = \
                CAD.Placement(CAD.Vector(X, Y, 0.0),
                CAD.Rotation(CAD.Vector(0.0, 0.0, 1.0),Phi/math.pi*180.0),
                CAD.Vector(self.startX[aniBody-1], self.startY[aniBody-1], 0.0))
    #  -------------------------------------------------------------------------
    def getStandardButtons(self):
        """ Set which button will appear at the top of the TaskDialog [Called from FreeCAD]"""
        return QtGui.QDialogButtonBox.Close
    #  -------------------------------------------------------------------------
    def __getstate__(self):
        return
    #  -------------------------------------------------------------------------
    def __setstate__(self, state):
        return
# =============================================================================
