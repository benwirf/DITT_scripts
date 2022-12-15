root = QgsProject.instance().layerTreeRoot()
#print([c.name() for c in root.children()])
ltl = [c for c in root.children() if c.name() == 'Broadmere_Land_Systems'][0]
ltm = iface.layerTreeView().layerTreeModel()
legend_nodes = ltm.layerLegendNodes(ltl)
for n in legend_nodes:
    print(n.userLabel())