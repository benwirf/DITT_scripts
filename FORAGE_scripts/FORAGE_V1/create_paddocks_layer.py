project = QgsProject.instance()

output_paddocks = QgsVectorLayer('Polygon?crs=epsg:7845', 'Pdk_Boundaries', 'memory')

output_paddocks.dataProvider().addAttributes([QgsField('NAME', QVariant.String),
                                                QgsField('DISTRICT', QVariant.String),
                                                QgsField('PROPERTY', QVariant.String),
                                                QgsField('AREA_KM2',QVariant.Double)])
                                                
output_paddocks.updateFields()

def paddock_geom(g, src_crs):
    geom = QgsGeometry().fromWkt(g.asWkt())
    dest_crs = QgsCoordinateReferenceSystem('epsg:7845')
    xform = QgsCoordinateTransform(src_crs, dest_crs, QgsProject.instance())
    if src_crs.authid() != dest_crs.authid():
        geom.transform(xform)
    filled_geom = geom.removeInteriorRings()
    return filled_geom
    
pdk_feats = []
    
kdm_pdks = project.mapLayersByName('Kidman_Paddocks')[0]
null_count = 1
for ft in kdm_pdks.getFeatures():
    pdk_geom = paddock_geom(ft.geometry(), kdm_pdks.crs())
    if pdk_geom.area() > 1000000 or ft['Name'] != NULL:
        pdk_feat = QgsFeature(output_paddocks.fields())
        if ft['Name'] != NULL:
            atts = [ft['Name'], 'VRD', 'Kidman', round(pdk_geom.area()/1000000, 5)]
        else:
            atts = [f'KDM_no-name_{null_count}', 'VRD', 'Kidman', round(pdk_geom.area()/1000000, 5)]
        pdk_feat.setGeometry(pdk_geom)
        pdk_feat.setAttributes(atts)
        pdk_feats.append(pdk_feat)
        
# Mt Riddock
mrk_pdks = project.mapLayersByName('mrk_pdks_slct')[0]
null_count = 1
for ft in mrk_pdks.getFeatures():
    pdk_geom = paddock_geom(ft.geometry(), mrk_pdks.crs())
    pdk_feat = QgsFeature(output_paddocks.fields())
    pdk_feat.setGeometry(pdk_geom)
    if ft['LABEL'] != NULL:
        atts = [ft['LABEL'], 'Northern Alice Springs', 'Mount Riddock', round(pdk_geom.area()/1000000, 5)]
    else:
        atts = [f'MRK_no-name_{null_count}', 'Northern Alice Springs', 'Mount Riddock', round(pdk_geom.area()/1000000, 5)]
        null_count+=1
    pdk_feat.setAttributes(atts)
    pdk_feats.append(pdk_feat)
    
# OMP
omp_pdks = project.mapLayersByName('OMP_PDKS')[0]
null_count = 1
for ft in omp_pdks.getFeatures():
    pdk_geom = paddock_geom(ft.geometry(), omp_pdks.crs())
    if pdk_geom.area() > 1000000:
        pdk_feat = QgsFeature(output_paddocks.fields())
        pdk_feat.setGeometry(pdk_geom)
        if ft['NAME'] != NULL:
            atts = [ft['NAME'], 'Southern Alice Springs', 'Old Man Plains', round(pdk_geom.area()/1000000, 5)]
        else:
            atts = [f'OMP_no-name_{null_count}', 'Southern Alice Springs', 'Old Man Plains', round(pdk_geom.area()/1000000, 5)]
            null_count+=1
        pdk_feat.setAttributes(atts)
        pdk_feats.append(pdk_feat)
        
output_paddocks.dataProvider().addFeatures(pdk_feats)

project.addMapLayer(output_paddocks)