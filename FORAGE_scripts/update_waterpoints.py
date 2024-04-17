project = QgsProject.instance()

output_lyr = QgsVectorLayer('Point?crs=epsg:7845', 'forage_waters', 'memory')

orig_lyr = project.mapLayersByName('Forage_Waterpoints')[0]

kidman_lyr = project.mapLayersByName('Kidman_Waters')[0]

#fld_names = [fld.name() for fld in orig_lyr.fields()][1:]

flds_to_add = [fld for fld in orig_lyr.fields()][1:]

output_lyr.dataProvider().addAttributes(flds_to_add)

output_lyr.updateFields()

out_feats = []

for ft in kidman_lyr.getFeatures():
    feat = QgsFeature(output_lyr.fields())
    feat.setGeometry(ft.geometry())
    feat.setAttributes([att for att in ft.attributes()][1:])
    out_feats.append(feat)
    
for ft in orig_lyr.getFeatures():
    if ft['PROPERTY'] == 'Kidman':
        continue
    feat = QgsFeature(output_lyr.fields())
    feat.setGeometry(ft.geometry())
    feat.setAttributes([att for att in ft.attributes()][1:])
    out_feats.append(feat)
    
output_lyr.dataProvider().addFeatures(out_feats)
output_lyr.updateExtents()

project.addMapLayer(output_lyr)
