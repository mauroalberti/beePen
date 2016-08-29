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
        self.canvas = canvas
        
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
        pen_layout.addWidget( QLabel("Width (map units)"))        
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


        # Help widgets
        
        help_QGroupBox = QGroupBox(self)
        help_QGroupBox.setTitle( 'Help')        
        help_layout = QHBoxLayout()
        
        # help button
        help_QPushButton = QPushButton("Help")  
        help_QPushButton.clicked.connect(self.open_help_page)              
        help_layout.addWidget( help_QPushButton)
                
        help_QGroupBox.setLayout( help_layout )
        self.dialog_layout.addWidget( help_QGroupBox )    
               
        
        # final settings
                                                           
        self.setLayout(self.dialog_layout)            
        self.adjustSize()               
        self.setWindowTitle(self.plugin_name)        
  
  
    def open_help_page(self):
        
        import webbrowser
        local_url = os.path.dirname(os.path.realpath(__file__)) + os.sep + "help" + os.sep + "help.html"
        local_url = local_url.replace("\\","/")
        if not webbrowser.open(local_url):
            self.warn("Error with browser.\nOpen manually help/help.html")


    def get_prjcrs_as_proj4str(self):
        # get project CRS information
        hasOTFP, project_crs = get_on_the_fly_projection(self.canvas)
        if hasOTFP:
            proj4_str = str(project_crs.toProj4())
            project_crs_osr = osr.SpatialReference()
            project_crs_osr.ImportFromProj4(proj4_str)
            return project_crs_osr
        else:
            return None

    def create_annotation_layer(self):

        _, project_crs = get_on_the_fly_projection(self.canvas)
            
        file_path = new_file_path(self,
                                  "Define shapefile",
                                  os.path.join(lastUsedDir(), "annotation.shp"),
                                  "shapefiles (*.shp *.SHP)" )
        if file_path == "":
            return

        if os.path.exists(file_path):
            self.warn("Shapefile already exists.\nChoose a new name")
            return

        setLastUsedDir( file_path ) 
             
        shape_name = file_path.split("/")[-1].split(".")[0] 
        geom_type = ogr.wkbLineString
            
        fields_dict_list = [{"name": "width", "ogr_type": ogr.OFTReal},
                            {"name": "transp", "ogr_type": ogr.OFTInteger},
                            {"name": "color", "ogr_type": ogr.OFTString, "width": 20}]

        # get project CRS information
        project_crs_osr = self.get_prjcrs_as_proj4str()

        shapefile_create(file_path, geom_type, fields_dict_list, project_crs_osr)
        
        annotation_layer = QgsVectorLayer(file_path, shape_name, "ogr")        
        QgsMapLayerRegistry.instance().addMapLayer(annotation_layer)       
    
        self.info("Layer created")
        
        
    def get_current_color_name_choice(self):
        
        self.color_name = self.pen_color_QComboBox.currentText()
        # self.info("Color is %s" % (self.color_name))
        self.style_signal.emit("color", self.color_name)


    def get_current_pencil_width_choice(self):
        
        self.pencil_width = float(self.pen_width_QComboBox.currentText())
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
        
        


