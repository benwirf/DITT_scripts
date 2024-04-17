project = QgsProject.instance()

buffer_dist = 500# meters
            
pdk_wpts = {'Acacia': 'Trough(45); Tank(17)',
            'Acacia Cooler': 'Tank(17)',
            'Supplejack': 'Trough(50); Trough(39)',
            'Road': 'Trough(45)',
            'Boab': 'Tank(47); Turkey Nest(15); Trough(50)',
            'No Name': 'Waterhole(18)',
            'Snappy Gum': 'Trough(51); Dam(3)',
            'Little Rosewood': 'Dam(2); Trough(24)',
            'Dogwood': 'Trough(42)',
            'Corkwood': 'Trough(26); Trough(42)',
            'Rosewood West': 'Trough(42)',
            'Sullivans': 'Waterhole(52)',
            'Conkerberry': 'Trough(44); Tank(1)',
            'Suprise Creek': 'Trough(50); Trough(34)',
            'Coolibah': 'Trough(34); Trough(22); Tank(1)',
            'Nutwood': 'Tank(1); Trough(22)',
            'Improved': 'Tank(20)',
            'Gutta Percha': 'Trough(46); Trough(45)',
            'Hakea': 'Trough(31)',
            'Bloodwood': 'Trough(31)',
            'Rubberbush': 'Trough(30)',
            'Weaner': 'Trough(23); Tank(1)',
            'Bull': 'Trough(23)',
            'Bauhinia': 'Trough(30)',
            'Box': 'Trough(14); Waterhole(41)'}
            
def parse_waterpoints(data_string):
    wp_ids = []
    wp_items = data_string.split(';')
    for wp in wp_items:
        wp_id = wp.split('(')[1].split(')')[0]
        wp_ids.append(int(wp_id))
    return wp_ids
            
pdk_lyr = project.mapLayersByName('Kidman_Paddocks')[0]
wpt_lyr = project.mapLayersByName('Kidman_Waters')[0]

wa_lyr = QgsVectorLayer('Polygon?crs=epsg:7845', 'temp_wa', 'memory')
wa_lyr.dataProvider().addAttributes([QgsField('Pdk_Name', QVariant.String),
                                    QgsField('Pdk_ID', QVariant.Int),
                                    QgsField('Water pts', QVariant.String),
                                    QgsField('Area_m2', QVariant.Double, len=10, prec=3),
                                    QgsField('Area_ha', QVariant.Double, len=10, prec=3),
                                    QgsField('Area_km2', QVariant.Double, len=10, prec=5)])
wa_lyr.updateFields()

wa_feats = []

for pdk_ft in pdk_lyr.getFeatures():
    pdk_name = pdk_ft['NAME']
    if not pdk_name in list(pdk_wpts.keys()):
        continue
    wpt_info = pdk_wpts[pdk_name]
    wpt_ids = parse_waterpoints(wpt_info)#list of ids
    wpt_fts = wpt_lyr.getFeatures(wpt_ids)
    wa_geoms = [ft.geometry().buffer(buffer_dist, 25) for ft in wpt_fts]
    wa_geom = QgsGeometry.unaryUnion(wa_geoms)
    pdk_wa_geom = wa_geom.intersection(pdk_ft.geometry())
    pdk_wa_ft = QgsFeature(wa_lyr.fields())
    pdk_wa_ft.setGeometry(pdk_wa_geom)
    pdk_wa_ft.setAttributes([pdk_name,
                            pdk_ft.id(),
                            wpt_info,
                            round(pdk_wa_geom.area(), 3),#m2
                            round(pdk_wa_geom.area()/10000, 3),#ha
                            round(pdk_wa_geom.area()/1000000, 5)])#km2
    wa_feats.append(pdk_wa_ft)

wa_lyr.dataProvider().addFeatures(wa_feats)
wa_lyr.updateExtents()
project.addMapLayer(wa_lyr)

