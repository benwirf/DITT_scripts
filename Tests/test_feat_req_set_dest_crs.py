project = QgsProject.instance()

# Works on these layers...
#pt_lyr = project.mapLayersByName('point')[0]# 4326
#poly_lyr = project.mapLayersByName('poly')[0]# 28352

# Not on these layers! WTF?!!!
pt_lyr = project.mapLayersByName('Mulga_Park_waterpoints')[0]# 4326
poly_lyr = project.mapLayersByName('Paddocks_UTM')[0]# 28352
#print(poly_lyr.sourceCrs().isValid())
crs = poly_lyr.sourceCrs()
prepared_waterpoints = pt_lyr.materialize(QgsFeatureRequest().setSubsetOfAttributes([]).setDestinationCrs(crs, project.transformContext()))
prepared_paddocks = poly_lyr.materialize(QgsFeatureRequest().setSubsetOfAttributes([poly_lyr.fields().lookupField('LABEL')]))
#poly_it = poly_lyr.getFeatures()
#for f in poly_it:
#    print(f.geometry())

#for p in prepared_polys.getFeatures():
#    print(p.geometry().isGeosValid())
#    pad_name = p['LABEL']
#    print(pad_name)
##    print(p.geometry())
#    wpts = [x for x in prepared_pts.getFeatures() if x.geometry().within(p.geometry())]
#    print(wpts)
#    print('--------------')
    
for paddock in prepared_paddocks.getFeatures():
    paddock_name = paddock['LABEL']
    # Simple spatial query to retrieve water points within each paddock
    waterpoint_feats = [f for f in prepared_waterpoints.getFeatures() if f.geometry().intersects(paddock.geometry())]
#    model_feedback.pushInfo(repr(waterpoint_feats))
    if not waterpoint_feats:
        continue
#    model_feedback.pushInfo(repr(crs))
    # Create a temporary layer to hold waterpoint features which fall within each paddock
    tmp_lyr = QgsVectorLayer(f'Point?crs={crs.authid()}', f'{paddock_name}_waters', 'memory')
    tmp_lyr.dataProvider().addFeatures(waterpoint_feats)
    project.addMapLayer(tmp_lyr)
    
