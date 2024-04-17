lyr = QgsProject.instance().mapLayersByName('Paddock_Land_Types')[0]

fts = [ft for ft in lyr.getFeatures()]

sorted_fts = sorted(fts, key = lambda ft: ft['ID'])

count = 1

for ft in sorted_fts:
    print(count, ft['Paddock'], ft['ID'])
    count+=1