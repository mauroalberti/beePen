# -*- coding: utf-8 -*-


import os


from osgeo import ogr, osr, gdal
from osgeo import gdalconst 


from PyQt4.QtCore import *
from PyQt4.QtGui import *


from geosurf.qgs_tools import loaded_line_layers
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
        
        # use existing layer
        layer_layout.addWidget( QLabel("Use"))        
        use_layer_QComboBox = QComboBox()  
        layer_layout.addWidget( use_layer_QComboBox)          

        self.current_line_layers = loaded_line_layers()  
        self.update_layer_comboBox( use_layer_QComboBox, self.current_line_layers )        
                
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
        

        # Draw widgets

        draw_QGroupBox = QGroupBox(self)
        draw_QGroupBox.setTitle( 'Draw')        
        draw_layout = QHBoxLayout()
        
        # start drawing
        start_drawing_QPushButton = QPushButton("Start")        
        draw_layout.addWidget( start_drawing_QPushButton)

        # end drawing
        end_drawing_QPushButton = QPushButton("End")        
        draw_layout.addWidget( end_drawing_QPushButton)
        
        draw_QGroupBox.setLayout( draw_layout )
        self.dialog_layout.addWidget( draw_QGroupBox )  
        
                
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
                


    def update_layer_comboBox( self, combobox, layer_list ):
    
        combobox.clear()
        if len( layer_list ) == 0:
            return
        combobox.addItems( [ layer.name() for layer in layer_list ] ) 
        
 
    def create_annotation_layer(self):
            
        file_path = new_file_path( self, 
                                   "Define shapefile", 
                                   lastUsedDir(),
                                   "annotation.shp",
                                   "shapefile (shp, SHP)" )
        if file_path == "":
            return

        setLastUsedDir( file_path ) 
                
        geom_type = ogr.wkbLineString
            
        fields_dict_list = [{"name": "width", "ogr_type": ogr.OFTInteger},
                            {"name": "transp", "ogr_type": ogr.OFTInteger},
                            {"name": "color", "ogr_type": ogr.OFTString, "width": 20}]            
            
        outShapefile, outShapelayer = shapefile_create( file_path, geom_type, fields_dict_list, crs = None, layer_name = "layer" )
        
        self.info("Created")
        
        

    def info(self, msg):
        
        QMessageBox.information( self,  _plugin_name_, msg )
        
        
    def warn( self, msg):
    
        QMessageBox.warning( self,  _plugin_name_, msg )
        
        


