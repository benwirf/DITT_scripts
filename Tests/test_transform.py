project = QgsProject.instance()

#pt_lyr = project.mapLayersByName('point')[0]# 4326
poly_lyr = project.mapLayersByName('poly')[0]# 28352

pt_lyr = project.mapLayersByName('Mulga_Park_waterpoints')[0]# 4326
#poly_lyr = project.mapLayersByName('Paddocks_UTM')[0]# 28352

def transformed(g):
    xform = QgsCoordinateTransform(pt_lyr.sourceCrs(), poly_lyr.sourceCrs(), project.transformContext())
    g.transform(xform)
    return g

#for pt in pt_lyr.getFeatures():
#    print(transformed(pt.geometry()))
    
for p in poly_lyr.getFeatures():
#    print(p.geometry())
#    pad_name = p['LABEL']
#    print(pad_name)
#    print(p.geometry())
    wpts = [f for f in pt_lyr.getFeatures() if transformed(f.geometry()).within(p.geometry())]
    print(wpts)
    print('--------------')