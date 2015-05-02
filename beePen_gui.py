# beePen
# conception by Mauro Dedonatis
# implementation by Mauro Alberti
#
# Contains code adapted from:
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
from freehandeditingtool import FreehandEditingTool, EraserTool



class beePen_gui( object ):    


    def __init__(self, interface):

        self.interface = interface
        self.main_window = self.interface.mainWindow()
        self.canvas = self.interface.mapCanvas()        
        self.pencil_active = False
        self.plugin_name = "beePen"        
         
        self.pen_widths = [1,5,10,25,50,100,250,500,750,1000]
        self.pen_transparencies = [0,25,50,75]
        self.pen_colors = ["blue","red","yellow","green","orange","violet","pink"]
        

    def initGui(self):
        
        self.beePen_QAction = QAction(QIcon(":/plugins/beePen/icons/icon.png"), "beePen", self.interface.mainWindow())
        self.beePen_QAction.setWhatsThis( "Graphic annotations for field work" ) 
        self.beePen_QAction.triggered.connect( self.open_beePen_widget )
        self.interface.addPluginToMenu("beePen", self.beePen_QAction)
        self.interface.digitizeToolBar().addAction(self.beePen_QAction)
        
        self.beePen_pencil_QAction = QAction(QIcon(":/plugins/beePen/icons/pencil.png"), "beePencil", self.interface.mainWindow())
        self.beePen_pencil_QAction.setWhatsThis( "Pencil for graphic annotations" ) 
        self.beePen_pencil_QAction.setToolTip("Pencil tool for beePen")
        self.beePen_pencil_QAction.setEnabled(False)
        self.interface.digitizeToolBar().addAction(self.beePen_pencil_QAction)
    
        self.beePen_pencil_QAction.triggered.connect(self.freehandediting)
        self.interface.currentLayerChanged['QgsMapLayer*'].connect(self.toggle)
        self.canvas.mapToolSet['QgsMapTool*'].connect(self.deactivate_pencil)   
        
        self.beePen_rubber_QAction = QAction(QIcon(":/plugins/beePen/icons/rubber.png"), "beeRubber", self.interface.mainWindow())
        self.beePen_rubber_QAction.setWhatsThis( "Rubber for graphic annotations" ) 
        self.beePen_rubber_QAction.setToolTip("Rubber tool for beePen")
        self.beePen_rubber_QAction.setEnabled(False)
        self.interface.digitizeToolBar().addAction(self.beePen_rubber_QAction)

        self.beePen_rubber_QAction.triggered.connect(self.erase_features)
        
        
        self.is_beePen_widget_open = False
        self.pencil_tool = None

                    
    def open_beePen_widget(self):
        
        if self.is_beePen_widget_open:
            self.warn("beePen is already open")
            return

        beePen_DockWidget = QDockWidget( 'beePen', self.interface.mainWindow() )        
        beePen_DockWidget.setAttribute(Qt.WA_DeleteOnClose)
        beePen_DockWidget.setAllowedAreas( Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea )        
        self.beePen_QWidget = beePen_QWidget( self.canvas, self.plugin_name, self.pen_widths, self.pen_transparencies, self.pen_colors )        
        beePen_DockWidget.setWidget( self.beePen_QWidget )
        beePen_DockWidget.destroyed.connect( self.closeEvent )        
        self.interface.addDockWidget( Qt.BottomDockWidgetArea, beePen_DockWidget )
        
        self.renderer = self.create_symbol_renderer()
                
        self.is_beePen_widget_open = True
        

    def closeEvent(self):
        
        self.is_beePen_widget_open = False
        
                
    def freehandediting(self):
        
        if not self.is_beePen_widget_open:
            self.warn("First launch beePen button")
            return
                
        self.pencil_tool = FreehandEditingTool(self.canvas,
                                        self.beePen_QWidget.color_name,
                                        self.beePen_QWidget.pencil_width,                                        
                                        self.beePen_QWidget.transparency)

        self.beePen_QWidget.style_signal.connect(self.pencil_tool.update_pen_style)  
        
        self.canvas.setMapTool(self.pencil_tool)
        self.beePen_pencil_QAction.setChecked(True)
        self.pencil_tool.rbFinished['QgsGeometry*'].connect(self.createFeature)
        self.pencil_active = True
            
    
    def toggle(self):
        
        layer = self.canvas.currentLayer()
        if layer is None:
            return

        #Decide whether the plugin button/menu is enabled or disabled
        if layer.isEditable() and layer.geometryType() == QGis.Line:
            
            self.beePen_pencil_QAction.setEnabled(True)
            self.beePen_rubber_QAction.setEnabled(True)

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
            self.beePen_rubber_QAction.setEnabled(False)
            

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


 

    def create_symbol_renderer(self):

        categories = []
        symbols = []
        for pen_color in self.pen_colors:
            for pen_width in self.pen_widths:
                for transp in self.pen_transparencies:
                    symbol = QgsSymbolV2.defaultSymbol( QGis.Line )
                    symbol.setColor(QColor(pen_color))
                    symbol.setOutputUnit(QgsSymbolV2.MapUnit)
                    symbol.setWidth(pen_width)
                    symbol.setAlpha(1.0-(transp/100.0))
                    symbols.append(symbol)
                
                    category = QgsRendererCategoryV2(pen_color + "_" + str(pen_width) + "_" + str(transp), symbol, '')
                    categories.append(category)
        
        # create the renderer and assign it to a layer
        expression =  '''concat("color", '_', "width", '_', "transp")'''
        renderer = QgsCategorizedSymbolRendererV2(expression, categories)
        
        return renderer
        
        
    def createFeature(self, geom):
        
        settings = QSettings()

        layer = self.canvas.currentLayer()
        if layer is None:
            del geom
            return
        
        fields = layer.pendingFields()   
        field_names = [field.name() for field in fields]
        
        if not "width" in field_names and \
           not "transp" in field_names and \
           not "color" in field_names:
            del geom
            self.warn("The current active layer is not an annotation layer")
            return
        
        renderer = self.canvas.mapRenderer()
        
        layer.setRendererV2(self.renderer)           
        
        layerCRSSrsid = layer.crs().srsid()
        projectCRSSrsid = renderer.destinationCrs().srsid()
        provider = layer.dataProvider()
        f = QgsFeature()

        if layer.crs().projectionAcronym() == "longlat":
            tolerance = 0.000
        else:
            tolerance = settings.value("/beePen/tolerance",
                                       0.000, type=float)

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
        try:
            assert fields.count() >= 3
        except:
            self.warn("Current layer has not the required fields for annotation layer")
            return
        
        record_values = [self.beePen_QWidget.pencil_width, 
                         self.beePen_QWidget.transparency, 
                         self.beePen_QWidget.color_name]
                         
        for ndx, value in enumerate(record_values):
            f.setAttribute(ndx, value)

        layer.beginEditCommand("Feature added")
        layer.addFeature(f)
        layer.endEditCommand()
        
        

    def deleteFeatures(self, geom):
        
        settings = QSettings()

        layer = self.canvas.currentLayer()
        if layer is None:
            del geom
            return
        
        fields = layer.pendingFields()   
        field_names = [field.name() for field in fields]
        
        if not "width" in field_names and \
           not "transp" in field_names and \
           not "color" in field_names:
            del geom
            self.warn("The current active layer is not an annotation layer")
            return
        
        renderer = self.canvas.mapRenderer()
        
        layer.setRendererV2(self.renderer)           
        
        layerCRSSrsid = layer.crs().srsid()
        projectCRSSrsid = renderer.destinationCrs().srsid()
        provider = layer.dataProvider()
        f = QgsFeature()

        if layer.crs().projectionAcronym() == "longlat":
            tolerance = 0.000
        else:
            tolerance = settings.value("/beePen/tolerance",
                                       0.000, type=float)

        # on the Fly reprojection.
        if layerCRSSrsid != projectCRSSrsid:
            geom.transform(QgsCoordinateTransform(projectCRSSrsid,
                                                  layerCRSSrsid))
        simpl_geom = geom.simplify(tolerance)
        
        provider = layer.dataProvider()

        for feat in layer.getFeatures():
            
            target_geom = feat.geometry()
            if target_geom.intersects(simpl_geom):
                layer.beginEditCommand("Feature deleted")
                layer.deleteFeature( feat.id() )
                layer.endEditCommand()                
            else: 
                pass

        
                    
    def deactivate_pencil(self, mapTool = None):        
                
        if mapTool is self.pencil_tool:
            return
        
        self.beePen_pencil_QAction.setChecked(False)
        if self.pencil_active:
            self.pencil_tool.rbFinished['QgsGeometry*'].disconnect(self.createFeature)
        self.pencil_active = False
 
 
    def erase_features(self):
        
        # self.deactivate_pencil()
        
        if not self.is_beePen_widget_open:
            self.warn("First launch beePen button")
            return
                
        self.eraser_tool = EraserTool(self.canvas)
        
        self.canvas.setMapTool(self.eraser_tool)
        self.beePen_rubber_QAction.setChecked(True)
        self.eraser_tool.rbFinished['QgsGeometry*'].connect(self.deleteFeatures)
        self.eraser_active = True
        #

    def info(self, msg):
        
        QMessageBox.information( self.interface.mainWindow(),  self.plugin_name, msg )
        
        
    def warn( self, msg):
    
        QMessageBox.warning( self.interface.mainWindow(),  self.plugin_name, msg )
        
                               
    def unload(self):

        self.interface.digitizeToolBar().removeAction(self.beePen_QAction)
        self.interface.digitizeToolBar().removeAction(self.beePen_pencil_QAction)
        self.interface.digitizeToolBar().removeAction(self.beePen_rubber_QAction)
               
        self.interface.removePluginMenu( "beePen", self.beePen_QAction )

        
        
               

