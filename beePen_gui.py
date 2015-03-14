
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *

import resources


from beePen_QWidget import beePen_QWidget



class beePen_gui( object ):

    def __init__(self, interface):

        self.interface = interface
        self.main_window = self.interface.mainWindow()
        self.canvas = self.interface.mapCanvas()        


    def initGui(self):
        
        self.beePen_QAction = QAction(QIcon(":/plugins/beePen/bee.png"), "beePen", self.interface.mainWindow())
        self.beePen_QAction.setWhatsThis( "Graphic annotations for field work" ) 
        self.beePen_QAction.triggered.connect( self.open_beePen )
        self.interface.addPluginToMenu("beePen", self.beePen_QAction)


    def unload(self):

        self.interface.removePluginMenu( "beePen", self.beePen_QAction )


    def open_beePen(self):

        beePen_DockWidget = QDockWidget( 'beePen', self.interface.mainWindow() )        
        beePen_DockWidget.setAttribute(Qt.WA_DeleteOnClose)
        beePen_DockWidget.setAllowedAreas( Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea )        
        self.beePen_QWidget = beePen_QWidget( self.canvas )        
        beePen_DockWidget.setWidget( self.beePen_QWidget ) 
        beePen_DockWidget.destroyed.connect( self.beePen_QWidget.closeEvent )       
        self.interface.addDockWidget( Qt.RightDockWidgetArea, beePen_DockWidget )



        
        

