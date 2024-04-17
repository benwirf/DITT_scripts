lyr = QgsProject.instance().mapLayersByName('VRD_Land_Systems')[0]
fld_idx = lyr.fields().lookupField('DESC')

src_lyr = QgsProject.instance().mapLayersByName('Pigeon_Hole_Land_Systems')[0]

atts = {}

for ft in lyr.getFeatures():
    src_feats = [feat for feat in src_lyr.getFeatures() if feat['LANDSYSTEM'] == ft['LANDSYSTEM']]
    if not src_feats:
        continue
    src_feat = src_feats[0]
    desc = src_feat['DESC']
    atts[ft.id()] = {fld_idx: desc}
    
lyr.dataProvider().changeAttributeValues(atts)

print('Done')