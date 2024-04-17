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

all_ids = []
for k, v in pdk_wpts.items():
    all_ids.append(parse_waterpoints(v))

ids = list(set([i for r in all_ids for i in r]))
#print(ids)
project = QgsProject.instance()
wpt_lyr = project.mapLayersByName('Kidman_Waters')[0]
output_lyr = QgsVectorLayer('Point?crs=epsg:7845', 'temp_wpts', 'memory')
output_lyr.dataProvider().addAttributes(wpt_lyr.fields())
output_lyr.updateFields()

out_feats = []

for ft in wpt_lyr.getFeatures(ids):
    out_feat = QgsFeature(output_lyr.fields())
    out_feat.setGeometry(ft.geometry())
    out_feat.setAttributes(ft.attributes())
    out_feats.append(out_feat)

output_lyr.dataProvider().addFeatures(out_feats)

project.addMapLayer(output_lyr)
