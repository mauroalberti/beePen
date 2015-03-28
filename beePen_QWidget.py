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


_plugin_name_ = "beePen"

        
class beePen_QWidget( QWidget ):


    def __init__( self, canvas ):

        super( beePen_QWidget, self ).__init__() 
        self.mapcanvas = canvas   
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
        pen_width_QComboBox = QComboBox()  
        pen_width_QComboBox.insertItems(0, ["1","2","3","4","5"])      
        pen_layout.addWidget( pen_width_QComboBox)

        # transparency
        pen_layout.addWidget( QLabel("Transp."))        
        transparency_QComboBox = QComboBox() 
        transparency_QComboBox.insertItems(0, ["0%","25%","50%","75%","100%"])        
        pen_layout.addWidget( transparency_QComboBox)
        
        # pen color
        pen_layout.addWidget( QLabel("Color"))        
        pen_color_QComboBox = QComboBox() 
        pen_color_QComboBox.insertItems(0, ["red","blue","yellow","green","orange","violet","pink"])         
        pen_layout.addWidget( pen_color_QComboBox)
        
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
        self.setWindowTitle(_plugin_name_)        
                


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
         
        try:   
            _, _ = shapefile_create( file_path, geom_type, fields_dict_list, project_crs, layer_name = "layer" )
        except:
            self.warn("Error in shapefile creation")
            return
        
        annotation_layer = QgsVectorLayer(file_path, shape_name, "ogr")        
        QgsMapLayerRegistry.instance().addMapLayer(annotation_layer)       
    
        self.info("Layer created")
        
        
        
    def info(self, msg):
        
        QMessageBox.information( self,  _plugin_name_, msg )
        
        
    def warn( self, msg):
    
        QMessageBox.warning( self,  _plugin_name_, msg )
        
        


