project = QgsProject.instance()

lyr = project.mapLayersByName('Reprojected')[0]

ft = [f for f in lyr.getFeatures()][0]

#print(ft)

geom = ft.geometry()

da = QgsDistanceArea()
da.setSourceCrs(lyr.sourceCrs(), project.transformContext())
da.setEllipsoid(lyr.sourceCrs().ellipsoidAcronym())

print(da.measureArea(geom))
print(geom.area())
