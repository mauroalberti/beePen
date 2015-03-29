# beePen
# conception by Mauro Dedonatis
# code by Mauro Alberti
#
#
#
# Ccontains code adapted from:
#
# 'Freehand Editing  Plugin', Copyright (C) Pavol Kapusta
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




from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *

import resources


from beePen_QWidget import beePen_QWidget
from freehandeditingtool import FreehandEditingTool



class beePen_gui( object ):

    def __init__(self, interface):

        self.interface = interface
        self.main_window = self.interface.mainWindow()
        self.canvas = self.interface.mapCanvas()        
        self.active = False
        

    def initGui(self):
        
        self.beePen_QAction = QAction(QIcon(":/plugins/beePen/icon.png"), "beePen", self.interface.mainWindow())
        self.beePen_QAction.setWhatsThis( "Graphic annotations for field work" ) 
        self.beePen_QAction.triggered.connect( self.open_beePen_widget )
        self.interface.addPluginToMenu("beePen", self.beePen_QAction)
        self.interface.digitizeToolBar().addAction(self.beePen_QAction)

        self.beePen_pencil_QAction = QAction(QIcon(":/plugins/beePen/pencil.png"), "beePencil", self.interface.mainWindow())
        self.beePen_pencil_QAction.setWhatsThis( "Pencil for graphic annotations" ) 
        self.beePen_pencil_QAction.setToolTip("Pencil tool for beePen")
        self.beePen_pencil_QAction.setEnabled(False)
        self.interface.digitizeToolBar().addAction(self.beePen_pencil_QAction)

        self.beePen_pencil_QAction.activated.connect(self.freehandediting)
        self.interface.currentLayerChanged['QgsMapLayer*'].connect(self.toggle)
        self.canvas.mapToolSet['QgsMapTool*'].connect(self.deactivate_pencil)
              
              
        self.color_name = "blue"
        self.pencil_width = 5    
        self.tool = FreehandEditingTool(self.canvas, self.color_name, self.pencil_width)
        

    def get_current_color_name(self):
        
        return self.beePen_QWidget.pen_color_QComboBox.currentText()


    def get_pencil_width(self):
        
        return  int(self.beePen_QWidget.pen_width_QComboBox.currentText())
    
        
    def open_beePen_widget(self):

        beePen_DockWidget = QDockWidget( 'beePen', self.interface.mainWindow() )        
        beePen_DockWidget.setAttribute(Qt.WA_DeleteOnClose)
        beePen_DockWidget.setAllowedAreas( Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea )        
        self.beePen_QWidget = beePen_QWidget( self.canvas )        
        beePen_DockWidget.setWidget( self.beePen_QWidget )      
        self.interface.addDockWidget( Qt.BottomDockWidgetArea, beePen_DockWidget )



    def freehandediting(self):
        
        self.canvas.setMapTool(self.tool)
        self.beePen_pencil_QAction.setChecked(True)
        self.tool.rbFinished['QgsGeometry*'].connect(self.createFeature)
        self.active = True
            
    
    def toggle(self):
        
        layer = self.canvas.currentLayer()
        if layer is None:
            return

        #Decide whether the plugin button/menu is enabled or disabled
        if layer.isEditable() and layer.geometryType() == QGis.Line:
            
            self.beePen_pencil_QAction.setEnabled(True)

            try:  # remove any existing connection first
                layer.editingStopped.disconnect(self.toggle)
            except TypeError:  # missing connection
                pass
            
            layer.editingStopped.connect(self.toggle)
            try:
                layer.editingStarted.disconnect(self.toggle)
            except TypeError:  # missing connection
                pass
        else:
            
            self.beePen_pencil_QAction.setEnabled(False)

            if layer.type() == QgsMapLayer.VectorLayer and layer.geometryType() == QGis.Line:
                
                try:  # remove any existing connection first
                    layer.editingStarted.disconnect(self.toggle)
                except TypeError:  # missing connection
                    pass
                
                layer.editingStarted.connect(self.toggle)
                
                try:
                    layer.editingStopped.disconnect(self.toggle)
                except TypeError:  # missing connection
                    pass
 

    def createFeature(self, geom):
        
        settings = QSettings()

        layer = self.canvas.currentLayer()
        if layer is None:
            return
        
        renderer = self.canvas.mapRenderer()
        layerCRSSrsid = layer.crs().srsid()
        projectCRSSrsid = renderer.destinationCrs().srsid()
        provider = layer.dataProvider()
        f = QgsFeature()

        if layer.crs().projectionAcronym() == "longlat":
            tolerance = 0.000
        else:
            tolerance = settings.value("/beePen/tolerance",
                                       0.000, type=float)

        #On the Fly reprojection.
        if layerCRSSrsid != projectCRSSrsid:
            geom.transform(QgsCoordinateTransform(projectCRSSrsid,
                                                  layerCRSSrsid))
        s = geom.simplify(tolerance)

        f.setGeometry(s)

        # add attribute fields to feature
        fields = layer.pendingFields()

        f.initAttributes(fields.count())
        for i in range(fields.count()):
            if provider.defaultValue(i):
                f.setAttribute(i, provider.defaultValue(i))

        layer.beginEditCommand("Feature added")
        layer.addFeature(f)
        layer.endEditCommand()

                
    def deactivate_pencil(self):
        
        self.beePen_pencil_QAction.setChecked(False)
        if self.active:
            self.tool.rbFinished['QgsGeometry*'].disconnect(self.createFeature)
        self.active = False
                        
                       
    def unload(self):

        self.interface.digitizeToolBar().removeAction(self.beePen_QAction)
        self.interface.digitizeToolBar().removeAction(self.beePen_pencil_QAction)
        
        self.interface.removePluginMenu( "beePen", self.beePen_QAction )

        
        
               

