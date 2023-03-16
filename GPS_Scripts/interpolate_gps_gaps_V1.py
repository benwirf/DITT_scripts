import datetime

project = QgsProject.instance()
src_lyr = project.mapLayersByName('test_points_raw')[0]

dest_lyr = QgsVectorLayer('Point?epsg:4326', 'test_layer', 'memory')

dest_lyr.dataProvider().addAttributes(src_lyr.fields())

dest_lyr.updateFields()

if not dest_lyr.isValid():
    print('Destination layer is not valid!')

for f in src_lyr.getFeatures():
    # first add current existing feature
    existing_feat = QgsFeature(dest_lyr.fields())
    existing_feat.setGeometry(f.geometry())
    existing_feat.setAttributes(f.attributes())
    dest_lyr.dataProvider().addFeature(existing_feat)
    next_ft = src_lyr.getFeature(f.id()+1)
#    print(next_ft.id())
    if next_ft.id()>0:
        current_dt = f['date_time'].toPyDateTime()
        next_dt = next_ft['date_time'].toPyDateTime()
        t_delta = next_dt-current_dt# timedelta object
        t_delta_as_int = int(t_delta.seconds/60)
        no_of_feats_to_add = t_delta_as_int-1
#        print(no_of_feats_to_add)
        if not no_of_feats_to_add:
            continue
        line_to_interp = QgsGeometry.fromPolyline([QgsPoint(f.geometry().asPoint()), QgsPoint(next_ft.geometry().asPoint())])
#        print(line_to_interp.length())
        interp_dist = line_to_interp.length()/(no_of_feats_to_add+1)
        for i in range(no_of_feats_to_add):
            dist = interp_dist*(i+1)
            time_delta = datetime.timedelta(minutes=i+1)
            new_geom = line_to_interp.interpolate(dist)
            new_dt = current_dt+time_delta
            new_feat = QgsFeature(dest_lyr.fields())
            new_feat.setGeometry(new_geom)
            new_feat['date_time'] = QDateTime(new_dt)
            dest_lyr.dataProvider().addFeature(new_feat)
            dest_lyr.updateFeature(new_feat)
            
project.addMapLayer(dest_lyr)