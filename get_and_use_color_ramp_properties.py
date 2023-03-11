# 14/02/23

# get properties from existing color ramp...

l = iface.activeLayer()
r = l.renderer().shader().rasterShaderFunction().sourceColorRamp()
print(r.properties())

##or...
#l = iface.activeLayer()
#r = l.renderer().shader().rasterShaderFunction().createColorRamp()
#print(r.properties())

def style_raster(rl, max, min):
    props = {'color1': '1,133,113,255',
            'color2': '166,97,26,255',
            'discrete': '0',
            'rampType': 'gradient',
            'stops': '0.25;128,205,193,255:0.5;245,245,245,255:0.75;223,194,125,255'}

    color_ramp = QgsGradientColorRamp.create(props)
    renderer = QgsSingleBandPseudoColorRenderer(rl.dataProvider(), 1)
    renderer.setClassificationMin(min)
    renderer.setClassificationMax(max)
    renderer.createShader(color_ramp, QgsColorRampShader.Interpolated, QgsColorRampShader.EqualInterval, 5)# Don't use Continuous
    rl.setRenderer(renderer)
    rl.triggerRepaint()
