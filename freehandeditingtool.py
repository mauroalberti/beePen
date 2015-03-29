# -*- coding: utf-8 -*-


# adapted from Freehabdediting plugin 
# by Pavol Kapusta



from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *



class FreehandEditingTool(QgsMapTool):

    rbFinished = pyqtSignal('QgsGeometry*')


    def __init__(self, canvas, color_name, pencil_width):
        
        QgsMapTool.__init__(self, canvas)
        
        self.canvas = canvas
        self.rb = None
        self.mCtrl = None
        self.drawing = False
        self.ignoreclick = False
        
        self.color_name = color_name
        self.pencil_width = pencil_width
        
        #our own fancy cursor
        self.cursor = QCursor(QPixmap(["16 16 3 1",
                                       "      c None",
                                       ".     c #FF0000",
                                       "+     c #faed55",
                                       "                ",
                                       "       +.+      ",
                                       "      ++.++     ",
                                       "     +.....+    ",
                                       "    +.  .  .+   ",
                                       "   +.   .   .+  ",
                                       "  +.    .    .+ ",
                                       " ++.    .    .++",
                                       " ... ...+... ...",
                                       " ++.    .    .++",
                                       "  +.    .    .+ ",
                                       "   +.   .   .+  ",
                                       "   ++.  .  .+   ",
                                       "    ++.....+    ",
                                       "      ++.++     ",
                                       "       +.+      "]))



    def keyPressEvent(self, event):
        
        if event.key() == Qt.Key_Control:
            self.mCtrl = True


    def keyReleaseEvent(self, event):
        
        if event.key() == Qt.Key_Control:
            self.mCtrl = False


    def canvasPressEvent(self, event):
        
        if self.ignoreclick or self.drawing:
            # ignore secondary canvasPressEvents if already drag-drawing
            # NOTE: canvasReleaseEvent will still occur (ensures rb is deleted)
            # click on multi-button input device will halt drag-drawing
            return
        
        layer = self.canvas.currentLayer()
        if not layer:
            return
        
        self.drawing = True
        
        self.rb = QgsRubberBand(self.canvas)
        self.rb.setColor(QColor(self.color_name))
        self.rb.setWidth(self.pencil_width)
            
        x = event.pos().x()
        y = event.pos().y()        

        point = self.toLayerCoordinates(layer, event.pos())
        pointMap = self.toMapCoordinates(layer, point)
        self.rb.addPoint(pointMap)


    def canvasMoveEvent(self, event):
        
        if self.ignoreclick or not self.rb:
            return
        
        self.rb.addPoint(self.toMapCoordinates(event.pos()))


    def canvasReleaseEvent(self, event):
        
        if self.ignoreclick:
            return
        
        self.drawing = False
        
        if not self.rb:
            return
        
        if self.rb.numberOfVertices() > 2:
            geom = self.rb.asGeometry()
            self.rbFinished.emit(geom)

        # reset rubberband and refresh the canvas
        self.rb.reset()
        self.rb = None
        self.canvas.refresh()


    def setIgnoreClick(self, ignore):
        """Used to keep the tool from registering clicks during modal dialogs"""
        
        self.ignoreclick = ignore


    def showSettingsWarning(self):
        
        pass


    def activate(self):
        
        mc = self.canvas
        mc.setCursor(self.cursor)        


    def deactivate_pencil(self):
        
        pass
    

    def isZoomTool(self):
        
        return False


    def isTransient(self):
        
        return False
    

    def isEditTool(self):
        
        return True
    
    
