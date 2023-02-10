pt_lyr = QgsProject.instance().mapLayersByName('Mulga_Park_waterpoints')[0]# 4326
poly_lyr = QgsProject.instance().mapLayersByName('Paddocks_UTM')[0]# 28352

for paddock in poly_lyr.getFeatures():
    pad_name = paddock['LABEL']
    print(pad_name)
    wpts = [f for f in pt_lyr.getFeatures() if f.geometry().within(paddock.geometry())]
    print(wpts)
    print('--------------')