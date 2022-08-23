photo_lyr = QgsProject.instance().mapLayersByName('photos')[0]

sites = []

site_dic = {}

for f in photo_lyr.getFeatures():
    if not '(' in f['filename']:
        sites.append(f['filename'])

for site in sites:
#    print(site)
    site_photos = []
    for f in photo_lyr.getFeatures():
        if f['filename'] == site:
            site_photos.insert(0, f'{site}.jpg')
        elif f['filename'].split('(')[0].rstrip() == site:
            if len(f['filename'].split('(')) > 1:
                site_photos.append(f"{site} ({f['filename'].split('(')[1]}.jpg")
#    print(site_photos)
    site_dic[site]=site_photos

num_images = max([len(v) for k, v in site_dic.items()])
#print(num_images)
    
site_lyr = QgsVectorLayer('PointZ?crs=epsg:4326', 'test_lyr', 'memory')

site_lyr.dataProvider().addAttributes([QgsField('site_name', QVariant.String)])
site_lyr.dataProvider().addAttributes([QgsField(f'photo_{i}', QVariant.String) for i in range(1, num_images+1)])
site_lyr.dataProvider().addAttributes([QgsField(f'photo_{i}_rot', QVariant.Int) for i in range(1, num_images+1)])
site_lyr.dataProvider().addAttributes([
    QgsField('altitude', QVariant.Double),
    QgsField('timestamp', QVariant.DateTime)
])

site_lyr.updateFields()

QgsProject.instance().addMapLayer(site_lyr)

for k, v in site_dic.items():
    site_feats = [f for f in photo_lyr.getFeatures() if f['photo'].split('/')[-1] in v]
#    print(k, site_feats)
    feat = QgsFeature()
    atts = []
    atts.append(k)
    feat.setGeometry(site_feats[0].geometry())
    photo_atts = [NULL for i in range(num_images)]
    for index, current in enumerate(v):
        photo_atts[index]=current
    for i in photo_atts:
        atts.append(i)
    photo_rot = [NULL for i in range(num_images)]
    for index, current in enumerate(site_feats):
        photo_rot[index]=current['rotation']
    for j in photo_rot:
        atts.append(j)
    atts.append(site_feats[0]['altitude'])
    atts.append(site_feats[0]['timestamp'])
#    print(atts)
    feat.setAttributes(atts)
    site_lyr.dataProvider().addFeature(feat)
    site_lyr.updateFeature(feat)

    
