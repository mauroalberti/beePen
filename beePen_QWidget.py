# -*- coding: utf-8 -*-


import os


from osgeo import ogr, osr, gdal
from osgeo import gdalconst 


from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import QgsVectorLayer, QgsMapLayerRegistry


from geosurf.qgs_tools import loaded_line_layers, get_on_the_fly_projection
from geosurf.geo_io import shapefile_create
from geosurf.qt_utils import new_file_path, lastUsedDir, setLastUsedDir


        
class beePen_QWidget( QWidget ):
    
    style_signal = pyqtSignal(str, str)


    def __init__( self, canvas, plugin_name, pen_widths, pen_transparencies, pen_colors ):

        super( beePen_QWidget, self ).__init__() 
        self.mapcanvas = canvas
        
        self.plugin_name = plugin_name

         
        self.pen_widths = pen_widths
        self.pen_transparencies = pen_transparencies
        self.pen_colors = pen_colors
              
        self.color_name = self.pen_colors[0]
        self.pencil_width = self.pen_widths[0]  
        self.transparency = self.pen_transparencies[0]
           
        self.setup_gui()
          
                      
    def setup_gui( self ): 

        self.dialog_layout = QHBoxLayout()        
    
        # Annotation layer widgets
        
        layer_QGroupBox = QGroupBox(self)
        layer_QGroupBox.setTitle( 'Annotation layer')        
        layer_layout = QHBoxLayout()
        
        # create new annotation layer button
        create_new_QPushButton = QPushButton("Create new")  
        create_new_QPushButton.clicked.connect(self.create_annotation_layer)              
        layer_layout.addWidget( create_new_QPushButton)

                
        layer_QGroupBox.setLayout( layer_layout )
        self.dialog_layout.addWidget( layer_QGroupBox )        

        
        # Pen widgets
        
        pen_QGroupBox = QGroupBox(self)
        pen_QGroupBox.setTitle( 'Pen')        
        pen_layout = QHBoxLayout()
        
        # pen width
        pen_layout.addWidget( QLabel("Width"))        
        self.pen_width_QComboBox = QComboBox()  
        self.pen_width_QComboBox.insertItems(0, [str(width) for width in self.pen_widths])    
        self.pen_width_QComboBox.currentIndexChanged['QString'].connect(self.get_current_pencil_width_choice)         
        pen_layout.addWidget( self.pen_width_QComboBox)

        # transparency
        pen_layout.addWidget( QLabel("Transp."))        
        self.transparency_QComboBox = QComboBox() 
        self.pen_transparencies_percent = [str(val)+"%" for val in self.pen_transparencies]
        self.transparency_QComboBox.insertItems(0, self.pen_transparencies_percent) 
        self.transparency_QComboBox.currentIndexChanged['QString'].connect(self.get_current_transparency_value_choice)       
        pen_layout.addWidget( self.transparency_QComboBox)
        
        # pen color
        pen_layout.addWidget( QLabel("Color"))        
        self.pen_color_QComboBox = QComboBox() 
        self.pen_color_QComboBox.insertItems(0, self.pen_colors)         
        #self.pen_color_QComboBox.setCurrentText("blue")
        self.pen_color_QComboBox.currentIndexChanged['QString'].connect(self.get_current_color_name_choice)
        pen_layout.addWidget( self.pen_color_QComboBox)
        
        pen_QGroupBox.setLayout( pen_layout )
        self.dialog_layout.addWidget( pen_QGroupBox )           
        
                
        # Undo widgets

        undo_QGroupBox = QGroupBox(self)
        undo_QGroupBox.setTitle( 'Delete')        
        undo_layout = QHBoxLayout()
        
        # clear last button
        clear_last_QPushButton = QPushButton("Last")        
        undo_layout.addWidget( clear_last_QPushButton)
                
        # clear all button
        clear_all_QPushButton = QPushButton("All")        
        undo_layout.addWidget( clear_all_QPushButton)
        
        # delete tool
        delete_tool_QPushButton = QPushButton("Select")        
        undo_layout.addWidget( delete_tool_QPushButton)
                            
        undo_QGroupBox.setLayout( undo_layout )
        self.dialog_layout.addWidget( undo_QGroupBox )  
        
        
        # final settings
                                                           
        self.setLayout(self.dialog_layout)            
        self.adjustSize()               
        self.setWindowTitle(self.plugin_name)        
                

    def create_annotation_layer(self):

        _, project_crs = get_on_the_fly_projection(self.mapcanvas)
            
        file_path = new_file_path( self, 
                                   "Define shapefile", 
                                   lastUsedDir(),
                                   "annotation.shp",
                                   "shapefiles (*.shp *.SHP)" )
        if file_path == "":
            return

        setLastUsedDir( file_path ) 
             
        shape_name = file_path.split("/")[-1].split(".")[0] 
        geom_type = ogr.wkbLineString
            
        fields_dict_list = [{"name": "width", "ogr_type": ogr.OFTInteger},
                            {"name": "transp", "ogr_type": ogr.OFTInteger},
                            {"name": "color", "ogr_type": ogr.OFTString, "width": 20}]            
         

        _, _ = shapefile_create( file_path, geom_type, fields_dict_list, layer_name = "layer" )


        
        annotation_layer = QgsVectorLayer(file_path, shape_name, "ogr")        
        QgsMapLayerRegistry.instance().addMapLayer(annotation_layer)       
    
        self.info("Layer created")
        
        
    def get_current_color_name_choice(self):
        
        self.color_name = self.pen_color_QComboBox.currentText()
        # self.info("Color is %s" % (self.color_name))
        self.style_signal.emit("color", self.color_name)


    def get_current_pencil_width_choice(self):
        
        self.pencil_width = int(self.pen_width_QComboBox.currentText())
        # self.info("Width is %d" % (self.pencil_width))    
        self.style_signal.emit("width", str(self.pencil_width))
        

    def get_current_transparency_value_choice(self):
        
        self.transparency = int(self.transparency_QComboBox.currentText()[:-1])
        # self.info("Transparency is %d" % (self.transparency))        
        self.style_signal.emit("transparency", str(self.transparency))
                
        
    def info(self, msg):
        
        QMessageBox.information( self,  self.plugin_name, msg )
        
        
    def warn( self, msg):
    
        QMessageBox.warning( self,  self.plugin_name, msg )
        
        


