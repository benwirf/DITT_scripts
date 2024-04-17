
project = QgsProject.instance()

boundary_lyr = project.mapLayersByName('Station_Boundaries')[0]

#print([fld.name() for fld in boundary_lyr.fields()])

out_flds = ['fid', 'DISTRICT', 'NAME', 'AREA_KM2']

rocklands_bdry_lyr = project.mapLayersByName('rocklands_boundary')[0]

fts_to_add = []

fid = max([ft['fid'] for ft in boundary_lyr.getFeatures()])+1

for ft in rocklands_bdry_lyr.getFeatures():
    district = 'Barkly'
    feat = QgsFeature(boundary_lyr.fields())
    feat.setGeometry(ft.geometry())
    feat.setAttributes([fid,
                        district,
                        'Rocklands',
                        round(ft.geometry().area()/1000000, 3)])
    fts_to_add.append(feat)
    fid+=1
    
boundary_lyr.dataProvider().addFeatures(fts_to_add)

boundary_lyr.updateExtents()

boundary_lyr.triggerRepaint()

print('Done')