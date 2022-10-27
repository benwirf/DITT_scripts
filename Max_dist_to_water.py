import os

paddock_layer_name = 'Mt_Sanford_Paddocks'
waterpoint_layer_name = 'Mt_Sanford_Waterpoints'

paddock_name_field = 'PDK_NAME'

paddock_layer = QgsProject.instance().mapLayersByName(paddock_layer_name)[0]

waterpoint_layer = QgsProject.instance().mapLayersByName(waterpoint_layer_name)[0]

out_dir = 'C:\\Users\\qw2\\Desktop\\Mt_Sanford\\Proximity_Rasters'

# Iterate over each paddock
for paddock in paddock_layer.getFeatures():
    # Simple spatial query to retrieve water points within each paddock
    waterpoint_feats = [f for f in waterpoint_layer.getFeatures() if f.geometry().intersects(paddock.geometry())]
#    print(waters)
    # Create a temporary layer to hold waterpoint features which fall within each paddock
    wkb = QgsWkbTypes.displayString(waterpoint_layer.wkbType())
    crs = waterpoint_layer.crs().authid()
    tmp_lyr = QgsVectorLayer(f'{wkb}?crs={crs}', '', 'memory')
    tmp_lyr.dataProvider().addAttributes(waterpoint_layer.fields())
    tmp_lyr.updateFields()
    tmp_lyr.dataProvider().addFeatures(waterpoint_feats)
    
    ############################################################################
    # Rasterise temporary waterpoint layer to create a binary raster where pixel value
    # is 1 at water locations and 0 everywhere else
    raster_extent = paddock.geometry().boundingBox()
    xmin = raster_extent.xMinimum()
    xmax = raster_extent.xMaximum()
    ymin = raster_extent.yMinimum()
    ymax = raster_extent.yMaximum()
    
    extent_string = f'{xmin},{xmax},{ymin},{ymax} [{tmp_lyr.crs().authid()}]'
#    print(extent_string)
#ext = '670539.640100000,674839.662800000,8101017.562800000,8103145.602500000 [EPSG:28352]'

    rasterize_params = {'INPUT':tmp_lyr,
                        'FIELD':'',
                        'BURN':1,
                        'USE_Z':False,
                        'UNITS':1,
                        'WIDTH':10,
                        'HEIGHT':10,
                        'EXTENT':extent_string,
                        'NODATA':-1,
                        'OPTIONS':'',
                        'DATA_TYPE':0,
                        'INIT':0,
                        'INVERT':False,
                        'EXTRA':'',
                        'OUTPUT':'TEMPORARY_OUTPUT'}
    
    rasterised_waterpoints = processing.run("gdal:rasterize", rasterize_params)
    ############################################################################
    # Calculate Proximity Raster for each waterpoint binary raster...
    proximity_params = {'INPUT':rasterised_waterpoints['OUTPUT'],
                        'BAND':1,
                        'VALUES':'1',
                        'UNITS':0,
                        'MAX_DISTANCE':0,
                        'REPLACE':0,
                        'NODATA':0,
                        'OPTIONS':'',
                        'EXTRA':'',
                        'DATA_TYPE':5,
                        'OUTPUT':'TEMPORARY_OUTPUT'}

    water_proximity = processing.run("gdal:proximity", proximity_params)
    ############################################################################
    # Clip proximity raster to paddock...
    
    paddock_layer.selectByIds([paddock.id()])
    
    clipped_path = os.path.join(out_dir, f'{paddock[paddock_name_field]}.tif')
    
    clip_params = {'INPUT':water_proximity['OUTPUT'],
                    'MASK':QgsProcessingFeatureSourceDefinition(paddock_layer.source(), selectedFeaturesOnly=True, featureLimit=-1, geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),
                    'SOURCE_CRS':None,
                    'TARGET_CRS':None,
                    'NODATA':-9999,
                    'ALPHA_BAND':False,
                    'CROP_TO_CUTLINE':True,
                    'KEEP_RESOLUTION':False,
                    'SET_RESOLUTION':False,
                    'X_RESOLUTION':None,
                    'Y_RESOLUTION':None,
                    'MULTITHREADING':False,
                    'OPTIONS':'',
                    'DATA_TYPE':0,
                    'EXTRA':'',
                    'OUTPUT':clipped_path}
    
    processing.run("gdal:cliprasterbymasklayer", clip_params)
    
    print(f'{paddock[paddock_name_field]} done')
    
paddock_layer.removeSelection()

print('Completed')


