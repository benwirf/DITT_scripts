project = QgsProject.instance()

pdks_lyr = project.mapLayersByName('CDU_Paddocks')[0]
wpt_lyr = project.mapLayersByName('CDU_Waterpoints')[0]
lu_lyr = project.mapLayersByName('Katherine_Rural_College_LU')[0]

output_lyr = QgsVectorLayer('Polygon?crs=epsg:28353', 'CDU_cc_summary', 'memory')
#print(output_lyr.isValid())

flds = [QgsField('ID', QVariant.String),
        QgsField('Paddock', QVariant.String),
        QgsField('Land_Unit', QVariant.String),
        QgsField('Pdk_LU_area_km2', QVariant.Double, len=10, prec=5),
        QgsField('3km_WA_LU_area_km2', QVariant.Double, len=10, prec=5),
        QgsField('5km_WA_LU_area_km2', QVariant.Double, len=10, prec=5),
        QgsField('Watered_LU_area', QVariant.Double, len=10, prec=5),
        QgsField('Pcnt_LU_watered', QVariant.Double, len=10, prec=1)]
        
output_lyr.dataProvider().addAttributes(flds)
output_lyr.updateFields()

output_features = []

ID = 1

for pdk in pdk_lyr.getFeatures():
    PADDOCK_NAME = pdk['Pdk_Name']
    pdk_geom = pdk.geometry()
    pdk_wpts = [ft for ft in wpt_lyr.getFeatures() if ft.geometry().within(pdk_geom)]
    if pdk_wpts:
        buffers_3km = [ft.geometry().buffer(3000, 25) for ft in pdk_wpts]
        dissolved_3km_buffers = QgsGeometry.unaryUnion(buffers_3km)
        pdk_3km_wa = dissolved_3km_buffers.intersection(pdk_geom)
        buffers_5km = [ft.geometry().buffer(5000, 25) for ft in pdk_wpts]
        dissolved_5km_buffers = QgsGeometry.unaryUnion(buffers_5km)
        pdk_5km_wa = dissolved_5km_buffers.intersection(pdk_geom)
    
    pdk_lu_names = [ft['LAND_UNIT'] for ft in lu_lyr.getFeatures() if ft.geometry().intersects(pdk_geom)]
    
    for LAND_UNIT_NAME in pdk_lu_names:
        
        land_unit_features = [ft for ft in lu_lyr.getFeatures() if ft['LAND_UNIT'] == LAND_UNIT_NAME]
        lu_multipart_geom = QgsGeometry.collectGeometry([ft.geometry() for ft in land_unit_features])
        lu_in_pdk = lu_multipart_geom.intersection(pdk_geom)
        PDK_LU_AREA = lu_in_pdk.area()
        pdk_3km_wa_lu = lu_in_pdk.intersection(pdk_3km_wa)
        PDK_3KM_WA_LU_AREA = pdk_3km_wa_lu.area()
        pdk_5km_wa_lu = lu_in_pdk.intersection(pdk_5km_wa)
        PDK_5KM_WA_LU_AREA = pdk_5km_wa_lu.area()
        # We use 50% of the area between 3 and 5km from water so...
        # subtract 3km wa from 5km wa to get 3-5km wa as a band, divide it by 2 then add it back to the 3km wa
        WATERED_LU_AREA = ((PDK_5KM_WA_LU_AREA-PDK_3KM_WA_LU_AREA)/2)+PDK_3KM_WA_LU_AREA
        PCNT_LU_WATERED = (WATERED_LU_AREA/PDK_LU_AREA)*100
        
        output_attributes = [ID,
                            PADDOCK_NAME,
                            LAND_UNIT_NAME,
                            round(PDK_LU_AREA/1000000, 5),
                            round(PDK_3KM_WA_LU_AREA/1000000, 5),
                            round(PDK_5KM_WA_LU_AREA/1000000, 5),
                            round(WATERED_LU_AREA/1000000, 5),
                            round(PCNT_LU_WATERED, 1)]
        
        output_feat = QgsFeature(output_lyr.fields())
        output_feat.setGeometry(lu_in_pdk)
        output_feat.setAttributes(output_attributes)
        
        is_dup_geom = False
        for feat in output_features:
            if feat.geometry().isGeosEqual(output_feat.geometry()):
                is_dup_geom = True
        if not is_dup_geom:
            output_features.append(output_feat)
        
            ID+=1
        
output_lyr.dataProvider().addFeatures(output_features)
project.addMapLayer(output_lyr)
