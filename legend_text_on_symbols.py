lyr = iface.activeLayer()
canvas = iface.mapCanvas()

# Retrieve the current symbol node text format
tree_view = iface.layerTreeView()
model = tree_view.layerTreeModel()
root = model.rootGroup()
ltl = root.findLayer(lyr)
nodes = model.layerLegendNodes(ltl)
text_format = nodes[0].textOnSymbolTextFormat()

content = {}
context = QgsRenderContext.fromMapSettings(canvas.mapSettings())
# Set your expression here
#expr = QgsExpression("LANDSYSTEM")
expr = QgsExpression("SURVEY_ID")
expr.prepare(context.expressionContext())

r = lyr.renderer().clone()

r.startRender(context, lyr.fields())

for f in lyr.getFeatures():
    context.expressionContext().setFeature(f)
    keys = set(r.legendKeysForFeature(f, context))
    for key in keys:
        if key in content:
            continue
        label = expr.evaluate(context.expressionContext())
        if label:
            content[key] = label

r.stopRender(context)

legend = QgsDefaultVectorLayerLegend(lyr)
legend.setTextOnSymbolEnabled(True)
legend.setTextOnSymbolContent(content)
legend.setTextOnSymbolTextFormat(text_format)
lyr.setLegend(legend)

#tree_view.resizeColumnToContents(1)
legend.itemsChanged.emit()
#model.refreshLayerLegend(ltl)


