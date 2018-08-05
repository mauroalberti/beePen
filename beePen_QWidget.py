from __future__ import absolute_import


from builtins import map
from builtins import str
import os
from osgeo import ogr

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *

from qgis.core import *
from qgis.gui import QgsColorButton

from .qt_utils.qt_utils import new_file_path, lastUsedDir, setLastUsedDir, warn, info

from .geosurf.geo_io import shapefile_create
from .geosurf.qgs_tools import get_on_the_fly_projection


fields_dicts = [{"name": "width", "ogr_type": ogr.OFTReal},
                {"name": "color", "ogr_type": ogr.OFTString, "width": 20},
                {"name": "note", "ogr_type": ogr.OFTString, "width": 100}]


def isAnnotationLayer(layer):

    # check if vector
    if layer.type() != QgsMapLayer.VectorLayer:
        return False

    # check if is a line layer
    if layer.geometryType() != QgsWkbTypes.LineGeometry:
        return False

    # check that contains required fields
    layer_field_names = [fld.name() for fld in layer.fields()]
    expected_field_names = [rec["name"] for rec in fields_dicts]
    return all([exp_field_name in layer_field_names for exp_field_name in expected_field_names])


class beePen_QWidget(QWidget):
    
    style_signal = pyqtSignal(str, str)

    def __init__(self, interface, plugin_name, pen_widths, default_pen_width, pen_transparencies):

        super(beePen_QWidget, self).__init__() 

        self.interface = interface
        self.main_window = interface.mainWindow()
        self.canvas = interface.mapCanvas() 
        
        self.plugin_name = plugin_name
        self.plugin_dir = os.path.dirname(__file__)
         
        self.pen_widths = pen_widths
        self.pen_transparencies = pen_transparencies

        self.pencil_width = default_pen_width
        self.transparency = self.pen_transparencies[0]
        self.color_name = '255,0,0,255'

        self.setup_gui()

    def setup_gui(self): 

        self.dialog_layout = QHBoxLayout()        
    
        # Annotation layer widgets
        
        layer_QGroupBox = QGroupBox(self)
        layer_QGroupBox.setTitle('Annotation layer')        
        layer_layout = QHBoxLayout()
        
        # create new annotation layer button
        create_new_QPushButton = QPushButton("Create new")  
        create_new_QPushButton.clicked.connect(self.create_annotation_layer)              
        layer_layout.addWidget(create_new_QPushButton)

        # style existing
        style_current_QPushButton = QPushButton("Style selected layers")
        style_current_QPushButton.clicked.connect(self.style_annotation_layers)
        layer_layout.addWidget(style_current_QPushButton)

        layer_QGroupBox.setLayout(layer_layout)
        self.dialog_layout.addWidget(layer_QGroupBox)

        # Note widgets

        note_QGroupBox = QGroupBox(self)
        note_QGroupBox.setTitle('Note')
        note_layout = QHBoxLayout()

        self.note_QCheckBox = QCheckBox()
        self.note_QCheckBox.setChecked(True)
        note_layout.addWidget(self.note_QCheckBox)

        note_QGroupBox.setLayout(note_layout)
        self.dialog_layout.addWidget(note_QGroupBox)

# Pen widgets
        
        pen_QGroupBox = QGroupBox(self)
        pen_QGroupBox.setTitle('Pen')        
        pen_layout = QHBoxLayout()

        # pen width
        default_pen_width = 1
        pen_layout.addWidget(QLabel("Width (map units)"))        
        self.pen_width_QComboBox = QComboBox()  
        self.pen_width_QComboBox.insertItems(0, [str(width) for width in self.pen_widths])
        self.pen_width_QComboBox.setCurrentIndex(self.pen_width_QComboBox.findText(str(self.pencil_width)))
        self.pen_width_QComboBox.currentIndexChanged['QString'].connect(self.get_current_pencil_width_choice)         
        pen_layout.addWidget(self.pen_width_QComboBox)

        # transparency
        pen_layout.addWidget(QLabel("Transp."))        
        self.transparency_QComboBox = QComboBox() 
        self.pen_transparencies_percent = [str(val)+"%" for val in self.pen_transparencies]
        self.transparency_QComboBox.insertItems(0, self.pen_transparencies_percent) 
        self.transparency_QComboBox.currentIndexChanged['QString'].connect(self.update_color_transparency)
        pen_layout.addWidget(self.transparency_QComboBox)
        
        # pen color
        pen_layout.addWidget(QLabel("Color"))
        red, green, blue, alpha = list(map(int, self.color_name.split(",")))
        self.pencolor_QgsColorButtonV2 = QgsColorButton()
        self.pencolor_QgsColorButtonV2.setColor(QColor(red, green, blue, alpha))
        self.pencolor_QgsColorButtonV2.colorChanged['QColor'].connect(self.update_color_transparency)

        pen_layout.addWidget(self.pencolor_QgsColorButtonV2)

        pen_QGroupBox.setLayout(pen_layout)
        self.dialog_layout.addWidget(pen_QGroupBox)           

        # Help widgets
        
        help_QGroupBox = QGroupBox(self)
        help_QGroupBox.setTitle('Help')        
        help_layout = QHBoxLayout()
        
        # help button
        help_QPushButton = QPushButton("Help")  
        help_QPushButton.clicked.connect(self.open_help_page)              
        help_layout.addWidget(help_QPushButton)
                
        help_QGroupBox.setLayout(help_layout)
        self.dialog_layout.addWidget(help_QGroupBox)    

        # final settings
        self.setLayout(self.dialog_layout)            
        self.adjustSize()               
        self.setWindowTitle(self.plugin_name)        

    def open_help_page(self):

        dialog = HelpDialog()
        dialog.exec_()

    def get_prjcrs_as_proj4str(self):
        # get project CRS information

        hasOTFP, project_crs = get_on_the_fly_projection(self.canvas)
        if hasOTFP:
            return str(project_crs.toProj4())
        else:
            return ''

    def create_annotation_layer(self):

        _, project_crs = get_on_the_fly_projection(self.canvas)
            
        file_path = new_file_path(self,
                                  "Define shapefile",
                                  os.path.join(lastUsedDir(self.plugin_name), "annotation.shp"),
                                  "shapefiles (*.shp *.SHP)")
        if file_path == "":
            return

        if os.path.exists(file_path):
            warn(self.main_window,
                 self.plugin_name,
                 "Shapefile already exists.\nChoose a new name")
            return

        setLastUsedDir(self.plugin_name, file_path) 
             
        shape_name = file_path.split("/")[-1].split(".")[0] 
        geom_type = ogr.wkbLineString

        # get project CRS information
        project_crs_osr = self.get_prjcrs_as_proj4str()

        shapefile_create(file_path, geom_type, fields_dicts, project_crs_osr)
        
        annotation_layer = QgsVectorLayer(file_path, shape_name, "ogr")
        annotation_layer.loadNamedStyle(os.path.join(self.plugin_dir, "beePen_style.qml"))
        QgsProject.instance().addMapLayer(annotation_layer)
    
        info(self.main_window,
             self.plugin_name,
             "Layer created")

    def style_annotation_layers(self):

        selected_layers = self.interface.layerTreeView().selectedLayers()

        for layer in selected_layers:
            if isAnnotationLayer(layer):
                layer.loadNamedStyle(os.path.join(self.plugin_dir, "beePen_style.qml"))
            else:
                self.warn('Layer %s is not an annotation layer' % layer.name())

        self.canvas.refreshAllLayers()

    def update_color_transparency(self):

        color = self.pencolor_QgsColorButtonV2.color()
        red = color.red()
        green = color.green()
        blue = color.blue()
        transparency = 255 - int(self.transparency_QComboBox.currentText()[:-1])*2.55
        self.color_name = "%d,%d,%d,%d" % (red, green, blue, transparency)
        self.style_signal.emit("color_transp", self.color_name)

    def get_current_pencil_width_choice(self):
        
        self.pencil_width = float(self.pen_width_QComboBox.currentText())
        self.style_signal.emit("width", str(self.pencil_width))

    def info(self, msg):
        QMessageBox.information(self, self.plugin_name, msg)

    def warn(self, msg):
        QMessageBox.warning(self, self.plugin_name, msg)

    def error(self, msg):
        QMessageBox.error(self, self.plugin_name, msg)

        
class HelpDialog(QDialog):

    def __init__(self, parent=None):

        super(HelpDialog, self).__init__(parent)

        layout = QVBoxLayout()

        # About section

        helpTextBrwsr = QTextBrowser(self)

        helpTextBrwsr.setSource(QUrl('{}/help/help.html'.format(os.path.dirname(__file__))))
        helpTextBrwsr.setSearchPaths(['{}/help'.format(os.path.dirname(__file__))])

        layout.addWidget(helpTextBrwsr)

        self.setLayout(layout)

        self.setWindowTitle("beePen Help")



