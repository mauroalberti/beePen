# -*- coding: utf-8 -*-


import os


from PyQt4.QtCore import *
from PyQt4.QtGui import *



_plugin_name_ = "beePen"

        
class beePen_QWidget( QWidget ):

    def __init__( self, canvas ):

        super( beePen_QWidget, self ).__init__() 
        self.mapcanvas = canvas   
        self.setup_gui()


    def info(self, msg):
        
        QMessageBox.information( self,  _plugin_name_, msg )
        
        
    def warn( self, msg):
    
        QMessageBox.warning( self,  _plugin_name_, msg )
          
                      
    def setup_gui( self ): 

        self.dialog_layout = QVBoxLayout()
        self.main_widget = QTabWidget()        
        self.main_widget.addTab( self.setup_annotation1_tab(), "Annotation 1" )         
        self.main_widget.addTab( self.setup_annotation2_tab(), "Annotation 2" )
        self.main_widget.addTab( self.setup_about_tab(), "Help/About" )
        
        self.dialog_layout.addWidget(self.main_widget)                             
        self.setLayout(self.dialog_layout)            
        self.adjustSize()               
        self.setWindowTitle(_plugin_name_)        
                
  
    def setup_annotation1_tab( self ):  

        annotation1_widget = QWidget() 
        annotation1_layout = QVBoxLayout()
 
        annotation1_toolbox = QToolBox()   
                 
        # .... some code 
                       
        annotation1_layout.addWidget(annotation1_toolbox)
        annotation1_widget.setLayout(annotation1_layout) 
        
        return annotation1_widget     
        

    def setup_annotation2_tab( self ):
        
        annotation2_project_QWidget = QWidget()  
        annotation2_project_layout = QVBoxLayout() 

        project_toolbox = QToolBox()

        # .... some code 
                
        annotation2_project_layout.addWidget( project_toolbox ) 
           
        annotation2_project_QWidget.setLayout( annotation2_project_layout )
        
        return annotation2_project_QWidget


           
    def setup_about_tab(self):
        
        about_widget = QWidget()  
        about_layout = QVBoxLayout( )
        
        htmlText = """
        <h3>beePen</h3>
        Still to create
        <br />
        <br />
        <br />
        """
        
        aboutQTextBrowser = QTextBrowser( about_widget )        
        aboutQTextBrowser.insertHtml( htmlText )
         
        about_layout.addWidget( aboutQTextBrowser )  
        about_widget.setLayout(about_layout) 
        
        return about_widget



