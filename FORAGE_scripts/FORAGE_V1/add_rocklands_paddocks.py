
project = QgsProject.instance()

# Existing layers found in backup_gpkgs folder
paddocks_lyr = project.mapLayersByName('Paddock_Boundaries')[0]

#print([fld.name() for fld in paddocks_lyr.fields()])

out_flds = ['fid', 'NAME', 'DISTRICT', 'PROPERTY', 'AREA_KM2']

rocklands_pdk_lyr = project.mapLayersByName('rocklands_paddocks')[0]

fts_to_add = []

fid = max([ft['fid'] for ft in paddocks_lyr.getFeatures()])+1

for ft in rocklands_pdk_lyr.getFeatures():
    district = 'Barkly'
    pdk_area = ft.geometry().area()
    if pdk_area > 1000000:
        feat = QgsFeature(paddocks_lyr.fields())
        feat.setGeometry(ft.geometry())
        feat.setAttributes([fid,
                            ft['Name'],
                            district,
                            'Rocklands',
                            round(pdk_area/1000000, 3)])
        fts_to_add.append(feat)
        fid+=1
    
paddocks_lyr.dataProvider().addFeatures(fts_to_add)

paddocks_lyr.updateExtents()

paddocks_lyr.triggerRepaint()

print('Done')
