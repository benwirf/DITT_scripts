import os
from osgeo import gdal, osr

class MapToolShiftRaster(QgsMapToolEmitPoint):
    
    def __init__(self, canvas, shift_layer):
        self.canvas = canvas
        self.shift_layer = shift_layer
        QgsMapToolEmitPoint.__init__(self, self.canvas)
        self.first_click = True
        self.pnt_A = None
        self.pnt_B = None
        self.X_offset = None
        self.Y_offset = None
        
    def canvasReleaseEvent(self, e):
        if self.first_click:
            self.pnt_A = self.toLayerCoordinates(self.shift_layer, e.mapPoint())
            self.first_click = False
        elif not self.first_click:
            self.pnt_B = self.toLayerCoordinates(self.shift_layer, e.mapPoint())
            if self.pnt_A and self.pnt_B:
                self.X_offset = self.pnt_B.x() - self.pnt_A.x()
                self.Y_offset = self.pnt_B.y() - self.pnt_A.y()

                print(f'PointA: {self.pnt_A}')
                print(f'PointB: {self.pnt_B}')
                print(f'Xoffset: {self.X_offset}')
                print(f'Yoffset: {self.Y_offset}')
            self.first_click = True

layer = iface.activeLayer()
T = MapToolShiftRaster(iface.mapCanvas(), layer)
iface.mapCanvas().setMapTool(T)