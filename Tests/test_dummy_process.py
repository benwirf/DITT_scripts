project = QgsProject.instance()

pt_lyr = project.mapLayersByName('Mulga_Park_waterpoints')[0]# 4326
poly_lyr = project.mapLayersByName('Paddocks_UTM')[0]# 28352
#print(poly_lyr.sourceCrs().isValid())
crs = poly_lyr.sourceCrs()
prepared_waterpoints = pt_lyr.materialize(QgsFeatureRequest().setSubsetOfAttributes([]).setDestinationCrs(crs, project.transformContext()))
prepared_paddocks = poly_lyr.materialize(QgsFeatureRequest().setSubsetOfAttributes([poly_lyr.fields().lookupField('LABEL')]))
    
for paddock in prepared_paddocks.getFeatures():
    paddock_name = paddock['LABEL']
    # Simple spatial query to retrieve water points within each paddock
    waterpoint_feats = [f for f in prepared_waterpoints.getFeatures() if f.geometry().intersects(paddock.geometry())]
    if not waterpoint_feats:
        continue
    # Create a temporary layer to hold waterpoint features which fall within each paddock
    tmp_lyr = QgsVectorLayer(f'Point?crs={crs.authid()}', f'{paddock_name}_waters', 'memory')
    tmp_lyr.dataProvider().addFeatures(waterpoint_feats)
#    project.addMapLayer(tmp_lyr)

    ############################################################################
    # Rasterise temporary waterpoint layer to create a binary raster where pixel value
    # is 1 at water locations and 0 everywhere else
    raster_extent = paddock.geometry().boundingBox()
    xmin = raster_extent.xMinimum()
    xmax = raster_extent.xMaximum()
    ymin = raster_extent.yMinimum()
    ymax = raster_extent.yMaximum()
    
    extent_string = f'{xmin},{xmax},{ymin},{ymax} [{tmp_lyr.crs().authid()}]'
    #extent_string = '670539.640100000,674839.662800000,8101017.562800000,8103145.602500000 [EPSG:28352]'

    rasterize_params = {'INPUT':tmp_lyr,
                        'FIELD':'',
                        'BURN':1,
                        'USE_Z':False,
                        'UNITS':1,
                        'WIDTH':100,
                        'HEIGHT':100,
                        'EXTENT':extent_string,
                        'NODATA':-1,
                        'OPTIONS':'',
                        'DATA_TYPE':0,
                        'INIT':0,
                        'INVERT':False,
                        'EXTRA':'',
                        'OUTPUT':'TEMPORARY_OUTPUT'}
                        
    rasterized = processing.run("gdal:rasterize", rasterize_params)
    
    proximity_params = {'INPUT':rasterized['OUTPUT'],
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
                    
    prox = processing.run("gdal:proximity", proximity_params)
    
    paddock_layer_subset = prepared_paddocks.materialize(QgsFeatureRequest(paddock.id()))
    
    clip_params = {'INPUT':prox['OUTPUT'],
                    'MASK':paddock_layer_subset,
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
                    'OUTPUT':'TEMPORARY_OUTPUT'}
                    
    processing.runAndLoadResults("gdal:cliprasterbymasklayer", clip_params)
