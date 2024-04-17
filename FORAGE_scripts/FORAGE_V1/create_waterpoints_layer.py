project = QgsProject.instance()

output_waterpoints = QgsVectorLayer('Point?crs=epsg:7845', 'Waterpoints', 'memory')

output_waterpoints.dataProvider().addAttributes([QgsField('FEATURE', QVariant.String),
                                                QgsField('NAME', QVariant.String),
                                                QgsField('DISTRICT', QVariant.String),
                                                QgsField('PROPERTY', QVariant.String)])
                                                
output_waterpoints.updateFields()

def transformed_geom(g, src_crs, dest_crs):
    geom = QgsGeometry().fromWkt(g.asWkt())
    xform = QgsCoordinateTransform(src_crs, dest_crs, QgsProject.instance())
    if src_crs.authid() != dest_crs.authid():
        geom.transform(xform)
    geom.convertToSingleType()
    return geom
    
wpt_feats = []
    
kdm_wpts = project.mapLayersByName('KID_WATERPOINTS')[0]
for ft in kdm_wpts.getFeatures():
    ft_geom = transformed_geom(ft.geometry(), kdm_wpts.crs(), output_waterpoints.crs())
    wpt_feat = QgsFeature(output_waterpoints.fields())
    wpt_feat.setGeometry(ft_geom)
    wpt_feat.setAttributes([ft['Type'],
                            ft['NAME'],
                            'VRD',
                            'Kidman'])
    wpt_feats.append(wpt_feat)

mrk_wpts = project.mapLayersByName('mrk_wpts')[0]
for ft in mrk_wpts.getFeatures():
    ft_geom = transformed_geom(ft.geometry(), mrk_wpts.crs(), output_waterpoints.crs())
    wpt_feat = QgsFeature(output_waterpoints.fields())
    wpt_feat.setGeometry(ft_geom)
    wpt_feat.setAttributes([ft['FEATURE'],
                            ft['LABEL'],
                            ft['DISTRICT'],
                            ft['PROPERTY']])
    wpt_feats.append(wpt_feat)

omp_wpts = project.mapLayersByName('OMP_TROUGHS')[0]
for ft in omp_wpts.getFeatures():
    ft_geom = transformed_geom(ft.geometry(), omp_wpts.crs(), output_waterpoints.crs())
    wpt_feat = QgsFeature(output_waterpoints.fields())
    wpt_feat.setGeometry(ft_geom)
    wpt_feat.setAttributes(['Trough',
                            NULL,
                            'Southern Alice Springs',
                            'Old Man Plains'])
    wpt_feats.append(wpt_feat)

output_waterpoints.dataProvider().addFeatures(wpt_feats)
output_waterpoints.updateExtents()
project.addMapLayer(output_waterpoints)
