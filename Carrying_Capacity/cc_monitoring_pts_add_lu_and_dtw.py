project = QgsProject.instance()


wpt_lyr = project.mapLayersByName('CDU_Waterpoints')[0]
lu_lyr = project.mapLayersByName('Katherine_Rural_College_LU')[0]
dtw_lyr = project.mapLayersByName('CDU_Paddocks')[0]

output_lyr = QgsVectorLayer('Polygon?crs=epsg:28353', 'CDU_cc_summary', 'memory')