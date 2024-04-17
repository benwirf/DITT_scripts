project = QgsProject.instance()
tgt_lyr = project.mapLayersByName('Birrindudu_Land_Systems')[0]
src_lyr = project.mapLayersByName('Inverway_Land_Systems')[0]
fld1 = 'SIMPLE_DESC'
fld2 = 'VEG_DESC'
fld1_idx = tgt_lyr.fields().lookupField(fld1)
fld2_idx = tgt_lyr.fields().lookupField(fld2)
atts_map = {}
for feat in tgt_lyr.getFeatures():
    match_feats = [ft for ft in src_lyr.getFeatures() if ft['LANDSYSTEM'] == feat['LANDSYSTEM']]
    if not match_feats:
        continue
    fld1_att = match_feats[0][fld1]
    fld2_att = match_feats[0][fld2]
    atts_map[feat.id()] = {fld1_idx: fld1_att, fld2_idx: fld2_att}
    
tgt_lyr.dataProvider().changeAttributeValues(atts_map)