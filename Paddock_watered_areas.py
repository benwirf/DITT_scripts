import os

paddock_layer_name = 'Mt_Sanford_Paddocks'
waterpoint_layer_name = 'Mt_Sanford_Waterpoints'

paddock_name_field = 'PDK_NAME'

paddock_layer = QgsProject.instance().mapLayersByName(paddock_layer_name)[0]

waterpoint_layer = QgsProject.instance().mapLayersByName(waterpoint_layer_name)[0]

# Create a temporary layer to hold watered area features
wkb = QgsWkbTypes.displayString(waterpoint_layer.wkbType())
crs = waterpoint_layer.crs().authid()
wa_3km_lyr = QgsVectorLayer(f'Polygon?crs={crs}', '3km_WA', 'memory')
wa_3km_lyr.dataProvider().addAttributes([QgsField('PDK_NAME', QVariant.String)])
wa_3km_lyr.updateFields()


for paddock in paddock_layer.getFeatures():
    # Simple spatial query to retrieve water points within each paddock
    waterpoint_feats = [f for f in waterpoint_layer.getFeatures() if f.geometry().intersects(paddock.geometry())]
    wa_feat = QgsFeature()
    geom = QgsGeometry.collectGeometry([f.geometry() for f in waterpoint_feats])
    buff_geom = geom.buffer(3000.0, 25)
    pad_wa = buff_geom.intersection(paddock.geometry())
#    print(pad_wa)
    wa_feat.setGeometry(pad_wa)
    wa_feat.setAttributes([paddock[paddock_name_field]])
    res = wa_3km_lyr.dataProvider().addFeatures([wa_feat])
#    print(res)
    
QgsProject.instance().addMapLayer(wa_3km_lyr)
