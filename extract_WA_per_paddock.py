paddock_layer_name = 'Mulga_Park_Pdks'
waterpoint_layer_name = 'Pdk_Water'

paddock_layer = QgsProject.instance().mapLayersByName(paddock_layer_name)[0]

waterpoint_layer = QgsProject.instance().mapLayersByName(waterpoint_layer_name)[0]

# Create a temporary layer to hold watered area features
crs = waterpoint_layer.crs().authid()
wa_5km_lyr = QgsVectorLayer(f'Polygon?crs={crs}', '5km_WA', 'memory')
wa_5km_lyr.dataProvider().addAttributes([QgsField('property', QVariant.String),
                                        QgsField('padd_num', QVariant.Int),
                                        QgsField('padd_name', QVariant.String),
                                        QgsField('area_km2', QVariant.Double, len=10, prec=5)])
wa_5km_lyr.updateFields()

for i, p in enumerate(paddock_layer.getFeatures()):
    wpts = [pt for pt in waterpoint_layer.getFeatures() if pt.geometry().within(p.geometry())]
    buffers = [wpt.geometry().buffer(5000, 25) for wpt in wpts]
    dissolved_buff = QgsGeometry.unaryUnion(buffers)
    clipped_buff = dissolved_buff.intersection(p.geometry())
    ft = QgsFeature(wa_5km_lyr.fields())
    ft.setGeometry(clipped_buff)
    ft.setAttributes(['Mulga Park', i+1, p['PADDOCK'], round(clipped_buff.area()/1000000, 5)])
    wa_5km_lyr.dataProvider().addFeatures([ft])
    
QgsProject.instance().addMapLayer(wa_5km_lyr)
