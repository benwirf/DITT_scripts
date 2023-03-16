pdks = QgsProject.instance().mapLayersByName('Rocklands_paddocks')[0]
grassy_geom = [ft.geometry() for ft in pdks.getFeatures() if ft['Name'] == 'Grassy'][0]
for lyr in QgsProject.instance().mapLayers().values():
    if 'BigMudgee' in lyr.name():
        for f in lyr.getFeatures():
            if f.geometry().intersects(grassy_geom):
                lyr.dataProvider().deleteFeatures([f.id()])
        lyr.updateExtents()
Print('Done')