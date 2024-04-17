lyr = iface.activeLayer()
r = lyr.renderer()
for c in r.categories():
    print(f'{c.value()}-{c.symbol().color().name()}')
