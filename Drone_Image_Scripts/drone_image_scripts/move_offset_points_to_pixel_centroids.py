from osgeo import gdal, osr

raster_layer = QgsProject.instance().mapLayersByName('Middle-Point-19-05-2023-2-orthophoto')[0]
point_layer = QgsProject.instance().mapLayersByName('alignment_offset_points')[0]

selected_pts = point_layer.selectedFeatures()

if not selected_pts:
    print('No features selected')
else:
    pt_feat1 = selected_pts[0]
    print(pt_feat1)

    geom1 = pt_feat1.geometry()
    ref_point_1 = geom1.asPoint()
    ref_point1_x = ref_point_1.x()
    ref_point1_y = ref_point_1.y()
    print(ref_point1_x, ref_point1_y)
    
    raster_path = raster_layer.source()
    print(raster_path)

    raster = gdal.Open(raster_path)

    geotransform = raster.GetGeoTransform()
    originX = geotransform[0]
    originY = geotransform[3]
    pixelWidth = geotransform[1]
    pixelHeight = geotransform[5]
    cols = raster.RasterXSize
    rows = raster.RasterYSize

    #print(geotransform)
        
    target_pixel_col = int((ref_point1_x - originX) / pixelWidth)
    target_pixel_row = int((ref_point1_y - originY) / pixelHeight)
    
    print(target_pixel_col)
    print(target_pixel_row)
    
    pixel_top_leftX = originX + (target_pixel_col * pixelWidth)
    pixel_top_leftY = originY + (target_pixel_row * pixelHeight)
    
    pixel_centroidX = pixel_top_leftX + (pixelWidth/2)
    pixel_centroidY = pixel_top_leftY + (pixelHeight/2)
    
    centroid_feat = QgsFeature()
    centroid_feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(pixel_centroidX, pixel_centroidY)))
    centroid_feat.setAttributes([5])
    
    point_layer.dataProvider().addFeatures([centroid_feat])
    point_layer.updateExtents()
    point_layer.triggerRepaint()

    