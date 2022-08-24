'''
Set legend custom node labels in layout for a categorized layer.
E.g. land systems labelled with name and area.
'''

layer = QgsProject.instance().mapLayersByName('Broadmere_Land_Systems')[0]

labels = sorted([f'{f["LANDSYSTEM"]}- {round(f["AREA_KM2"], 1)} km²' for f in layer.getFeatures()])

final_labels = []

for lbl in labels:
    map_unit = [f['MAPUNIT'] for f in layer.getFeatures() if f['LANDSYSTEM'] == lbl.split('-')[0]][0]
    new_lbl = f'{map_unit}, {lbl}'
    final_labels.append(new_lbl)

#print(labels)
#print('##############')
#print(final_labels)


layout = QgsProject.instance().layoutManager().layoutByName('Broadmere_LS')
#print(layout)
legend = [i for i in layout.items() if isinstance(i, QgsLayoutItemLegend)][0]
#print(legend)
model = legend.model()
#print(model)
layer_tree = model.rootGroup()
#print(layer_tree)
lyr_tree_lyr = layer_tree.findLayer(layer.id())
#lyr_tree_lyr = [c for c in layer_tree.children() if c.name() == 'Broadmere_Land_Systems'][0]
#print(lyr_tree_lyr)
legend.setAutoUpdateModel(False)
nodes = model.layerLegendNodes(lyr_tree_lyr)
#print(len(nodes))#25
for i, current in enumerate(nodes):
#    print(i, current.data(2))
    QgsMapLayerLegendUtils.setLegendNodeUserLabel(lyr_tree_lyr, i, final_labels[i])
model.refreshLayerLegend(lyr_tree_lyr)
