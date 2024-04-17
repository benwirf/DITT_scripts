# BOTH LAYERS IN EPSG:7845
project = QgsProject.instance()
land_types_layer = project.mapLayersByName('Land_Types')[0]# Existing land types layer (Kidman, OMP etc.)

output_land_types = QgsVectorLayer('Polygon?crs=epsg:7845', 'Forage_Land_Types', 'memory')

flds = [fld for fld in land_types_layer.fields()]

flds.insert(1, QgsField('Property', QVariant.String))

#print(flds)
for fld in flds:
    output_land_types.dataProvider().addAttributes([fld])

output_land_types.updateFields()

lt_fields = ['fid', 'SURVEY_ID', 'LAND_TYPE', 'MAP_UNIT', 'CLASS', 'SOIL_DESC', 'VEG_DESC', 'AREA_KM2']# For reference only (var not used)

fts_to_add = []

for ft in land_types_layer.getFeatures():
    if ft['SURVEY_ID'] == 'VRD':
        prop = 'Kidman'
    elif ft['SURVEY_ID'] == 'MTRID_250':
        prop = 'Mt Riddock'
    elif ft['SURVEY_ID'] == 'owsp_250':
        prop = 'OMP'
    elif ft['SURVEY_ID'] == 'ZCL2':
        prop = 'Rocklands'
    feat = QgsFeature(output_land_types.fields())
    feat.setGeometry(ft.geometry())
    atts = [att for att in ft.attributes()]
    atts.insert(1, prop)
    feat.setAttributes(atts)
    fts_to_add.append(feat)
    
output_land_types.dataProvider().addFeatures(fts_to_add)
output_land_types.updateExtents()
if output_land_types.isValid():
    project.addMapLayer(output_land_types)
print('Done')