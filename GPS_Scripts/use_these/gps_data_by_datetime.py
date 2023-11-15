from datetime import datetime
#import os

#print(datetime(2020,8,30,23,59,59))
#print(iface.activeLayer().source())
project = QgsProject.instance()

gps_merged_lyr_uri = r'C:/Users/qw2/Desktop/Paddock_Power_GPS/ALL_GPS_DATA_MERGED/all_with_distances.gpkg|layername=all_with_distances'
gps_merged_lyr = QgsVectorLayer(gps_merged_lyr_uri, 'all_with_distances', 'ogr')

single_day_layer = QgsVectorLayer('Point?crs=epsg:4326', 'March_2022', 'memory')
flds = gps_merged_lyr.fields()
single_day_layer.dataProvider().addAttributes(flds)
single_day_layer.updateFields()

start_dt = datetime(2022,3,1,00,00,00)
end_dt = datetime(2022,3,31,23,59,59)

single_day_feats = []

for ft in gps_merged_lyr.getFeatures():
    ft_qdt = ft['DateTime']
    ft_py_date = ft_qdt.toPyDateTime()
    if ft_py_date > start_dt and ft_py_date < end_dt:
        new_feat = QgsFeature(single_day_layer.fields())
        new_feat.setGeometry(ft.geometry())
        new_feat.setAttributes(ft.attributes())
        single_day_feats.append(new_feat)

single_day_layer.dataProvider().addFeatures(single_day_feats)

print('Done')

if single_day_layer.isValid():
    project.addMapLayer(single_day_layer)
    