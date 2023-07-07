wa_lyr = QgsProject.instance().mapLayersByName('ANT_NO5_SPLIT_GR3_TOP_WATER')[0]
lc_lyr = QgsProject.instance().mapLayersByName('Landcon_no456')[0]

lc_idx = QgsSpatialIndex(lc_lyr.getFeatures(QgsFeatureRequest().setDestinationCrs(QgsCoordinateReferenceSystem('EPSG:7845'), QgsProject.instance().transformContext())))

def transformed_geom(g, src_crs):
    tgt_crs = QgsCoordinateReferenceSystem('EPSG:7845')
    xform = QgsCoordinateTransform(src_crs, tgt_crs, QgsProject.instance())
    new_geom = QgsGeometry.fromWkt(g.asWkt())
    new_geom.transform(xform)
    return new_geom

# Create a memory layer to hold results
output_layer = QgsVectorLayer('Polygon?crs=EPSG:7845', 'Watered Land Condition', 'memory')
flds = [QgsField('Property', QVariant.String),
        QgsField('Paddock', QVariant.String),
        QgsField('Water_Dist', QVariant.String),
        QgsField('Land_Condition', QVariant.String),
        QgsField('Area_m2', QVariant.Double, len=10, prec=3),
        QgsField('Area_ha', QVariant.Double, len=10, prec=3),
        QgsField('Area_km2', QVariant.Double, len=10, prec=5),
        QgsField('Percent', QVariant.Double, len=10, prec=1)]
        
output_layer.dataProvider().addAttributes(flds)
output_layer.updateFields()

    
pdk_names = wa_lyr.uniqueValues(wa_lyr.fields().lookupField('name'))

for pdk_name in pdk_names:
#    print(pdk_name)
    ###############################3km WATERED AREA############################
    wa_3km_fts = [ft for ft in wa_lyr.getFeatures() if ft['name'] == pdk_name and int(ft['tobufdist']) == 3000]
    if wa_3km_fts:
        if len(wa_3km_fts) > 1:
            wa_3km_geom = QgsGeometry.collectGeometry([f.geometry() for f in wa_3km_fts])
        else:
            wa_3km_geom = wa_3km_fts[0].geometry()
    wa_3km_geom_transformed = transformed_geom(wa_3km_geom, wa_lyr.sourceCrs())
    wa_3km_land_condition_candidate_ids = lc_idx.intersects(wa_3km_geom_transformed.boundingBox())
#    print(wa_3km_land_condition_fts)
    wa_3km_land_condition_fts = [ft for ft in lc_lyr.getFeatures(wa_3km_land_condition_candidate_ids) if transformed_geom(ft.geometry(), lc_lyr.sourceCrs()).intersects(wa_3km_geom_transformed)]
#    print(wa_3km_land_condition_fts)
    wa_3km_LCs = list(set([f['LCOverall_'] for f in wa_3km_land_condition_fts]))
#    print(wa_3km_LCs)
    lc_3km_percentages = []
    for lc in wa_3km_LCs:
        lc_feats = [ft for ft in wa_3km_land_condition_fts if ft['LCOverall_'] == lc]
        geom_intersections = [transformed_geom(ft.geometry(), lc_lyr.sourceCrs()).intersection(wa_3km_geom_transformed) for ft in lc_feats]
        lc_intersection = QgsGeometry.collectGeometry(geom_intersections)
        #
        lc_area_m2 = round(lc_intersection.area(), 3)
        lc_area_ha = round(lc_intersection.area()/10000, 3)
        lc_area_km2 = round(lc_intersection.area()/1000000, 5)
        lc_pcnt = (lc_area_m2/wa_3km_geom_transformed.area())*100
        lc_3km_percentages.append(lc_pcnt)
        #
        new_feat = QgsFeature(output_layer.fields())
        new_feat.setGeometry(lc_intersection)
        new_feat.setAttributes(['ANTHONY_LAGOON', pdk_name, '0-3km', lc, lc_area_m2, lc_area_ha, lc_area_km2, lc_pcnt])
        output_layer.dataProvider().addFeatures([new_feat])
    pcnt_checksum = round(sum(lc_3km_percentages), 1)
    print(pcnt_checksum)# Should be 100

    ###############################5km WATERED AREA############################
    wa_5km_fts = [ft for ft in wa_lyr.getFeatures() if ft['name'] == pdk_name and int(ft['tobufdist']) == 5000]
    if wa_5km_fts:
        if len(wa_5km_fts) > 1:
            wa_5km_geom = QgsGeometry.collectGeometry([f.geometry() for f in wa_5km_fts])
        else:
            wa_5km_geom = wa_5km_fts[0].geometry()
    wa_5km_geom_transformed = transformed_geom(wa_5km_geom, wa_lyr.sourceCrs())
    wa_5km_land_condition_candidate_ids = lc_idx.intersects(wa_5km_geom_transformed.boundingBox())
#    print(wa_5km_land_condition_fts)
    wa_5km_land_condition_fts = [ft for ft in lc_lyr.getFeatures(wa_5km_land_condition_candidate_ids) if transformed_geom(ft.geometry(), lc_lyr.sourceCrs()).intersects(wa_5km_geom_transformed)]
#    print(wa_5km_land_condition_fts)
    wa_5km_LCs = list(set([f['LCOverall_'] for f in wa_5km_land_condition_fts]))
#    print(wa_5km_LCs)
    lc_5km_percentages = []
    for lc in wa_5km_LCs:
        lc_feats = [ft for ft in wa_5km_land_condition_fts if ft['LCOverall_'] == lc]
        geom_intersections = [transformed_geom(ft.geometry(), lc_lyr.sourceCrs()).intersection(wa_5km_geom_transformed) for ft in lc_feats]
        lc_intersection = QgsGeometry.collectGeometry(geom_intersections)
        #
        lc_area_m2 = round(lc_intersection.area(), 3)
        lc_area_ha = round(lc_intersection.area()/10000, 3)
        lc_area_km2 = round(lc_intersection.area()/1000000, 5)
        lc_pcnt = (lc_area_m2/wa_5km_geom_transformed.area())*100
        lc_5km_percentages.append(lc_pcnt)
        #
        new_feat = QgsFeature(output_layer.fields())
        new_feat.setGeometry(lc_intersection)
        new_feat.setAttributes(['ANTHONY_LAGOON', pdk_name, '3km-5km', lc, lc_area_m2, lc_area_ha, lc_area_km2, lc_pcnt])
        output_layer.dataProvider().addFeatures([new_feat])
    pcnt_checksum = round(sum(lc_5km_percentages), 1)
    print(pcnt_checksum)# Should be 100
    
    ###############################UNWATERED AREA############################
    unwatered_fts = [ft for ft in wa_lyr.getFeatures() if ft['name'] == pdk_name and int(ft['tobufdist']) == -99]
    if unwatered_fts:
        if len(unwatered_fts) > 1:
            unwatered_geom = QgsGeometry.collectGeometry([f.geometry() for f in unwatered_fts])
        else:
            unwatered_geom = unwatered_fts[0].geometry()
    unwatered_geom_transformed = transformed_geom(unwatered_geom, wa_lyr.sourceCrs())
    unwatered_land_condition_candidate_ids = lc_idx.intersects(unwatered_geom_transformed.boundingBox())
    unwatered_land_condition_fts = [ft for ft in lc_lyr.getFeatures(unwatered_land_condition_candidate_ids) if transformed_geom(ft.geometry(), lc_lyr.sourceCrs()).intersects(unwatered_geom_transformed)]
#    print(unwatered_land_condition_fts)
    unwatered_LCs = list(set([f['LCOverall_'] for f in unwatered_land_condition_fts]))
#    print(unwatered_LCs)
    unwatered_percentages = []
    for lc in unwatered_LCs:
        lc_feats = [ft for ft in unwatered_land_condition_fts if ft['LCOverall_'] == lc]
        geom_intersections = [transformed_geom(ft.geometry(), lc_lyr.sourceCrs()).intersection(unwatered_geom_transformed) for ft in lc_feats]
        lc_intersection = QgsGeometry.collectGeometry(geom_intersections)
        #
        lc_area_m2 = round(lc_intersection.area(), 3)
        lc_area_ha = round(lc_intersection.area()/10000, 3)
        lc_area_km2 = round(lc_intersection.area()/1000000, 5)
        lc_pcnt = (lc_area_m2/unwatered_geom_transformed.area())*100
        unwatered_percentages.append(lc_pcnt)
        #
        new_feat = QgsFeature(output_layer.fields())
        new_feat.setGeometry(lc_intersection)
        new_feat.setAttributes(['ANTHONY_LAGOON', pdk_name, 'Unwatered', lc, lc_area_m2, lc_area_ha, lc_area_km2, lc_pcnt])
        output_layer.dataProvider().addFeatures([new_feat])
    pcnt_checksum = round(sum(unwatered_percentages), 1)
    print(pcnt_checksum)# Should be 100
            
if output_layer.isValid():
    QgsProject.instance().addMapLayer(output_layer)
else:
    print('Output layer not valid')