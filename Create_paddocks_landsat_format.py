
# Create a new temporary layer and add fields
project = QgsProject.instance()
new_flds = [QgsField('padd_num', QVariant.Int), QgsField('padd_name', QVariant.String), QgsField('area_km2', QVariant.Double, len=10, prec=6)]
new_lyr = QgsVectorLayer(f'Polygon?crs={project.crs().authid()}', 'paddocks', 'memory')
new_lyr.dataProvider().addAttributes(new_flds)
new_lyr.updateFields()

paddock_lyr = iface.activeLayer()

new_geoms = {}
geoms_to_collect = [f.geometry() for f in paddock_lyr.selectedFeatures()]
#print(geoms_to_collect)
dissolved_geom = QgsGeometry().collectGeometry(geoms_to_collect)
new_geoms['North Queens All Paddocks']=(dissolved_geom.combine(dissolved_geom))
for f in [f for f in paddock_lyr.getFeatures() if f.id() not in [f.id() for f in paddock_lyr.selectedFeatures()]]:
    new_geoms[f['PckName']]=f.geometry()
#print(new_geoms)
pnum = 1
for k, v in new_geoms.items():
    fet = QgsFeature()
    fet.setGeometry(v)
    fet.setAttributes([pnum, k, v.area()/1000000])
    new_lyr.dataProvider().addFeatures([fet])
    pnum+=1

# Add layer to project
if new_lyr.isValid():
    project.addMapLayer(new_lyr)
else:
    print('Layer not valid')


