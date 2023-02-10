lyr = iface.activeLayer()

if lyr.isValid():
    prov = lyr.dataProvider()
    stats = prov.bandStatistics(1, QgsRasterBandStats.All, lyr.extent(), 0)
    min = stats.minimumValue
    max = stats.maximumValue
    color_ramp = QgsStyle.defaultStyle().colorRamp('BrBG')
    ramp_shader = qgis.core.QgsColorRampShader(min, max, color_ramp)
    ramp_shader.classifyColorRamp() # Need this line!
    raster_shader = QgsRasterShader()
    raster_shader.setRasterShaderFunction(ramp_shader)
    renderer = QgsSingleBandPseudoColorRenderer(prov, 1, raster_shader)
    lyr.setRenderer(renderer)
    lyr.triggerRepaint()