project = QgsProject.instance()

pdk_lyr = project.mapLayersByName('MGP_all_paddocks')[0]

name_fld = 'LABEL'

waterpoint_lyr = project.mapLayersByName('MGP_waterpoints')[0]

target_crs = waterpoint_lyr.sourceCrs()

# print(target_crs.authid())

output_lyr = QgsVectorLayer(f'Polygon?crs={target_crs.authid()}', 'Watered_bands', 'memory')
# print(output_lyr.isValid())
flds = QgsFields()

flds_to_add = [QgsField('Pdk Name', QVariant.String),
                QgsField('PdkArea Ha', QVariant.Double, len=10, prec=2),
                QgsField('DTW Band', QVariant.String),
                QgsField('Outer dist', QVariant.Int),
                QgsField('Area Ha', QVariant.Double, len=10, prec=2),
                QgsField('Percent', QVariant.Double, len=10, prec=7)]
                
for fld in flds_to_add:
    flds.append(fld)
    
output_lyr.dataProvider().addAttributes(flds)
output_lyr.updateFields()

for pdk in pdk_lyr.getFeatures():
    pdk_name = pdk[name_fld]
    print(pdk_name)
    pdk_area = round(pdk.geometry().area()/10000, 2)# Hectares
    # get all waterpoints which fall inside the current paddock
    waterpoint_geoms = [wp.geometry() for wp in waterpoint_lyr.getFeatures() if wp.geometry().within(pdk.geometry())]
    if waterpoint_geoms:
        band_width = 500
        buffer_distance = band_width
        band_count = 0
        band_intersects = True
        # dissolved buffer of all paddock waterpoints
        # this will be the first 'band' (just a buffer around waterpoint)
        first_buffer = QgsGeometry.unaryUnion([geom.buffer(buffer_distance, 25) for geom in waterpoint_geoms])
        print(f'Band count: {band_count}')
        if band_count == 0:
            clipped_to_pdk = first_buffer.intersection(pdk.geometry())
            area_ha = round(clipped_to_pdk.area()/10000, 2)
            pcnt = round((area_ha/pdk.geometry().area())*100, 7)
            feat = QgsFeature(output_lyr.fields())
            feat.setGeometry(clipped_to_pdk)
            feat.setAttributes([pdk_name, pdk_area, f'0-{buffer_distance}m', buffer_distance, area_ha, pcnt])
            output_lyr.dataProvider().addFeatures([feat])
            buffer_distance+=band_width
            band_count+=1
        # these will be 'band buffers' composed of difference between current & previous buffer
        # break the loop if the last buffer does not intersect the paddock
        while band_intersects and band_count < 500:
            print(f'Band count: {band_count}')
            outer_ring = QgsGeometry.unaryUnion([geom.buffer(buffer_distance, 25) for geom in waterpoint_geoms])
            inner_ring = QgsGeometry.unaryUnion([geom.buffer(buffer_distance-band_width, 25) for geom in waterpoint_geoms])
            dtw_band = outer_ring.difference(inner_ring)
            if dtw_band.intersects(pdk.geometry()):
                clipped_to_pdk = dtw_band.intersection(pdk.geometry())
                area_ha = round(clipped_to_pdk.area()/10000, 2)
                pcnt = round((area_ha/pdk.geometry().area())*100, 7)
                feat = QgsFeature(output_lyr.fields())
                feat.setGeometry(clipped_to_pdk)
                feat.setAttributes([pdk_name,
                                    pdk_area,
                                    f'{buffer_distance-band_width}-{buffer_distance}m',
                                    buffer_distance,
                                    area_ha,
                                    pcnt])
                output_lyr.dataProvider().addFeatures([feat])
                buffer_distance+=band_width
                band_count+=1
            else:
                band_intersects = False
            

project.addMapLayer(output_lyr)