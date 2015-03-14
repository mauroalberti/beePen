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

        profile_widget = QWidget() 
        profile_layout = QVBoxLayout()
 
        profile_toolbox = QToolBox()        


                 
        # widget final setup 
                       
        profile_layout.addWidget(profile_toolbox)
        profile_widget.setLayout(profile_layout) 
        
        return profile_widget     
        

    def setup_annotation2_tab( self ):
        
        section_project_QWidget = QWidget()  
        section_project_layout = QVBoxLayout() 

        project_toolbox = QToolBox()
        
        ### Point project toolbox
                
        # widget final setup
                
        section_project_layout.addWidget( project_toolbox ) 
           
        section_project_QWidget.setLayout( section_project_layout )
        
        return section_project_QWidget


           
    def setup_about_tab(self):
        
        about_widget = QWidget()  
        about_layout = QVBoxLayout( )
        
        htmlText = """
        <h3>beePen</h3>
        To create
        <br />
        <br />
        <br />
        
        
        
        
        """
        
        aboutQTextBrowser = QTextBrowser( about_widget )        
        aboutQTextBrowser.insertHtml( htmlText )
         
        about_layout.addWidget( aboutQTextBrowser )  
        about_widget.setLayout(about_layout) 
        
        return about_widget




