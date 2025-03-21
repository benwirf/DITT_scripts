import os

out_dir = '\\gpkg\\paths'

for lyr in QgsProject.instance().mapLayers().values():
    if lyr.type() == QgsMapLayerType.VectorLayer:
        if lyr.geometryType() == QgsWkbTypes.PointGeometry:
            out_file = os.path.join(out_dir, f'{lyr.name()}.gpkg')
            params = {'INPUT':lyr,
                'CLOSE_PATH':False,
                'ORDER_EXPRESSION':'',
                'NATURAL_SORT':False,
                'GROUP_EXPRESSION':'',
                'OUTPUT':out_file}
            processing.run("native:pointstopath", params)
                
print('Done')


