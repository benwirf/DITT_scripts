# BOTH LAYERS IN EPSG:7845
project = QgsProject.instance()
land_types_layer = project.mapLayersByName('Forage_Land_Types')[0]# Existing land types layer (Kidman, OMP etc.)

output_fields = ['fid', 'SURVEY_ID', 'LAND_TYPE', 'MAP_UNIT', 'CLASS', 'SOIL_DESC', 'VEG_DESC', 'AREA_KM2']# For reference only (var not used)

fts_to_add = []

ls_patch_lyr = project.mapLayersByName('ntls_patch')[0]

fid = max([ft['fid'] for ft in land_types_layer.getFeatures()])+1

for ft in ls_patch_lyr.getFeatures():
    ls_feat = QgsFeature(land_types_layer.fields())
    ls_feat.setGeometry(ft.geometry())
    ls_feat.setAttributes([fid,
                            ft['SURVEY_ID'],
                            ft['LANDSYSTEM'],
                            ft['MAPUNIT'],
                            ft['CLASS'],
                            ft['SOIL_ASC'],
                            ft['VEGETATION'],
                            round(ft.geometry().area()/1000000, 3)])
    fts_to_add.append(ls_feat)
    fid+=1

land_types_layer.dataProvider().addFeatures(fts_to_add)

land_types_layer.updateExtents()

print('Done')