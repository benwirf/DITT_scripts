lyr = iface.activeLayer()
color1 = QColor(0, 255, 0)
color2 = QColor(255, 0, 0)

if lyr.isValid():
    prov = lyr.dataProvider()
    stats = prov.bandStatistics(
        1, QgsRasterBandStats.All, lyr.extent(), 0
    )
    min = stats.minimumValue
    max = stats.maximumValue
    renderer = QgsSingleBandPseudoColorRenderer(
        lyr.dataProvider(), band=1
    )
    color_ramp = QgsGradientColorRamp(
        color1, color2
    )
    renderer.setClassificationMin(min)
    renderer.setClassificationMax(max)
    renderer.createShader(color_ramp)
    lyr.setRenderer(renderer)
    lyr.triggerRepaint()
