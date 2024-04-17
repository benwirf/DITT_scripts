project = QgsProject.instance()

output_boundaries = QgsVectorLayer('Polygon?crs=epsg:7845', 'Boundaries', 'memory')

output_boundaries.dataProvider().addAttributes([QgsField('DISTRICT', QVariant.String),
                                                QgsField('NAME', QVariant.String),
                                                QgsField('AREA_KM2',QVariant.Double)])
                                                
output_boundaries.updateFields()

kidman = project.mapLayersByName('Reprojected')[0]# Kidman_Boundary reprojected to 7845
kdm_bdry = [ft for ft in kidman.getFeatures()][0]
kdm_bdry_feat = QgsFeature(output_boundaries.fields())
kdm_bdry_feat.setGeometry(kdm_bdry.geometry())
kdm_bdry_feat.setAttributes(['VRD', 'Kidman Springs Research Station', round(kdm_bdry.geometry().area()/1000000, 3)])
output_boundaries.dataProvider().addFeatures([kdm_bdry_feat])

mrk = project.mapLayersByName('MRK_BDRY')[0]
mrk_bdry = [ft for ft in mrk.getFeatures()][0]
mrk_bdry_feat = QgsFeature(output_boundaries.fields())
mrk_bdry_feat.setGeometry(mrk_bdry.geometry())
mrk_bdry_feat.setAttributes(['Northern Alice Springs', 'Mount Riddock', round(mrk_bdry.geometry().area()/1000000, 3)])
output_boundaries.dataProvider().addFeatures([mrk_bdry_feat])

omp = project.mapLayersByName('OMP Boundary')[0]
omp_bdry = [ft for ft in omp.getFeatures()][0]
omp_bdry_feat = QgsFeature(output_boundaries.fields())
omp_bdry_feat.setGeometry(omp_bdry.geometry())
omp_bdry_feat.setAttributes(['Southern Alice Springs', 'Old Man Plains Research Station', round(omp_bdry.geometry().area()/1000000, 3)])
output_boundaries.dataProvider().addFeatures([omp_bdry_feat])

project.addMapLayer(output_boundaries)
                                                