project = QgsProject.instance()

pdk_lyr = project.mapLayersByName('Mt_Sanford_Paddocks')[0]

geom = QgsGeometry.unaryUnion([f.geometry() for f in pdk_lyr.getFeatures()])

print(QgsGeometry(geom.constGet()))