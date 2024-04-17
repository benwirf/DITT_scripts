project = QgsProject.instance()

lyr = project.mapLayersByName('Birrindudu_Land_Systems')[0]

r = lyr.renderer()

for c in r.categories():
#    mu = c.value()
#    ls = [ft for ft in lyr.getFeatures() if ft['MAPUNIT'] == mu][0]['LANDSYSTEM']
    ls = c.value()
    mu = [ft for ft in lyr.getFeatures() if ft['LANDSYSTEM'] == ls][0]['MAPUNIT']
    sym = c.symbol()
    print(mu, ls, sym.color().name())