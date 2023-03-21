project = QgsProject.instance()

src_crs = QgsCoordinateReferenceSystem('epsg:28352')

#dest_crs = QgsCoordinateReferenceSystem('epsg:9473')
#dest_crs = QgsCoordinateReferenceSystem('epsg:28352')
dest_crs = QgsCoordinateReferenceSystem('epsg:4283')

pdk_lyr = project.mapLayersByName('Mt_Sanford_Paddocks')[0]

temp_lyr = QgsVectorLayer(f'Polygon?crs={dest_crs.authid()}&field=fid:integer', 'All paddocks', 'memory')

geom = QgsGeometry.unaryUnion([f.geometry() for f in pdk_lyr.getFeatures()])
print(f'Original: {geom}')


def transformedGeom(g, orig_crs, target_crs, transform_context):
    print(orig_crs)
    print(target_crs)
    geom = QgsGeometry().fromWkt(g.asWkt())
    if orig_crs != target_crs:
        print('Ping')
        xform = QgsCoordinateTransform(orig_crs, target_crs, transform_context)
        geom.transform(xform)
    return geom


gda_geom = transformedGeom(geom, src_crs, dest_crs, project).makeValid()
print(f'Transformed: {gda_geom}')
print(f'Original: {geom}')
ft = QgsFeature()
ft.setGeometry(gda_geom)
ft.setAttributes([1])
temp_lyr.dataProvider().addFeatures([ft])
project.addMapLayers([temp_lyr])