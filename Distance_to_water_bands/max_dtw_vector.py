project = QgsProject.instance()

pdk_lyr = project.mapLayersByName('MGP_all_paddocks')[0]

name_fld = 'LABEL'

waterpoint_lyr = project.mapLayersByName('MGP_waterpoints')[0]

output_lyr = project.mapLayersByName('Watered_bands')[0]

distance_lyr = QgsVectorLayer('LineString?crs=epsg:9473', 'max_distance_lines', 'memory')

flds = QgsFields()

flds_to_add = [QgsField('Pdk Name', QVariant.String),
                QgsField('Max_DTW', QVariant.Double, len=10, prec=1)]
                
for fld in flds_to_add:
    flds.append(fld)
    
distance_lyr.dataProvider().addAttributes(flds)
distance_lyr.updateFields()

for pdk in pdk_lyr.getFeatures():
    pdk_name = pdk[name_fld]
    pdk_wpts = [wp.geometry() for wp in waterpoint_lyr.getFeatures() if wp.geometry().within(pdk.geometry())]
    if not pdk_wpts:
        continue
    pdk_water_band_feats = [ft for ft in output_lyr.getFeatures() if ft['Pdk Name'] == pdk_name]
    max_band_dist = max(ft['Outer dist'] for ft in pdk_water_band_feats)
    max_band_dist_feat = [ft for ft in pdk_water_band_feats if ft['Outer dist'] == max_band_dist][0]
    nearest_wpt_to_farthest_band = QgsGeometry.collectGeometry(pdk_wpts).nearestPoint(max_band_dist_feat.geometry())
    all_vert_distances = []
    for v in max_band_dist_feat.geometry().vertices():
        water_dist = nearest_wpt_to_farthest_band.asPoint().distance(QgsPointXY(v))
        all_vert_distances.append(water_dist)
    # print(all_vert_distances)
    max_dtw = max(all_vert_distances)
    farthest_vertex = [v for v in max_band_dist_feat.geometry().vertices() if QgsPointXY(v).distance(nearest_wpt_to_farthest_band.asPoint()) == max_dtw][0]
    line_geom = QgsGeometry().fromPolyline([QgsPoint(nearest_wpt_to_farthest_band.asPoint()), farthest_vertex])
    feat = QgsFeature(distance_lyr.fields())
    feat.setGeometry(line_geom)
    feat.setAttributes([pdk_name, float(round(max_dtw, 1))])
    distance_lyr.dataProvider().addFeatures([feat])
    print(f'Maximum distance to water in {pdk_name}: {max_dtw}m')
    
project.addMapLayers([distance_lyr])