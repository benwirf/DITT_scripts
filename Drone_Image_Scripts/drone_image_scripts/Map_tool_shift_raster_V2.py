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
        
        self.rb1 = None
        self.rb2 = None
        self.rb3 = None
    
    def canvasMoveEvent(self, e):
        if not self.first_click:
            if self.rb2:
                self.rb2.reset()
            geom = self.transform_geom(QgsGeometry().fromPolylineXY([self.pnt_A, self.toLayerCoordinates(self.shift_layer, e.mapPoint())]))
            self.rb2 = QgsRubberBand(self.canvas, QgsWkbTypes.LineGeometry)
            self.rb2.setToGeometry(geom)
            self.rb2.setColor(QColor('Blue'))
            self.rb2.show()
    
    def canvasReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            if self.first_click:
                if self.rb1:
                    self.rb1.reset()
                if self.rb2:
                    self.rb2.reset()
                if self.rb3:
                    self.rb3.reset()
                self.pnt_A = self.toLayerCoordinates(self.shift_layer, e.mapPoint())
                geom = self.transform_geom(QgsGeometry().fromPointXY(self.pnt_A))
                self.rb1 = QgsRubberBand(self.canvas, QgsWkbTypes.PointGeometry)
                self.rb1.setToGeometry(geom)
                self.rb1.setIcon(QgsRubberBand.ICON_BOX)
                self.rb1.setColor(QColor('Red'))
                self.rb1.show()
                self.first_click = False
            elif not self.first_click:
                if self.rb2:
                    self.rb2.reset()
                self.pnt_B = self.toLayerCoordinates(self.shift_layer, e.mapPoint())
                if self.pnt_A and self.pnt_B:
                    geom = self.transform_geom(QgsGeometry().fromPointXY(self.pnt_B))
                    self.rb3 = QgsRubberBand(self.canvas, QgsWkbTypes.PointGeometry)
                    self.rb3.setToGeometry(geom)
                    self.rb3.setIcon(QgsRubberBand.ICON_BOX)
                    self.rb3.setColor(QColor('Red'))
                    self.rb3.show()
                    self.X_offset = self.pnt_B.x() - self.pnt_A.x()
                    self.Y_offset = self.pnt_B.y() - self.pnt_A.y()
                self.first_click = True
        elif e.button() == Qt.RightButton:
            if self.rb1:
                self.rb1.reset()
            if self.rb2:
                self.rb2.reset()
            if self.rb3:
                self.rb3.reset()
            self.shift_raster(self.shift_layer, self.X_offset, self.Y_offset)
            
#########################################################################

    def shift_raster(self, lyr, x_offset, y_offset):
        if x_offset is not None and y_offset is not None:
            in_path = lyr.source()
            print(in_path)
            out_string = QFileDialog.getSaveFileName(None, 'Save output raster', filter='.tif')
            file_name = out_string[0].split('/')[-1]
            out_path = ''.join(out_string)

            raster = gdal.Open(in_path)
            if not raster:
                print('Input raster is none')
                return

            # Get input raster bands
            input_bands = [raster.GetRasterBand(i+1) for i in range(raster.RasterCount)]

            # Get input raster data type
            data_type = input_bands[0].DataType

            # Create list of bands read into arrays
            band_arrays = [band.ReadAsArray() for band in input_bands]

            geotransform = raster.GetGeoTransform()
            originX = geotransform[0]
            originY = geotransform[3]
            pixelWidth = geotransform[1]
            pixelHeight = geotransform[5]
            cols = raster.RasterXSize
            rows = raster.RasterYSize

            driver = gdal.GetDriverByName('GTiff')
            outRaster = driver.Create(out_path, cols, rows, len(input_bands), data_type)
            if not outRaster:
                print('Output raster is none')
                return
            outRaster.SetGeoTransform((originX+x_offset, pixelWidth, 0, originY+y_offset, 0, pixelHeight))

            # Write array from each input band to each output band
            for index, array in enumerate(band_arrays):
                outband = outRaster.GetRasterBand(index+1)
                if outband:
                    outband.WriteArray(array)
                    outband.FlushCache()
                
            outRasterSRS = osr.SpatialReference()
            outRasterSRS.ImportFromWkt(raster.GetProjectionRef())
            outRaster.SetProjection(outRasterSRS.ExportToWkt())

            outRaster = None
            
            iface.addRasterLayer(out_path, file_name, 'gdal')

#########################################################################
            
    def transform_geom(self, geom):
        proj_crs = QgsProject.instance().crs()
        lyr_crs = self.shift_layer.crs()
        if proj_crs != lyr_crs:
            xform = QgsCoordinateTransform(lyr_crs, proj_crs, QgsProject.instance())
            geom.transform(xform)
            return geom
        return geom
            
    def deactivate(self):
        if self.rb1:
            self.rb1.reset()
            self.rb1 = None
        if self.rb2:
            self.rb2.reset()
            self.rb2 = None
        if self.rb3:
            self.rb3.reset()
            self.rb3 = None
        

layer = iface.activeLayer()
if layer.type() == QgsMapLayerType.RasterLayer:
    T = MapToolShiftRaster(iface.mapCanvas(), layer)
    iface.mapCanvas().setMapTool(T)
else:
    iface.messageBar().pushMessage('Please select a raster layer!')