from __future__ import absolute_import
#-----------------------------------------------------------
#
#
#   beePen
#       conception by Mauro Dedonatis
#       implementation by Mauro Alberti
#
#   Contains code adapted from:
#   'Freehand Editing  Plugin', Copyright (C) Pavol Kapusta
#
#
#-----------------------------------------------------------
#
# licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#---------------------------------------------------------------------

from builtins import object
import os

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *

from qgis.PyQt.uic import loadUi

from qgis.core import *

from . import resources  # Note: maintain even if it is reported as unused

from .beePen_QWidget import beePen_QWidget, isAnnotationLayer
from .qt_utils.qt_utils import warn
from .freehandeditingtool import FreehandEditingTool, EraserTool


_plugin_name_ = "beePen"
_plugin_directory_ = os.path.dirname(__file__)


class beePen_gui(object):

    def __init__(self, interface):

        self.interface = interface
        self.canvas = self.interface.mapCanvas()        
        self.pencil_active = False
        self.plugin_name = _plugin_name_
        self.plugin_dir_pth = _plugin_directory_

        self.pen_widths = [0.01, 0.02, 0.05, 0.08, 0.1, 0.2, 0.5, 1, 5, 10, 25, 50, 100, 250, 500, 750, 1000]
        self.default_pen_width = 1
        self.pen_transparencies = [0, 25, 50, 75]

    def initGui(self):

        self.isbeePenOpen = False
        self.pencil_tool = None

        self.beePen_QAction = QAction(
            QIcon(":/plugins/%s/icons/icon.png" % self.plugin_name),
            self.plugin_name,
            self.interface.mainWindow())
        self.beePen_QAction.setWhatsThis("Graphic annotations for field work") 
        self.beePen_QAction.triggered.connect(self.open_beePen_widget)
        self.interface.addPluginToMenu(self.plugin_name, self.beePen_QAction)
        self.interface.digitizeToolBar().addAction(self.beePen_QAction)
        
        self.beePen_pencil_QAction = QAction(
            QIcon(":/plugins/%s/icons/pencil.png" % self.plugin_name),
            "beePencil",
            self.interface.mainWindow())
        self.beePen_pencil_QAction.setWhatsThis("Pencil for graphic annotations") 
        self.beePen_pencil_QAction.setToolTip("Pencil tool for %s" % self.plugin_name)
        self.beePen_pencil_QAction.triggered.connect(self.freehandediting)
        self.beePen_pencil_QAction.setEnabled(False)
        self.interface.digitizeToolBar().addAction(self.beePen_pencil_QAction)

        self.interface.currentLayerChanged['QgsMapLayer*'].connect(self.setup_pencil_eraser)

        self.canvas.mapToolSet.connect(self.deactivate_pencil)

        self.beePen_rubber_QAction = QAction(
            QIcon(":/plugins/%s/icons/rubber.png" % self.plugin_name),
            "beeRubber",
            self.interface.mainWindow())
        self.beePen_rubber_QAction.setWhatsThis("Rubber for graphic annotations") 
        self.beePen_rubber_QAction.setToolTip("Rubber tool for %s" % self.plugin_name)
        self.beePen_rubber_QAction.triggered.connect(self.erase_features)
        self.beePen_rubber_QAction.setEnabled(False)
        self.interface.digitizeToolBar().addAction(self.beePen_rubber_QAction)

    def open_beePen_widget(self):
        
        if self.isbeePenOpen:
            warn(self.interface.mainWindow(),
                 self.plugin_name,
                 "%s is already open" % self.plugin_name)
            return

        beePen_DockWidget = QDockWidget(self.plugin_name, self.interface.mainWindow())
        beePen_DockWidget.setAttribute(Qt.WA_DeleteOnClose)
        beePen_DockWidget.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea)

        self.beePen_QWidget = beePen_QWidget(
            self.interface,
            self.plugin_name,
            self.plugin_dir_pth,
            self.pen_widths,
            self.default_pen_width,
            self.pen_transparencies)
        
        beePen_DockWidget.setWidget(self.beePen_QWidget)
        beePen_DockWidget.destroyed.connect(self.closeEvent)        
        self.interface.addDockWidget(Qt.BottomDockWidgetArea, beePen_DockWidget)

        self.isbeePenOpen = True

        self.setup_pencil_eraser()

    def closeEvent(self):
        
        self.isbeePenOpen = False
        self.beePen_pencil_QAction.setEnabled(False)
        self.beePen_rubber_QAction.setEnabled(False)

    def freehandediting(self):
        
        if not self.isbeePenOpen:
            warn(self.interface.mainWindow(),
                 self.plugin_name,
                 "First launch %s" % self.plugin_name)
            return

        self.pencil_tool = FreehandEditingTool(
            self.interface,
            self.canvas,
            self.beePen_QWidget.color_name,
            self.beePen_QWidget.pencil_width
        )
        self.beePen_QWidget.style_signal.connect(self.pencil_tool.update_pen_style)
        self.canvas.setMapTool(self.pencil_tool)
        self.beePen_pencil_QAction.setChecked(True)
        self.pencil_tool.rbFinished.connect(self.createFeature)
        self.pencil_active = True

    def setup_pencil_eraser(self):

        if not self.isbeePenOpen:
            self.beePen_pencil_QAction.setEnabled(False)
            self.beePen_rubber_QAction.setEnabled(False)
        else:
            layer = self.canvas.currentLayer()
            if layer is None or not isAnnotationLayer(layer):
                self.beePen_pencil_QAction.setEnabled(False)
                self.beePen_rubber_QAction.setEnabled(False)
            else:
                self.beePen_pencil_QAction.setEnabled(True)
                self.beePen_rubber_QAction.setEnabled(True)

    def createFeature(self, geom):

        if geom is None:
            return

        layer = self.canvas.currentLayer()
        if layer is None:
            del geom
            return

        if not isAnnotationLayer(layer):
            del geom
            warn(self.interface.mainWindow(),
                 self.plugin_name,
                 "The current active layer is not an annotation layer")
            return

        # open note window for inputting the note text

        note = ''
        if self.beePen_QWidget.note_QCheckBox.isChecked():
            noteDialog = NoteDialog()
            if noteDialog.exec_():
                note = noteDialog.note_plainTextEdit.toPlainText()

        layer.startEditing()

        map_settings = self.canvas.mapSettings()

        layer_crs = layer.crs()
        project_crs = map_settings.destinationCrs()

        layerCRSSrsid = layer_crs.srsid()
        projectCRSSrsid = project_crs.srsid()
        feature = QgsFeature()

        # on-the-fly re-projection

        if layerCRSSrsid != projectCRSSrsid:
            geom.transform(
                QgsCoordinateTransform(
                    project_crs,
                    layer_crs,
                    QgsProject.instance()))

        # simplification and smoothing section

        settings = QSettings()
        simplify_tolerance=settings.value("/%s/simplify_tolerance" % self.plugin_name, 0.0, type=float)
        smooth_iterations=settings.value("/%s/smooth_iterations" % self.plugin_name, 0, type=int)
        smooth_offset=settings.value("/%s/smooth_offset" % self.plugin_name, 0.25, type=float)
        smooth_mindistance=settings.value("/%s/smooth_mindistance" % self.plugin_name, -1.0, type=float)
        smooth_maxangle=settings.value("/%s/smooth_maxangle" % self.plugin_name, 180.0, type=float)

        # let the feature unchanged when CRS is in polar coordinates

        if layer.crs().projectionAcronym() == "longlat":
            simplify_tolerance = 0.0
            smooth_iterations = 0

        if simplify_tolerance:
            s = geom.simplify(simplify_tolerance)
        else:
            s = geom

        if smooth_iterations:
            s = s.smooth(
                iterations=smooth_iterations,
                offset=smooth_offset,
                minimumDistance=smooth_mindistance,
                maxAngle=smooth_maxangle
            )

        feature.setGeometry(s)

        del geom

        # add attribute fields to feature

        fields = layer.fields()
        feature.initAttributes(fields.count())
        record_values = [self.beePen_QWidget.pencil_width,
                         self.beePen_QWidget.color_name,
                         note]
        for ndx, value in enumerate(record_values):
            feature.setAttribute(ndx, value)

        layer.addFeature(feature)

        layer.commitChanges()

    def deleteFeatures(self, geom):

        if geom is None:
            return

        layer = self.canvas.currentLayer()
        if layer is None:
            del geom
            return

        if not isAnnotationLayer(layer):
            del geom
            warn(self.interface.mainWindow(),
                 self.plugin_name,
                 "The current active layer is not an annotation layer")
            return

        map_settings = self.canvas.mapSettings()

        layer_crs = layer.crs()
        layerCRSSrsid = layer_crs.srsid()

        project_crs = map_settings.destinationCrs()
        projectCRSSrsid = project_crs.srsid()

        if layer.crs().projectionAcronym() == "longlat":
            tolerance = 0.000
        else:
            settings = QSettings()
            tolerance = settings.value("/%s/tolerance" % self.plugin_name,
                                       0.000, type=float)

        # on-the-fly reprojection
        if layerCRSSrsid != projectCRSSrsid:
            geom.transform(QgsCoordinateTransform(project_crs,
                                                  layer_crs,
                                                  QgsProject.instance()))

        simpl_geom = geom.simplify(tolerance)

        # delete intersected features from layer
        layer.startEditing()
        for feat in layer.getFeatures():
            target_geom = feat.geometry()
            if target_geom.intersects(simpl_geom):
                layer.beginEditCommand("Feature deleted")
                layer.deleteFeature(feat.id())
                layer.endEditCommand()
        layer.commitChanges()

    def deactivate_pencil(self, mapTool = None):

        if mapTool is self.pencil_tool:
            return

        self.beePen_pencil_QAction.setChecked(False)
        if self.pencil_active:
            self.pencil_tool.rbFinished.disconnect(self.createFeature)
        self.pencil_active = False

    def erase_features(self):

        if not self.isbeePenOpen:
            warn(self.interface.mainWindow(),
                 self.plugin_name,
                 "First launch %s" % self.plugin_name)
            return

        self.eraser_tool = EraserTool(self.interface, self.canvas)

        self.canvas.setMapTool(self.eraser_tool)
        self.beePen_rubber_QAction.setChecked(True)
        self.eraser_tool.rbFinished.connect(self.deleteFeatures)
        self.eraser_active = True

    def unload(self):

        self.interface.digitizeToolBar().removeAction(self.beePen_QAction)
        self.interface.digitizeToolBar().removeAction(self.beePen_pencil_QAction)
        self.interface.digitizeToolBar().removeAction(self.beePen_rubber_QAction)

        self.interface.removePluginMenu(self.plugin_name, self.beePen_QAction)


class NoteDialog(QDialog):

    def __init__(self):

        super(NoteDialog, self).__init__()
        loadUi(os.path.join(_plugin_directory_, 'note.ui'), self)
        self.show()

