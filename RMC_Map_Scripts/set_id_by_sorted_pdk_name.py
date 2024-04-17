lyr = QgsProject.instance().mapLayersByName('Paddock_Land_Types')[0]

all_feats = [ft for ft in lyr.getFeatures()]

sorted_feats = sorted(all_feats, key = lambda ft: (ft['Paddock'], ft['LANDSYSTEM']))

fld_idx = lyr.fields().lookupField('ID')

att_map = {}

id = 1

for ft in sorted_feats:
    #print(ft.attributes())
    att_map[ft.id()] = {fld_idx: id}
    id+=1

lyr.dataProvider().changeAttributeValues(att_map)

print('Done')