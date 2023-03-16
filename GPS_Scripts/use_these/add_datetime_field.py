from datetime import datetime

project = QgsProject.instance()
#lyr = project.mapLayersByName('Big_Mudgee_0307_DL20220308')[0]
gps_lyrs = [l for l in project.mapLayers().values() if 'BigMudgee' in l.name()]

dt_fld = QgsField('date_time', QVariant.DateTime)

for lyr in gps_lyrs:
    print(f'Adding datetime field to {lyr.name()}')
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

print('Done!')