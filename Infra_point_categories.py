lyr = QgsProject.instance().mapLayersByName('Extracted')[0]

categories = ['Aerial or Tower', 'Bore', 'Dam', 'Gate', 'General Building', 'Homestead', 'Landing Ground', 'Spring', 'Stock Yard', 'Trough', 'Underground Mine', 'Water Tank']

ids = [ft.id() for ft in lyr.getFeatures() if ft['FEATURE'] not in categories]

lyr.selectByIds(ids)