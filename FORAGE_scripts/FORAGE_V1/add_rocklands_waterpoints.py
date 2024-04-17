
project = QgsProject.instance()

# Existing layers found in backup_gpkgs folder
waterpoints_lyr = project.mapLayersByName('Waterpoints')[0]

#print([fld.name() for fld in waterpoints_lyr.fields()])

out_flds = ['fid', 'FEATURE', 'NAME', 'DISTRICT', 'PROPERTY']

rocklands_wpt_lyr = project.mapLayersByName('rocklands_waterpoints')[0]

fts_to_add = []

fid = max([ft['fid'] for ft in waterpoints_lyr.getFeatures()])+1

for ft in rocklands_wpt_lyr.getFeatures():
    district = 'Barkly'
    feat = QgsFeature(waterpoints_lyr.fields())
    feat.setGeometry(ft.geometry())
    feat.setAttributes([fid,
                        ft['Type'],
                        ft['Name'],
                        district,
                        'Rocklands'])
    fts_to_add.append(feat)
    fid+=1
    
waterpoints_lyr.dataProvider().addFeatures(fts_to_add)

waterpoints_lyr.updateExtents()

waterpoints_lyr.triggerRepaint()

print('Done')
