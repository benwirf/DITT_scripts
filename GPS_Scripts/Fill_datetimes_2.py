import datetime

lyr = QgsProject.instance().mapLayersByName('All_Points')[0]

dt = datetime.datetime(2022, 6, 9, 14, 56, 0)

dt_idx = lyr.fields().lookupField('Date_Time')

att_map = {}

for f in lyr.getFeatures():
    dt = dt + datetime.timedelta(seconds=10)
    att_map[f.id()] = {dt_idx: QDateTime(dt)}
    
lyr.dataProvider().changeAttributeValues(att_map)