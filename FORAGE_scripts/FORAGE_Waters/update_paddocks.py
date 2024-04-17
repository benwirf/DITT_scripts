project = QgsProject.instance()

pdk_lyr = project.mapLayersByName('Kidman_Paddocks')[0]

#Fields: ['fid', 'NAME', 'DISTRICT', 'PROPERTY', 'AREA_KM2']
#Added fields: ['NAME', 'DISTRICT', 'PROPERTY', 'AREA_KM2']

output_lyr = QgsVectorLayer('Polygon?crs=epsg:7845', 'Updated_paddocks', 'memory')
flds = QgsFields()
for fld in [fld for fld in pdk_lyr.fields()][1:]:
    flds.append(fld)
output_lyr.dataProvider().addAttributes(flds)
output_lyr.updateFields()

out_feats = []

for ft in pdk_lyr.getFeatures():
    if ft['NAME'] == 'Improved 1':
        orig_pdk_geoms_1 = [fat.geometry() for fat in pdk_lyr.getFeatures() if 'Improved' in fat['NAME']]
        #print(orig_pdk_geoms_1)
        new_geom = QgsGeometry.unaryUnion(orig_pdk_geoms_1)
        feat = QgsFeature(output_lyr.fields())
        feat.setGeometry(new_geom)
        feat.setAttributes(['Improved', 'VRD', 'Kidman', round(new_geom.area()/1000000, 5)])
        out_feats.append(feat)
    elif ft['NAME'] == 'Improved 2':
        continue
    elif ft['NAME'] == 'Little Rosewood West':
        #print([f for f in pdk_lyr.getFeatures() if 'Little Rosewood' in f['NAME']])
        orig_pdk_geoms_2 = [fet.geometry() for fet in pdk_lyr.getFeatures() if 'Little Rosewood' in fet['NAME']]
        #print(orig_pdk_geoms_2)
        new_geom = QgsGeometry.unaryUnion(orig_pdk_geoms_2)
        feat = QgsFeature(output_lyr.fields())
        feat.setGeometry(new_geom)
        feat.setAttributes(['Little Rosewood', 'VRD', 'Kidman', round(new_geom.area()/1000000, 5)])
        out_feats.append(feat)
    elif ft['NAME'] == 'Little Rosewood East':
        continue
    else:
        #just copy geom and atts from ft to feat...
        feat = QgsFeature(output_lyr.fields())
        feat.setGeometry(ft.geometry())
        atts = ft.attributes()
        feat.setAttributes([atts[1], atts[2], atts[3], atts[4]])
        out_feats.append(feat)
        
output_lyr.dataProvider().addFeatures(out_feats)
project.addMapLayer(output_lyr)
    
