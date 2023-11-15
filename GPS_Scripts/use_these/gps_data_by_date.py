from datetime import date
#import os

#print(date(2022,10,29))

project = QgsProject.instance()

gps_data_lyr = project.mapLayersByName('Wet_Season_Control')[0]

week_gps_layer = QgsVectorLayer(f'Point?crs={gps_data_lyr.crs().authid()}', 'Week_Before_Rain', 'memory')
flds = gps_data_lyr.fields()
week_gps_layer.dataProvider().addAttributes(flds)
week_gps_layer.updateFields()

start_date = date(2022,12,17)
end_date = date(2022,12,23)

week_feats = []

for ft in gps_data_lyr.getFeatures():
    ft_qd = ft['Date']
    ft_py_date = ft_qd.toPyDate()
    if ft_py_date >= start_date and ft_py_date <= end_date:
        new_feat = QgsFeature(week_gps_layer.fields())
        new_feat.setGeometry(ft.geometry())
        new_feat.setAttributes(ft.attributes())
        week_feats.append(new_feat)

week_gps_layer.dataProvider().addFeatures(week_feats)

print('Done')

if week_gps_layer.isValid():
    project.addMapLayer(week_gps_layer)
