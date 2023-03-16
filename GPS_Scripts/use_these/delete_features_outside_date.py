import datetime

# TODO: Run iterating over all gps layers in project
project = QgsProject.instance()

gps_lyrs = [l for l in project.mapLayers().values() if 'BigMudgee' in l.name()]

for lyr in gps_lyrs:
    to_delete = []
    for f in lyr.getFeatures():
#        print(f.attributes())
        date_string = f['Date']
        y = date_string.split('/')[0]
        m = date_string.split('/')[1]
        d = date_string.split('/')[2]
        full_date = datetime.date(int(y), int(m), int(d))
#        print(full_date)
        begin_date = datetime.date(2021, 10, 31)
        end_date = datetime.date(2021, 11, 9)
        if full_date < begin_date or full_date > end_date:
#            print('will be deleted')
            to_delete.append(f.id())
            
    lyr.dataProvider().deleteFeatures(to_delete)
    lyr.updateExtents()
    lyr.triggerRepaint()
    print(f'{lyr.name()} done')
    
iface.mapCanvas().refresh()
print('Finished!')