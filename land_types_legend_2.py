
layer = QgsProject.instance().mapLayersByName('Huckitta_Land_Systems_250')[0]

labels = []

#labels = sorted([f'{ft["LAND_TYPE"]}\n{round(ft.geometry().area()/1000000, 2)} km²' for ft in layer.getFeatures()])
total_area = 2101.68# km2

pcnts = []

for ft in layer.getFeatures():
    land_type = ft['LandSystem']
    if ft['LSDesc'] == NULL:
        desc = ''
    else:
        desc = ft['LSDesc']
    area = round(ft.geometry().area()/1000000, 2)
    pcnt = round((area/total_area)*100, 1)
    pcnts.append(pcnt)
    label = f'{land_type}- {area} km² ({pcnt}%)\n{desc}'
    #label = f'{land_type}- {desc}\n{area} km² ({pcnt}%)'
    labels.append(label)

for label in labels:
    print(label)
print(sum(pcnts))


'''
sorted_labels = sorted(labels)
print(sorted_labels)


layout = QgsProject.instance().layoutManager().layoutByName('Huckitta_RMC')
legend = [i for i in layout.items() if isinstance(i, QgsLayoutItemLegend)][0]
model = legend.model()
layer_tree = model.rootGroup()
lyr_tree_lyr = layer_tree.findLayer(layer.id())
legend.setAutoUpdateModel(False)
nodes = model.layerLegendNodes(lyr_tree_lyr)
#print(len(nodes))#25
for i, current in enumerate(nodes):
    QgsMapLayerLegendUtils.setLegendNodeUserLabel(lyr_tree_lyr, i, sorted_labels[i])
model.refreshLayerLegend(lyr_tree_lyr)
'''