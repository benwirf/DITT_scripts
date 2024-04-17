# ALL LAYERS ARE IN EPSG:7845

project = QgsProject.instance()
land_types_layer = project.mapLayersByName('Land_Types')[0]# Existing land types layer (Kidman, OMP etc.)

rok_bdry_lyr = project.mapLayersByName('rocklands_nt_boundary')[0]

lt_feats = []

rok_nt_ls_lyr = project.mapLayersByName('rocklands_ntls_lambert')[0]

output_fields = ['fid', 'SURVEY_ID', 'LAND_TYPE', 'MAP_UNIT', 'CLASS', 'SOIL_DESC', 'VEG_DESC', 'AREA_KM2']# For reference only (var not used)

fid = max([ft['fid'] for ft in land_types_layer.getFeatures()])+1

rok_bdry_ft = next(iface.activeLayer().getFeatures())
rok_bdry_buff = rok_bdry_ft.geometry().buffer(5000, 25)# EPSG:7845
rok_rect = rok_bdry_buff.boundingBox()

# ADD LAND SYSTEMS
rok_nt_ls_idx = QgsSpatialIndex(rok_nt_ls_lyr.getFeatures())
rok_nt_ls_candidates = rok_nt_ls_idx.intersects(rok_rect)
for ft in rok_nt_ls_lyr.getFeatures(rok_nt_ls_candidates):
    ft_geom = ft.geometry()# EPSG:7845
    if ft_geom.intersects(rok_bdry_buff):
        lt_ix = ft_geom.intersection(rok_bdry_buff)
        lt_feat = QgsFeature(land_types_layer.fields())
        lt_feat.setGeometry(lt_ix)
        lt_feat.setAttributes([fid,
                                ft['SURVEY_ID'],
                                ft['LANDSYSTEM'],
                                ft['MAPUNIT'],
                                ft['CLASS'],
                                ft['SOIL_ASC'],
                                ft['VEGETATION'],
                                round(lt_ix.area()/1000000, 3)])
        lt_feats.append(lt_feat)
        fid+=1

print(lt_feats)
res = land_types_layer.dataProvider().addFeatures(lt_feats)
print(res)
land_types_layer.updateExtents()
land_types_layer.triggerRepaint()

print('Done')