
point_lyr = QgsVectorLayer('Polygon?crs=epsg:4326', 'polygons', 'memory')

point_lyr.dataProvider().addAttributes([QgsField('ID', QVariant.Int), QgsField('NAME', QVariant.String)])

point_lyr.updateFields()

for i, layer in enumerate(QgsProject.instance().mapLayers().values()):
    if layer.type() == QgsMapLayerType.VectorLayer:
        if layer.geometryType() == 2:
            lyr_name = layer.name().split('—')[0].rstrip(' ')
            kmz_feat = [f for f in layer.getFeatures()][0]
            new_feat = QgsFeature()
            new_feat.setGeometry(kmz_feat.geometry())
            new_feat.setAttributes([i, lyr_name])
            point_lyr.dataProvider().addFeature(new_feat)
            point_lyr.updateFeature(new_feat)
            
QgsProject.instance().addMapLayer(point_lyr)

