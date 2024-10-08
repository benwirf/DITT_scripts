'''
This script calculates percentage burnt for each pastoral property
from NAFI firescars to date shapefile via multiple processing steps.
Firescar geometries are fixed, then clipped to a buffered NT boundary,
reprojected to epsg:9473 to match the property layer and clipped to the
pastoral properties. Firescar features are then extracted for relevant months
and dissolved (areas checked pre/post dissolve). Overlap analysis is run for
firescars & properties and fields are added for rounded area in km2 and rounded
percent. Finally, the result is saved to a spreadsheet. Some intermediate
result layers are also saved as geopackages.
'''

import os

fs_to_date = 'Sep_10'# Change Output folder path

fire_period = 'jul-dec-24'

# Used in extractbyexpression processing step
months_to_extract = '(7, 8, 9, 10, 11, 12)'

project = QgsProject.instance()# pastoral_properties_burnt.qgz

properties_lyr = project.mapLayersByName('Pastoral_Property_Boundaries')[0]# epsg:9473
firescar_lyr = project.mapLayersByName('fs2024shp')[0]# epsg:4283
nt_buffered_lyr = project.mapLayersByName('NT_buffered')[0]# epsg:4283

output_folder = r'C:\Users\qw2\Desktop\Pastoral_Properties_Burnt\Results_Jul-Dec-24'

print('fixing firescar geometries...')
firescars_fixed = processing.run("native:fixgeometries",
                {'INPUT':firescar_lyr,
                'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']

print('clipping firescars to NT...')
fs_clipped_to_nt = processing.run("native:clip",
                {'INPUT':firescars_fixed,
                'OVERLAY': nt_buffered_lyr,
                'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']

print('reprojecting firescars to EPSG:9473...')
fs_9473 = processing.run("native:reprojectlayer",
                {'INPUT':fs_clipped_to_nt,
                'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:9473'),'OPERATION':'+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad +step +proj=push +v_3 +step +proj=cart +ellps=GRS80 +step +proj=helmert +x=0.06155 +y=-0.01087 +z=-0.04019 +rx=-0.0394924 +ry=-0.0327221 +rz=-0.0328979 +s=-0.009994 +convention=coordinate_frame +step +inv +proj=cart +ellps=GRS80 +step +proj=pop +v_3 +step +proj=aea +lat_0=0 +lon_0=132 +lat_1=-18 +lat_2=-36 +x_0=0 +y_0=0 +ellps=GRS80',
                'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']

print('clipping firescars to pastoral properties...')
firescars_on_pastoral_estate = processing.run("native:clip",
                {'INPUT':fs_9473,
                'OVERLAY':properties_lyr,
                'OUTPUT':os.path.join(output_folder, f'all_pastoral_firescars_{fire_period}.gpkg')})['OUTPUT']

print('extracting firescars by month burnt...')
firescars_jul_dec = processing.run("native:extractbyexpression",
                {'INPUT':firescars_on_pastoral_estate,
                'EXPRESSION':f'"month" IN {months_to_extract}',
                'OUTPUT':os.path.join(output_folder, f'Property_FS_Jul_1-{fs_to_date}.gpkg')})['OUTPUT']

print('dissolving result firescars...')
fs_jul_dec_dissolved = processing.runAndLoadResults("native:dissolve",
                {'INPUT':firescars_jul_dec,
                'FIELD':[],
                'OUTPUT':os.path.join(output_folder, f'fs_dissolved_{fire_period}.gpkg')})['OUTPUT']

fs_lyr = QgsVectorLayer(firescars_jul_dec, '', 'ogr')

fs_dissolved_lyr = QgsVectorLayer(fs_jul_dec_dissolved, '', 'ogr')

print('checking total areas...')
original_total_area = sum([ft.geometry().area() for ft in fs_lyr.getFeatures()])
print(f'Original Area: {original_total_area}')
dissolved_total_area = sum([ft.geometry().area() for ft in fs_dissolved_lyr.getFeatures()])
print(f'Dissolved Area: {dissolved_total_area}')

if original_total_area == dissolved_total_area:
    print('Total areas match')

print('Calculating firescar/property overlap...')
overlaps = processing.run("native:calculatevectoroverlaps",
                {'INPUT':properties_lyr,
                'LAYERS':[firescars_jul_dec],
                'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']

print('Adding rounded area km2 and percent fields...')
field_1_added = processing.run("native:fieldcalculator",
                {'INPUT':overlaps,
                'FIELD_NAME':'area_burnt_km2',
                'FIELD_TYPE':0,
                'FIELD_LENGTH':0,
                'FIELD_PRECISION':3,
                'FORMULA':f'round("Property_FS_Jul_1-{fs_to_date}_area"/1000000, 3)',
                'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']
                
field_2_added = processing.runAndLoadResults("native:fieldcalculator",
                {'INPUT':field_1_added,
                'FIELD_NAME':'pcnt_burnt',
                'FIELD_TYPE':0,
                'FIELD_LENGTH':0,
                'FIELD_PRECISION':2,
                'FORMULA':f'round("Property_FS_Jul_1-{fs_to_date}_pc", 2)',
                'OUTPUT':os.path.join(output_folder, f'fire_property_overlap_{fire_period}.gpkg')})['OUTPUT']

print('Saving overlap results to spreadsheet...')

processing.run("native:exporttospreadsheet",
                {'LAYERS':[field_2_added],
                'USE_ALIAS':False,
                'FORMATTED_VALUES':False,
                'OUTPUT':os.path.join(output_folder, f'Property_Pcnt_Burnt_Jul_1-{fs_to_date}.xlsx'),
                'OVERWRITE':False})

fs_lyr = None
fs_dissolved_lyr = None

print('Done')