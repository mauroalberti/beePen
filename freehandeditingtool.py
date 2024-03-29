
# adapted from Freehandediting plugin
# by Pavol Kapusta


from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *

from qgis.core import *
from qgis.gui import *

from .qt_utils.qt_utils import warn


class FreehandEditingTool(QgsMapToolEmitPoint):

    rbFinished = pyqtSignal(QgsGeometry)
    rubberband_conv_factor = 3800  # empirical factor for adapting rubberband width to actual scale

    def __init__(self, interface, canvas, color_name, width):

        QgsMapToolEmitPoint.__init__(self, canvas)

        self.interface = interface
        self.canvas = canvas
        self.rubberband = None
        self.mCtrl = None
        self.drawing = False
        self.ignoreclick = False
        
        self.color_name = color_name
        self.pencil_width = width

        # our own fancy cursor
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


    def update_pen_style(self, name, parameter):
        
        if name == "color_transp":
            self.color_name = parameter
        elif name == "width":
            self.pencil_width = float(parameter)
        else:
            warn(self.interface.mainWindow(), self.plugin_name, "Error with pen style update")

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
        
        layers = self.interface.layerTreeView().selectedLayers()
        if len(layers) != 1:
            return
        else:
            layer = layers[0]

        self.drawing = True
        
        self.rubberband = QgsRubberBand(self.canvas)

        red, green, blue, alpha = list(map(int, self.color_name.split(",")))
        self.rubberband.setColor(QColor(red, green, blue, alpha))
        self.rubberband.setWidth(self.pencil_width * FreehandEditingTool.rubberband_conv_factor / self.canvas.scale()) # denominator is empirically-derived value

        point = self.toLayerCoordinates(layer, event.pos())
        pointMap = self.toMapCoordinates(layer, point)
        self.rubberband.addPoint(pointMap)

    def canvasMoveEvent(self, event):

        if self.ignoreclick or not self.rubberband:
            return
        
        self.rubberband.addPoint(self.toMapCoordinates(event.pos()))

    def canvasReleaseEvent(self, event):

        if self.ignoreclick:
            return
        
        self.drawing = False

        if not self.rubberband:
            return
        
        if self.rubberband.numberOfVertices() > 2:
            geom = self.rubberband.asGeometry()
        else:
            geom = None

        # reset rubberband and refresh the canvas
        self.rubberband.reset()
        self.rubberband = None
        self.canvas.refresh()

        try:
            self.rbFinished.emit(geom)
        except:
            pass


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

    
class EraserTool(QgsMapToolEmitPoint):

    rbFinished = pyqtSignal(QgsGeometry)

    def __init__(self, interface, canvas):

        QgsMapToolEmitPoint.__init__(self, canvas)

        self.interface = interface
        self.canvas = canvas
        self.rb = None
        self.mCtrl = None
        self.drawing = True
        self.ignoreclick = False

        #our own fancy cursor
        self.cursor = QCursor(QPixmap(["16 16 3 1",
                                       "      c None",
                                       ".     c #FF0000",
                                       "+     c #EEA9B8",
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
        
        layers = self.interface.layerTreeView().selectedLayers()
        if len(layers) != 1:
            return
        else:
            layer = layers[0]

        self.drawing = True
        
        self.rb = QgsRubberBand(self.canvas)        

        self.rb.setColor(QColor("red"))

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
        else:
            geom = None

        # reset rubberband and refresh the canvas

        self.rb.reset()
        self.rb = None
        self.canvas.refresh()

        try:
            self.rbFinished.emit(geom)
        except:
            pass

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

