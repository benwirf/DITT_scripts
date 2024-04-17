project = QgsProject.instance()

pdk_lyr = project.mapLayersByName('Mt_Sanford_Pdks')[0]

name_fld_idx = pdk_lyr.fields().lookupField('LABEL')

atts_map = {}

count = 1

for ft in pdk_lyr.getFeatures():
    if ft['LABEL'] == NULL:
        atts_map[ft.id()] = {name_fld_idx: f'NO NAME {count}'}
        count+=1
        
pdk_lyr.dataProvider().changeAttributeValues(atts_map)