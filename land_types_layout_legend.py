
layer = QgsProject.instance().mapLayersByName('OMP_Land_Types')[0]

labels = sorted([f'{ft["LAND_TYPE"]}\n{round(ft.geometry().area()/1000000, 2)} km²' for ft in layer.getFeatures()])

#for label in labels:
#    print(label)


layout = QgsProject.instance().layoutManager().layoutByName('OMP_RMC')
legend = [i for i in layout.items() if isinstance(i, QgsLayoutItemLegend)][0]
model = legend.model()
layer_tree = model.rootGroup()
lyr_tree_lyr = layer_tree.findLayer(layer.id())
legend.setAutoUpdateModel(False)
nodes = model.layerLegendNodes(lyr_tree_lyr)
#print(len(nodes))#25
for i, current in enumerate(nodes):
    QgsMapLayerLegendUtils.setLegendNodeUserLabel(lyr_tree_lyr, i, labels[i])
model.refreshLayerLegend(lyr_tree_lyr)
