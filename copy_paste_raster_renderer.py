
r = iface.activeLayer().renderer().clone()

target_layers = [l for l in QgsProject.instance().mapLayers().values() if l.providerType() == 'gdal'
                and l.name() != source_lyr.name()]

for lyr in target_layers:
    lyr.setRenderer(r)
    iface.layerTreeView().refreshLayerSymbology(lyr.id())
    lyr.triggerRepaint()