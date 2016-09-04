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

from osgeo import ogr

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

import resources  # maintain this import even if PyCharm says resources is unused

from beePen_QWidget import beePen_QWidget
from qt_utils.qt_utils import warn
from freehandeditingtool import FreehandEditingTool, EraserTool


class beePen_gui(object):

    def __init__(self, interface):

        self.interface = interface
        self.canvas = self.interface.mapCanvas()        
        self.pencil_active = False
        self.plugin_name = "beePen"        

        self.pen_widths = [0.01, 0.02, 0.05, 0.08, 0.1, 0.2, 0.5, 1, 5, 10, 25, 50, 100, 250, 500, 750, 1000]
        self.default_pen_width = 1
        self.pen_transparencies = [0, 25, 50, 75]

        self.fields_dicts = [{"name": "width", "ogr_type": ogr.OFTReal},
                             {"name": "color", "ogr_type": ogr.OFTString, "width": 20},
                             {"name": "note", "ogr_type": ogr.OFTString, "width": 100}]

    def initGui(self):

        self.isbeePenOpen = False
        self.pencil_tool = None

        self.beePen_QAction = QAction(QIcon(":/plugins/%s/icons/icon.png" % self.plugin_name),
                                            self.plugin_name,
                                            self.interface.mainWindow())
        self.beePen_QAction.setWhatsThis("Graphic annotations for field work") 
        self.beePen_QAction.triggered.connect(self.open_beePen_widget)
        self.interface.addPluginToMenu(self.plugin_name, self.beePen_QAction)
        self.interface.digitizeToolBar().addAction(self.beePen_QAction)
        
        self.beePen_pencil_QAction = QAction(QIcon(":/plugins/%s/icons/pencil.png" % self.plugin_name),
                                                   "beePencil",
                                                   self.interface.mainWindow())
        self.beePen_pencil_QAction.setWhatsThis("Pencil for graphic annotations") 
        self.beePen_pencil_QAction.setToolTip("Pencil tool for %s" % self.plugin_name)
        self.beePen_pencil_QAction.triggered.connect(self.freehandediting)
        self.beePen_pencil_QAction.setEnabled(False)
        self.interface.digitizeToolBar().addAction(self.beePen_pencil_QAction)

        self.interface.currentLayerChanged['QgsMapLayer*'].connect(self.setup_pencil_eraser)
        self.canvas.mapToolSet['QgsMapTool*'].connect(self.deactivate_pencil)   
        
        self.beePen_rubber_QAction = QAction(QIcon(":/plugins/%s/icons/rubber.png" % self.plugin_name),
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

        self.beePen_QWidget = beePen_QWidget(self.interface,
                                             self.plugin_name,
                                             self.pen_widths,
                                             self.default_pen_width,
                                             self.pen_transparencies,
                                             self.fields_dicts)
        
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

        self.pencil_tool = FreehandEditingTool(self.canvas,
                                               self.beePen_QWidget.color_name,
                                               self.beePen_QWidget.pencil_width)
        self.beePen_QWidget.style_signal.connect(self.pencil_tool.update_pen_style)
        self.canvas.setMapTool(self.pencil_tool)
        self.beePen_pencil_QAction.setChecked(True)
        self.pencil_tool.rbFinished['QgsGeometry*'].connect(self.createFeature)
        self.pencil_active = True
            

    def isAnnotationLayer(self, layer):

        # check if vector
        if layer.type() != QgsMapLayer.VectorLayer:
            return False

        # check if is a line layer
        if layer.geometryType() != QGis.Line:
            return False

        # check that contains required fields
        layer_field_names = map(lambda fld: fld.name(), layer.fields())
        expected_field_names = map(lambda rec: rec["name"], self.fields_dicts)
        return all(map(lambda exp_field_name: exp_field_name in layer_field_names, expected_field_names))


    def setup_pencil_eraser(self):

        if not self.isbeePenOpen:
            self.beePen_pencil_QAction.setEnabled(False)
            self.beePen_rubber_QAction.setEnabled(False)
        else:
            layer = self.canvas.currentLayer()
            if layer is None:
                self.beePen_pencil_QAction.setEnabled(False)
                self.beePen_rubber_QAction.setEnabled(False)
            else:
                if self.isAnnotationLayer(layer):
                    self.beePen_pencil_QAction.setEnabled(True)
                    self.beePen_rubber_QAction.setEnabled(True)
                else:
                    self.beePen_pencil_QAction.setEnabled(False)
                    self.beePen_rubber_QAction.setEnabled(False)



    """
    def setup_pencil_eraser(self):

        if not self.isbeePenOpen:
            return

        layer = self.canvas.currentLayer()
        if layer is None:
            return

        # Decide whether the plugin button/menu is enabled or disabled
        if layer.geometryType() == QGis.Line: # layer.isEditable() and

            if not self.isAnnotationLayer(layer):
                warn(self.interface.mainWindow(),
                     self.plugin_name,
                     "The current active layer is not an annotation layer")
                return

            self.beePen_pencil_QAction.setEnabled(True)
            self.beePen_rubber_QAction.setEnabled(True)

            try:  # remove any existing connection first
                layer.editingStopped.disconnect(self.setup_pencil_eraser)
            except TypeError:  # missing connection
                pass

            layer.editingStopped.connect(self.setup_pencil_eraser)
            try:
                layer.editingStarted.disconnect(self.setup_pencil_eraser)
            except TypeError:  # missing connection
                pass

        else:

            self.beePen_pencil_QAction.setEnabled(False)
            self.beePen_rubber_QAction.setEnabled(False)

            if layer.type() == QgsMapLayer.VectorLayer and layer.geometryType() == QGis.Line:

                try:  # remove any existing connection first
                    layer.editingStarted.disconnect(self.setup_pencil_eraser)
                except TypeError:  # missing connection
                    pass

                layer.editingStarted.connect(self.setup_pencil_eraser)

                try:
                    layer.editingStopped.disconnect(self.setup_pencil_eraser)
                except TypeError:  # missing connection
                    pass
    """


    def createFeature(self, geom):

        layer = self.canvas.currentLayer()
        if layer is None:
            del geom
            return

        if not self.isAnnotationLayer(layer):
            del geom
            warn(self.interface.mainWindow(),
                 self.plugin_name,
                 "The current active layer is not an annotation layer")
            return

        layer.startEditing()

        renderer = self.canvas.mapRenderer()

        layerCRSSrsid = layer.crs().srsid()
        projectCRSSrsid = renderer.destinationCrs().srsid()
        f = QgsFeature()

        if layer.crs().projectionAcronym() == "longlat":
            tolerance = 0.000
        else:
            settings = QSettings()
            tolerance = settings.value("/%s/tolerance" % self.plugin_name,
                                       0.000,
                                       type=float)

        # on the Fly reprojection.
        if layerCRSSrsid != projectCRSSrsid:
            geom.transform(QgsCoordinateTransform(projectCRSSrsid,
                                                  layerCRSSrsid))
        s = geom.simplify(tolerance)

        del geom

        f.setGeometry(s)

        # add attribute fields to feature
        fields = layer.pendingFields()

        f.initAttributes(fields.count())

        record_values = [self.beePen_QWidget.pencil_width,
                         self.beePen_QWidget.color_name]

        for ndx, value in enumerate(record_values):
            f.setAttribute(ndx, value)

        layer.addFeature(f)

        layer.commitChanges()


    def deleteFeatures(self, geom):

        layer = self.canvas.currentLayer()
        if layer is None:
            del geom
            return

        if not self.isAnnotationLayer(layer):
            del geom
            warn(self.interface.mainWindow(),
                 self.plugin_name,
                 "The current active layer is not an annotation layer")
            return

        renderer = self.canvas.mapRenderer()

        layerCRSSrsid = layer.crs().srsid()
        projectCRSSrsid = renderer.destinationCrs().srsid()

        if layer.crs().projectionAcronym() == "longlat":
            tolerance = 0.000
        else:
            settings = QSettings()
            tolerance = settings.value("/%s/tolerance" % self.plugin_name,
                                       0.000, type=float)

        # on-the-fly reprojection
        if layerCRSSrsid != projectCRSSrsid:
            geom.transform(QgsCoordinateTransform(projectCRSSrsid,
                                                  layerCRSSrsid))

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
            self.pencil_tool.rbFinished['QgsGeometry*'].disconnect(self.createFeature)
        self.pencil_active = False


    def erase_features(self):

        if not self.isbeePenOpen:
            warn(self.interface.mainWindow(),
                 self.plugin_name,
                 "First launch %s" % self.plugin_name)
            return

        self.eraser_tool = EraserTool(self.canvas)

        self.canvas.setMapTool(self.eraser_tool)
        self.beePen_rubber_QAction.setChecked(True)
        self.eraser_tool.rbFinished['QgsGeometry*'].connect(self.deleteFeatures)
        self.eraser_active = True


    def unload(self):

        self.interface.digitizeToolBar().removeAction(self.beePen_QAction)
        self.interface.digitizeToolBar().removeAction(self.beePen_pencil_QAction)
        self.interface.digitizeToolBar().removeAction(self.beePen_rubber_QAction)

        self.interface.removePluginMenu(self.plugin_name, self.beePen_QAction)

