src_layer = iface.activeLayer()
target_layer = QgsProject.instance().mapLayersByName('MGP_Transport_Lines')[0]

src_feats = src_layer.selectedFeatures()

if not src_feats:
    print('No Features Selected!')
else:
    src_geom = src_feats[0].geometry()

feat_ids = [ft.id() for ft in target_layer.getFeatures()]

fid = None

if not feat_ids:
    fid = 1
    
else:
    fid = max(feat_ids) + 1
    
if src_layer.name() == 'MGP_Roads':
    track_type = 'Road'
elif src_layer.name() == 'MGP_Vehicle_tracks':
    track_type = 'Vehicle track'

new_feat = QgsFeature(target_layer.fields())

if fid and src_geom:
    new_feat.setGeometry(src_geom)
    new_feat.setAttributes([fid, fid, track_type, 'Mulga Park', 'MGP'])
    target_layer.dataProvider().addFeatures([new_feat])
    target_layer.updateExtents()
    target_layer.triggerRepaint()

