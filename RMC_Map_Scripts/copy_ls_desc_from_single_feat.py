lyr = QgsProject.instance().mapLayersByName('Willeroo_Land_Systems')[0]
fld_idx = lyr.fields().lookupField('DESC')

src_lyr = QgsProject.instance().mapLayersByName('Newry_Land_Systems')[0]

atts = {}

for ft in lyr.getFeatures():
    if ft['LANDSYSTEM'] != 'Pinkerton':
        continue
    src_feats = [feat for feat in src_lyr.getFeatures() if feat['LANDSYSTEM'] == 'Pinkerton']
    if not src_feats:
        continue
    src_feat = src_feats[0]
    desc = src_feat['SIMPLE_DESC']
    atts[ft.id()] = {fld_idx: desc}
    
lyr.dataProvider().changeAttributeValues(atts)

print('Done')