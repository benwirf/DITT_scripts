project = QgsProject.instance()
pdk_lyr = project.mapLayersByName('Kidman_Paddocks')[0]
wpt_lyr = project.mapLayersByName('Kidman_Waters')[0]

buffer_dist = 1500# meters

output_lyr = QgsVectorLayer('LineString?crs=epsg:7845', 'arrow_lines', 'memory')
output_lyr.dataProvider().addAttributes([QgsField('Waterpoint', QVariant.String),
                                        QgsField('Paddock', QVariant.String)])
output_lyr.updateFields()

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

out_feats = []

all_ids = []
for k, v in pdk_wpts.items():
    all_ids.append(parse_waterpoints(v))

ids = list(set([i for r in all_ids for i in r]))
#print(ids)
for id in ids:
    wpt_ft = wpt_lyr.getFeature(id)
    wpt_geom = wpt_ft.geometry()
    start_pt = wpt_geom.asPoint()#QgsPointXY
    wa_geom = wpt_geom.buffer(buffer_dist, 25)
    pdks = []
    for k, v in pdk_wpts.items():
        wpt_ids = parse_waterpoints(v)
        if id in wpt_ids:
            pdks.append(k)
    #print(id, pdks)
    for pdk in pdks:
        pdk_feat = [ft for ft in pdk_lyr.getFeatures() if ft['NAME'] == pdk][0]
        pdk_wa = wa_geom.intersection(pdk_feat.geometry())
        end_pt = pdk_wa.centroid().asPoint()
        line_geom = QgsGeometry.fromPolylineXY([start_pt, end_pt])
        line_feat = QgsFeature(output_lyr.fields())
        line_feat.setGeometry(line_geom)
        line_feat.setAttributes([wpt_ft['FEATURE'], pdk])
        out_feats.append(line_feat)
    
output_lyr.dataProvider().addFeatures(out_feats)
output_lyr.updateExtents()
project.addMapLayer(output_lyr)
            