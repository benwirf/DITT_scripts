project = QgsProject.instance()

output_land_types = QgsVectorLayer('Polygon?crs=epsg:7845', 'Land_Types', 'memory')

output_land_types.dataProvider().addAttributes([QgsField('SURVEY_ID', QVariant.String),
                                                QgsField('LAND_TYPE', QVariant.String),
                                                QgsField('MAP_UNIT', QVariant.String),
                                                QgsField('CLASS', QVariant.String),
                                                QgsField('SOIL_DESC', QVariant.String),
                                                QgsField('VEG_DESC', QVariant.String),
                                                QgsField('AREA_KM2', QVariant.Double)])

output_land_types.updateFields()

def transformed_geom(g, src_crs, dest_crs):
    geom = QgsGeometry().fromWkt(g.asWkt())
    xform = QgsCoordinateTransform(src_crs, dest_crs, QgsProject.instance())
    if src_crs.authid() != dest_crs.authid():
        geom.transform(xform)
    return geom
    
bdry_lyr = project.mapLayersByName('Station_Boundaries')[0]

lt_feats = []

kdm_lt = project.mapLayersByName('vrd_100')[0]
kdm_lt_idx = QgsSpatialIndex(kdm_lt.getFeatures())
kdm_bdry_ft = [ft for ft in bdry_lyr.getFeatures() if ft['NAME'] == 'Kidman Springs Research Station'][0]
kdm_bdry_buff = kdm_bdry_ft.geometry().buffer(5000, 25)# EPSG:7845
kdm_bdry_buff_4283 = transformed_geom(kdm_bdry_buff, bdry_lyr.crs(), kdm_lt.crs())# EPSG:4283
kdm_rect = kdm_bdry_buff_4283.boundingBox()
kdm_lt_candidates = kdm_lt_idx.intersects(kdm_rect)
for ft in kdm_lt.getFeatures(kdm_lt_candidates):
    ft_geom = transformed_geom(ft.geometry(), kdm_lt.crs(), bdry_lyr.crs())# EPSG:7845
    if ft_geom.intersects(kdm_bdry_buff):
        lt_ix = ft_geom.intersection(kdm_bdry_buff)
        lt_feat = QgsFeature(output_land_types.fields())
        lt_feat.setGeometry(lt_ix)
        lt_feat.setAttributes([ft['SURVEY_ID'],
                                ft['LAND_UNIT'],
                                ft['LAND_UNIT'],
                                ft['LF_CLASS'],
                                ft['SOIL_DESC'],
                                ft['VEG_DESC_1'],
                                round(lt_ix.area()/1000000, 3)])
        lt_feats.append(lt_feat)


mrk_lt = project.mapLayersByName('mtrid_250')[0]
mrk_lt_idx = QgsSpatialIndex(mrk_lt.getFeatures())
mrk_bdry_ft = [ft for ft in bdry_lyr.getFeatures() if ft['NAME'] == 'Mount Riddock'][0]
mrk_bdry_buff = mrk_bdry_ft.geometry().buffer(5000, 25)# EPSG:7845
###***Most of these geometric operations unnecessary since all land types are within boundary
mrk_bdry_buff_4283 = transformed_geom(mrk_bdry_buff, bdry_lyr.crs(), mrk_lt.crs())# EPSG:4283
mrk_rect = mrk_bdry_buff_4283.boundingBox()
mrk_lt_candidates = mrk_lt_idx.intersects(mrk_rect)
for ft in mrk_lt.getFeatures(mrk_lt_candidates):
    ft_geom = transformed_geom(ft.geometry(), mrk_lt.crs(), bdry_lyr.crs())# EPSG:7845
    if ft_geom.intersects(mrk_bdry_buff):
        lt_ix = ft_geom.intersection(mrk_bdry_buff)
        lt_feat = QgsFeature(output_land_types.fields())
        lt_feat.setGeometry(lt_ix)
        lt_feat.setAttributes([ft['SurveyID'],
                                ft['LandSystem'],
                                ft['MapUnit'],
                                ft['MapClass'],
                                ft['SoilDesc'],
                                ft['VegDesc'],
                                round(lt_ix.area()/1000000, 3)])
        lt_feats.append(lt_feat)
###***

omp_lt = project.mapLayersByName('owsp_250')[0]
omp_lt_idx = QgsSpatialIndex(omp_lt.getFeatures())
omp_bdry_ft = [ft for ft in bdry_lyr.getFeatures() if ft['NAME'] == 'Old Man Plains Research Station'][0]
omp_bdry_buff = omp_bdry_ft.geometry().buffer(5000, 25)# EPSG:7845
###***
omp_bdry_buff_4283 = transformed_geom(omp_bdry_buff, bdry_lyr.crs(), omp_lt.crs())# EPSG:4283
omp_rect = omp_bdry_buff_4283.boundingBox()
omp_lt_candidates = omp_lt_idx.intersects(omp_rect)
for ft in omp_lt.getFeatures(omp_lt_candidates):
    ft_geom = transformed_geom(ft.geometry(), omp_lt.crs(), bdry_lyr.crs())# EPSG:7845
    if ft_geom.intersects(omp_bdry_buff):
        lt_ix = ft_geom.intersection(omp_bdry_buff)
        lt_feat = QgsFeature(output_land_types.fields())
        lt_feat.setGeometry(lt_ix)
        lt_feat.setAttributes([ft['SurveyID'],
                                ft['LandSystem'],
                                ft['MapUnit'],
                                ft['MapClass'],
                                ft['SoilDesc'],
                                ft['VegDesc'],
                                round(lt_ix.area()/1000000, 3)])
        lt_feats.append(lt_feat)
###***

output_land_types.dataProvider().addFeatures(lt_feats)
output_land_types.updateExtents()
project.addMapLayer(output_land_types)
