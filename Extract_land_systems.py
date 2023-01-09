
ls_lyr = QgsProject.instance().mapLayersByName('ntls_1m_gda2020')[0]
pdk_lyr = QgsProject.instance().mapLayersByName('Mulga_Park_Pdks')[0]
wa_3km_lyr = QgsProject.instance().mapLayersByName('Mulga_Park_3km_WA')[0]
wa_5km_lyr = QgsProject.instance().mapLayersByName('Mulga_Park_5km_WA')[0]
property_name = 'Mulga_Park'
crs = ls_lyr.crs().authid()

flds = QgsFields()

for f in [QgsField('property', QVariant.String),
        QgsField('padd_num', QVariant.Int),
        QgsField('padd_name', QVariant.String)]:
    flds.append(f)

for f in ls_lyr.fields():
    flds.append(f)

#print([f for f in flds])

# Create temp land systems layers
ls_pdks = QgsVectorLayer(f'Polygon?crs={crs}', f'{property_name}_ls_pdks', 'memory')
ls_pdks.dataProvider().addAttributes(flds)
ls_pdks.updateFields()

ls_3km_wa = QgsVectorLayer(f'Polygon?crs={crs}', f'{property_name}_ls_3km_wa', 'memory')
ls_3km_wa.dataProvider().addAttributes(flds)
ls_3km_wa.updateFields()

ls_5km_wa = QgsVectorLayer(f'Polygon?crs={crs}', f'{property_name}_ls_5km_wa', 'memory')
ls_5km_wa.dataProvider().addAttributes(flds)
ls_5km_wa.updateFields()

#print(len(ls_pdks.fields()))

ls_idx = QgsSpatialIndex(ls_lyr.getFeatures())

for i, p in enumerate(pdk_lyr.getFeatures()):
    p_name = p['PADDOCK']
    c = ls_idx.intersects(p.geometry().boundingBox())
    ix_ls = [f for f in ls_lyr.getFeatures(c) if f.geometry().intersects(p.geometry())]
    l_systems = set([f['LANDSYSTEM'] for f in ix_ls])
    for ls in l_systems:
        ft = QgsFeature(flds)
        ftgeom = QgsGeometry.collectGeometry([f.geometry().intersection(p.geometry()) for f in ix_ls if f['LANDSYSTEM'] == ls])
        ft.setGeometry(ftgeom)
        ft['property'] = property_name
        ft['padd_num'] = i+1
        ft['padd_name'] = p['PADDOCK']
        ft['LANDSYSTEM'] = ls
        src_ft = [ft for ft in ls_lyr.getFeatures() if ft['LANDSYSTEM'] == ls][0]
        target_flds = [f.name() for f in flds if f.name() not in ['property', 'padd_num', 'padd_name', 'LANDSYSTEM', 'Area_m2', 'Area_ha', 'Area_km2']]
        for fname in target_flds:
            ft[fname] = src_ft[fname]
        ft['Area_m2'] = round(ftgeom.area(), 2)
        ft['Area_ha'] = round(ftgeom.area()/10000, 3)
        ft['Area_km2'] = round(ftgeom.area()/1000000, 5)
        ls_pdks.dataProvider().addFeature(ft)

for i, wa in enumerate(wa_3km_lyr.getFeatures()):
    p_name = wa['padd_name']
    c = ls_idx.intersects(wa.geometry().boundingBox())
    ix_ls = [f for f in ls_lyr.getFeatures(c) if f.geometry().intersects(wa.geometry())]
    l_systems = set([f['LANDSYSTEM'] for f in ix_ls])
    for ls in l_systems:
        ft = QgsFeature(flds)
        ftgeom = QgsGeometry.collectGeometry([f.geometry().intersection(wa.geometry()) for f in ix_ls if f['LANDSYSTEM'] == ls])
        ft.setGeometry(ftgeom)
        ft['property'] = property_name
        ft['padd_num'] = i+1
        ft['padd_name'] = wa['padd_name']
        ft['LANDSYSTEM'] = ls
        src_ft = [ft for ft in ls_lyr.getFeatures() if ft['LANDSYSTEM'] == ls][0]
        target_flds = [f.name() for f in flds if f.name() not in ['property', 'padd_num', 'padd_name', 'LANDSYSTEM', 'Area_m2', 'Area_ha', 'Area_km2']]
        for fname in target_flds:
            ft[fname] = src_ft[fname]
        ft['Area_m2'] = round(ftgeom.area(), 2)
        ft['Area_ha'] = round(ftgeom.area()/10000, 3)
        ft['Area_km2'] = round(ftgeom.area()/1000000, 5)
        ls_3km_wa.dataProvider().addFeature(ft)

for i, wa in enumerate(wa_5km_lyr.getFeatures()):
    p_name = wa['padd_name']
    c = ls_idx.intersects(wa.geometry().boundingBox())
    ix_ls = [f for f in ls_lyr.getFeatures(c) if f.geometry().intersects(wa.geometry())]
    l_systems = set([f['LANDSYSTEM'] for f in ix_ls])
    for ls in l_systems:
        ft = QgsFeature(flds)
        ftgeom = QgsGeometry.collectGeometry([f.geometry().intersection(wa.geometry()) for f in ix_ls if f['LANDSYSTEM'] == ls])
        ft.setGeometry(ftgeom)
        ft['property'] = property_name
        ft['padd_num'] = i+1
        ft['padd_name'] = wa['padd_name']
        ft['LANDSYSTEM'] = ls
        src_ft = [ft for ft in ls_lyr.getFeatures() if ft['LANDSYSTEM'] == ls][0]
        target_flds = [f.name() for f in flds if f.name() not in ['property', 'padd_num', 'padd_name', 'LANDSYSTEM', 'Area_m2', 'Area_ha', 'Area_km2']]
        for fname in target_flds:
            ft[fname] = src_ft[fname]
        ft['Area_m2'] = round(ftgeom.area(), 2)
        ft['Area_ha'] = round(ftgeom.area()/10000, 3)
        ft['Area_km2'] = round(ftgeom.area()/1000000, 5)
        ls_5km_wa.dataProvider().addFeature(ft)
        
QgsProject.instance().addMapLayers([ls_pdks, ls_3km_wa, ls_5km_wa])

