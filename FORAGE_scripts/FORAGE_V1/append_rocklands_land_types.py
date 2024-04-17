# ALL LAYERS ARE IN EPSG:7845

project = QgsProject.instance()
land_types_layer = project.mapLayersByName('Land_Types')[0]# Existing land types layer (Kidman, OMP etc.)

rok_bdry_lyr = project.mapLayersByName('rocklands_boundary')[0]

lt_feats = []

rok_nt_lt_lyr = project.mapLayersByName('rocklands_nt_land_types')[0]

output_fields = ['fid', 'SURVEY_ID', 'LAND_TYPE', 'MAP_UNIT', 'CLASS', 'SOIL_DESC', 'VEG_DESC', 'AREA_KM2']

fid = max([ft['fid'] for ft in land_types_layer.getFeatures()])+1

rok_bdry_ft = rok_bdry_lyr.getFeature(1)
rok_bdry_buff = rok_bdry_ft.geometry().buffer(5000, 25)# EPSG:7845
rok_rect = rok_bdry_buff.boundingBox()

# ADD NT LAND TYPES
rok_nt_lt_idx = QgsSpatialIndex(rok_nt_lt_lyr.getFeatures())
rok_nt_lt_candidates = rok_nt_lt_idx.intersects(rok_rect)
for ft in rok_nt_lt_lyr.getFeatures(rok_nt_lt_candidates):
    ft_geom = ft.geometry()# EPSG:7845
    if ft_geom.intersects(rok_bdry_buff):
        lt_ix = ft_geom.intersection(rok_bdry_buff)
        lt_feat = QgsFeature(land_types_layer.fields())
        lt_feat.setGeometry(lt_ix)
        lt_feat.setAttributes([fid,
                                ft['SURVEY_ID'],
                                ft['LAND_TYPE'],
                                ft['LAND_TYPE'],
                                ft['LANDSCAPE'],
                                f'{ft["SOIL"]};{ft["LS_DESC"]}',
                                ft['VEG_DESC'],
                                round(lt_ix.area()/1000000, 3)])
        lt_feats.append(lt_feat)
        fid+=1

rok_qld_lt_lyr = project.mapLayersByName('rocklands_qld_land_types')[0]

# ADD QLD LAND TYPES
rok_qld_lt_idx = QgsSpatialIndex(rok_qld_lt_lyr.getFeatures())
rok_qld_lt_candidates = rok_qld_lt_idx.intersects(rok_rect)
for ft in rok_qld_lt_lyr.getFeatures(rok_qld_lt_candidates):
    ft_geom = ft.geometry()# EPSG:7845
    if ft_geom.intersects(rok_bdry_buff):
        lt_ix = ft_geom.intersection(rok_bdry_buff)
        lt_feat = QgsFeature(land_types_layer.fields())
        lt_feat.setGeometry(lt_ix)
        lt_feat.setAttributes([fid,
                                'DAF QLD GLM Land Types',
                                ft['RE1'],
                                ft['RE1_ClimZ_'],
                                ft['LT_NAME'],
                                NULL,
                                NULL,
                                round(lt_ix.area()/1000000, 3)])
        lt_feats.append(lt_feat)
        fid+=1
        
land_types_layer.dataProvider().addFeatures(lt_feats)

print('Done')
