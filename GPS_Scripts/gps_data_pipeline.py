'''
Raw CSVs need unnecessary columns removed and rows with 0 lat/long values deleted
to successfully import into QGIS. They must then be converted to gpkg for editing.
***The task above is implemented in batch_raw_csv_to_gpkg.py***
At this point, features within the desired time period can be selected
(with some time buffer [1 day?]) and re-exported. Then run workfow in script below
to add and fill QDateTime field, spatially and temporally interpolate gaps in data
at 1 minute increments, and delete features outside of the desired time period.
'''

from datetime import datetime
import os

project = QgsProject.instance()
gps_lyrs = [l for l in project.mapLayers().values() if 'Big_Mudgee' in l.name()]
#print(gps_lyrs)

dt_fld = QgsField('date_time', QVariant.DateTime)

flds_to_add = [QgsField('ID', QVariant.Int),
                QgsField('gpx_index', QVariant.Int),
                QgsField('Distance', QVariant.Double, len=10, prec=3),
                QgsField('Latitude', QVariant.Double, len=8, prec=6),
                QgsField('Longitude', QVariant.Double, len=9, prec=6),
                QgsField('date_time', QVariant.DateTime, len=9, prec=6),
                QgsField('Azimuth', QVariant.Int)]

for lyr in gps_lyrs:
    # Add and fill the date time field
    print(f'Creating datetime field for layer: {lyr.name()}')
    lyr.dataProvider().addAttributes([dt_fld])
    lyr.updateFields()
    fld_idx = lyr.fields().lookupField('date_time')
    atts = {}
    for ft in lyr.getFeatures():
        d = ft['Date'].lstrip()
        t = ft['Time']
        dt_txt = f'{d}{t[:-2]}00'
        dt = datetime.strptime(dt_txt, '%Y/%m/%d %H:%M:%S')
        atts[ft.id()] = {fld_idx:QDateTime(dt)}
    lyr.dataProvider().changeAttributeValues(atts)
    
    # Interpolate gaps in data and add to an output memory layer
    print(f'Interpolating gaps for layer: {lyr.name()}')
    dest_lyr = QgsVectorLayer('Point?epsg:4326', '', 'memory')
    dest_lyr.dataProvider().addAttributes(flds_to_add)
    dest_lyr.updateFields()

    da = QgsDistanceArea()
    da.setSourceCrs(dest_lyr.sourceCrs(), project.transformContext())
    da.setEllipsoid(dest_lyr.sourceCrs().ellipsoidAcronym())

    if not dest_lyr.isValid():
        print('Destination layer is not valid!')

    fid = 1

    for f in lyr.getFeatures():
        next_ft = lyr.getFeature(f.id()+1)
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
                
    # Select features within desired time period and run extract selected features
    # to get permanent output layers...
    out_folder = 'Paddock_Power_GPS\\GPS Data Aug21-March22\\gps_layers_final'
    out_lyr = f'{}.gpkg'
    out_path = os.path.join(out_folder, out_lyr)
    save_selected_params = {'INPUT':dest_lyr,
                            'OUTPUT':out_path}
    processing.run("native:saveselectedfeatures", save_selected_params)
    
