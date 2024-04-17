project = QgsProject.instance()

output_lyr = QgsVectorLayer('Polygon?crs=epsg:7845', 'forage_pdks', 'memory')

flds_to_add = [QgsField('NAME', QVariant.String),
                QgsField('DISTRICT', QVariant.String),
                QgsField('PROPERTY', QVariant.String),
                QgsField('AREA_KM2', QVariant.Double, len=10, prec=5)]
                
output_lyr.dataProvider().addAttributes(flds_to_add)

output_lyr.updateFields()

kidman_lyr = project.mapLayersByName('Kidman_Paddocks')[0]

rocklands_lyr = project.mapLayersByName('Rockland_NT_Paddocks')[0]

omp_lyr = project.mapLayersByName('OMP_Paddocks')[0]

src_lyrs = [kidman_lyr, rocklands_lyr, omp_lyr]

out_feats = []

for lyr in src_lyrs:
    for ft in lyr.getFeatures():
        feat = QgsFeature(output_lyr.fields())
        feat.setGeometry(ft.geometry())
        if lyr.name() == 'Rockland_NT_Paddocks':
            atts = [ft['Name'], 'Barkly', 'Rocklands']
        else:
            atts = [att for att in ft.attributes()][1:][:4]
        atts.append(round(ft.geometry().area()/1000000, 5))
        feat.setAttributes(atts)
        out_feats.append(feat)

output_lyr.dataProvider().addFeatures(out_feats)

output_lyr.updateExtents()

project.addMapLayer(output_lyr)