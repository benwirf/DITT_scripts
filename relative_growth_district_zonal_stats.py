import os

project = QgsProject.instance()

output_folder = r'R:\LID-BigData\SPATIAL DATA\PROJECTS\Northern Territory\Feed Outlook\2023\NOVEMBER-2023\OUTPUT\Relative_Growth_Outputs'

# Edit layer names & change/add layers as required
# located in DATA/PERCENTILE_GROWTH folder
relative_growth_rasters = [project.mapLayersByName('202310.03months.growth.pcnt.nt')[0],
                            project.mapLayersByName('202310.06months.growth.pcnt.nt')[0]]
                            
district_layer = project.mapLayersByName('PASTORAL_DISTRICTS_4326')[0]

def calculate_district_stats(pcnt_growth_lyr, district_lyr):
    pcnt_growth_lyr_name = pcnt_growth_lyr.name()
    mnth = pcnt_growth_lyr_name.split('.')[1][:2]
    values_over_100_removed = processing.run("qgis:rastercalculator",
                    {'EXPRESSION':f'(("{pcnt_growth_lyr_name}@1" <= 100) * "{pcnt_growth_lyr_name}@1") + (("{pcnt_growth_lyr_name}@1" > 100) * -999)',
                    'LAYERS':[pcnt_growth_lyr],
                    'CELLSIZE':0,
                    'EXTENT':None,
                    'CRS':None,
                    'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']
                    
    values_over_100_nodata = processing.run("gdal:translate",
                    {'INPUT':values_over_100_removed,
                    'TARGET_CRS':None,
                    'NODATA':-999,
                    'COPY_SUBDATASETS':False,'OPTIONS':'',
                    'EXTRA':'',
                    'DATA_TYPE':0,
                    'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']
                    
    zonal_stats = processing.run("native:zonalstatisticsfb",
                    {'INPUT':district_layer,
                    'INPUT_RASTER':values_over_100_nodata,
                    'RASTER_BAND':1,
                    'COLUMN_PREFIX':'_',
                    'STATISTICS':[2,3,5,6],
                    'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']
                    
    # Run export to spreadsheet...
    processing.run("native:exporttospreadsheet",
                    {'LAYERS':[zonal_stats],
                    'USE_ALIAS':False,
                    'FORMATTED_VALUES':False,
                    'OUTPUT':os.path.join(output_folder, f'Relative_{mnth}mnth_growth_district_stats.xlsx'),
                    'OVERWRITE':False})
                    
for rast in relative_growth_rasters:
    calculate_district_stats(rast, district_layer)
    
print('Done')