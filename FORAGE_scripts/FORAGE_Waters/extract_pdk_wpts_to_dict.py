project = QgsProject.instance()
wa_lyr = project.mapLayersByName('Kidman_5km_WA')[0]

pdk_wpts = {}

for ft in wa_lyr.getFeatures():
    pdk_wpts[ft['Pdk_Name']] = ft['Water pts']

print(pdk_wpts)