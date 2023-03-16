import datetime

# TODO: Run iterating over all gps layers in project
project = QgsProject.instance()
lyr = project.mapLayersByName('0307_DL20220308_filled')[0]

to_delete = []

for f in lyr.getFeatures():
#    print(f.attributes())
    d = f['date_time'].toPyDateTime().date()
    begin_date = datetime.date(2021,10,31)
    end_date = datetime.date(2021,11,9)
    if d < begin_date or d > end_date:
        to_delete.append(f.id())
        
lyr.dataProvider().deleteFeatures(to_delete)