'''
This script fills gaps in gps tracking collar point layers,
carrying out spatial and temporal interpolation between existing
points where a gap (more than 1 minute time delta) is detected.
'''

import datetime

# TODO: Run iterating over all gps layers in project
project = QgsProject.instance()
src_lyr = project.mapLayersByName('test_points_raw')[0]

flds_to_add = [QgsField('ID', QVariant.Int),
                QgsField('gpx_index', QVariant.Int),
                QgsField('Distance', QVariant.Double, len=10, prec=3),
                QgsField('Latitude', QVariant.Double, len=8, prec=6),
                QgsField('Longitude', QVariant.Double, len=9, prec=6),
                QgsField('date_time', QVariant.DateTime, len=9, prec=6),
                QgsField('Azimuth', QVariant.Int)]

dest_lyr = QgsVectorLayer('Point?epsg:4326', 'gps_points_interpolated', 'memory')

dest_lyr.dataProvider().addAttributes(flds_to_add)

dest_lyr.updateFields()

da = QgsDistanceArea()
da.setSourceCrs(dest_lyr.sourceCrs(), project.transformContext())
da.setEllipsoid(dest_lyr.sourceCrs().ellipsoidAcronym())

if not dest_lyr.isValid():
    print('Destination layer is not valid!')

fid = 1

for f in src_lyr.getFeatures():
    next_ft = src_lyr.getFeature(f.id()+1)
    # check for final feature (will return some large negative integer)
    if next_ft.id()>0:
        current_dt = f['date_time'].toPyDateTime()
        next_dt = next_ft['date_time'].toPyDateTime()
        t_delta = next_dt-current_dt# timedelta object
        t_delta_as_int = int(t_delta.seconds/60)
        az = f.geometry().asPoint().azimuth(next_ft.geometry().asPoint())
        no_of_feats_to_add = t_delta_as_int-1
        # first add current existing feature
        existing_feat = QgsFeature(dest_lyr.fields())
        existing_feat.setGeometry(f.geometry())
        atts = [fid, f['Index'], f['Distance'], f['Latitude'], f['Longitude'], f['date_time'], az]
        existing_feat.setAttributes(atts)
        dest_lyr.dataProvider().addFeature(existing_feat)
        fid+=1
        # skip if datetime stamps are one minute apart (no gap to fill)
        if not no_of_feats_to_add:
            continue
        # create a line geometry from current to next feature
        line_to_interp = QgsGeometry.fromPolyline([QgsPoint(f.geometry().asPoint()), QgsPoint(next_ft.geometry().asPoint())])
        interp_dist = line_to_interp.length()/(no_of_feats_to_add+1)
        dist_meters = da.measureLength(line_to_interp)/(no_of_feats_to_add+1)
        
        for i in range(no_of_feats_to_add):
            dist = interp_dist*(i+1)
            time_delta = datetime.timedelta(minutes=i+1)
            new_geom = line_to_interp.interpolate(dist)
            new_dt = current_dt+time_delta
            new_feat = QgsFeature(dest_lyr.fields())
            new_feat.setGeometry(new_geom)
            new_atts = [fid, f['Index']+(i+1), dist_meters, new_geom.asPoint().y(), new_geom.asPoint().x(), QDateTime(new_dt), az]
            new_feat.setAttributes(new_atts)
            dest_lyr.dataProvider().addFeature(new_feat)
            # increment variables
            fid+=1
            
project.addMapLayer(dest_lyr)
