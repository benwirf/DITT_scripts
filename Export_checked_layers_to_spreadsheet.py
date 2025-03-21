project = QgsProject.instance()
root = project.layerTreeRoot()
#print(root)
lyrs = [l.layer() for l in root.findLayers() if l.isVisible()]
#print(lyrs)

params = {'LAYERS':lyrs,
            'USE_ALIAS':False,
            'FORMATTED_VALUES':False,
            'OUTPUT':'/Mulga_Park/For_xxx/Mulga_Park_RRR.xlsx',
            'OVERWRITE':False}

processing.run("native:exporttospreadsheet", params)

