import datetime

lyr = QgsProject.instance().mapLayersByName('Joined layer')[0]

dt = datetime.datetime(2022, 6, 9, 14, 56, 0)

dt_idx = lyr.fields().lookupField('Date_Time')

att_map = {}

for i in range(lyr.featureCount()-1):
    dt = dt + datetime.timedelta(seconds=10)
    att_map[i] = {dt_idx: QDateTime(dt)}
    
lyr.dataProvider().changeAttributeValues(att_map)