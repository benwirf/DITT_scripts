from datetime import date
import calendar
import os
import csv


project = QgsProject.instance()

months_dict = dict((month, index) for index, month in enumerate(calendar.month_name) if month)

homerange_source_folder = r'Paddock_Power_GPS/home_range_geopackage_files/BIG_MUDGEE'

cibo_tc_folder = r'C:/Users/qw2/Desktop/Paddock_Power_GPS/Cibo_TC'

cibo_tsdm_folder = r'C:/Users/qw2/Desktop/Paddock_Power_GPS/Cibo_TSDM'

period_1_months = ['June', 'July', 'August', 'September', 'October', 'November', 'December']
period_2_months = ['January', 'February', 'March', 'April', 'May']

def get_file_date(file_name):
    '''
    Returns the correct date (year & month) associated with each homerange geopackage
    To allow for processing in the logical order by date and to enable looking up the
    correct Cibo TC & TSDM rasters.
    '''
    month = file_name.split('.')[0].split('_')[1]
    if month in period_1_months:
        actual_year = str(int(folder_year) - 1)
    elif month in period_2_months:
        actual_year = folder_year
    mnth_digit = months_dict[month]
    yr_and_mnth = f'{actual_year}{str(mnth_digit).zfill(2)}'
    dt = date(int(actual_year), mnth_digit, 1)
    return dt
    
def tsdm_file_path(date_string):
    '''
    Gets the path to the correct Cibo TSDM raster based on the date e.g. '202209'
    '''
    tsdm_fnames = [file.name for file in os.scandir(cibo_tsdm_folder) if date_string in file.name]
    if not tsdm_fnames:
        return
    elif tsdm_fnames:
        tsdm_fname = tsdm_fnames[0]
        tsdm_uri = os.path.join(cibo_tsdm_folder, tsdm_fname)
        return tsdm_uri
#        return tsdm_fname
        

def tc_file_path(date_string):
    '''
    Gets the path to the correct Cibo TC raster based on the date e.g. '202209'
    '''
    tc_fnames = [file.name for file in os.scandir(cibo_tc_folder) if date_string in file.name]
    if not tc_fnames:
        return
    elif tc_fnames:
        tc_fname = tc_fnames[0]
        tc_uri = os.path.join(cibo_tc_folder, tc_fname)
        return tc_uri
#        return tc_fname

def transformed_geom(g, src_crs, dest_crs):
    '''Don't need this function'''
    new_geom = QgsGeometry.fromWkt(g.asWkt())
    x_form = QgsCoordinateTransform(src_crs, dest_crs, project)
    new_geom.transform(x_form)
    return new_geom
    

def calculate_raster_stats(paddock_lyr, home_range_lyr, cibo_lyr):
    raster_stats = {}
    vector_layers = {}
    vector_layers['Entire_paddock'] = paddock_lyr
    
    hr_50_color = '#F8766D'
    hr_75_color = '#00BA38'
    hr_95_color = '#619CFF'
    
    hr_50_ids = [ft.id() for ft in home_range_lyr.getFeatures() if ft['colour'] == hr_50_color]
    hr_50_lyr = homerange_lyr.materialize(QgsFeatureRequest(hr_50_ids))
    dissolve_50_params = {'INPUT':hr_50_lyr,
                        'FIELD':[],
                        'OUTPUT':'TEMPORARY_OUTPUT'}
    hr_50_lyr_dissolved = processing.run("native:dissolve", dissolve_50_params)['OUTPUT']
    vector_layers['50_pcnt_homerange'] = hr_50_lyr_dissolved
    
    hr_75_ids = [ft.id() for ft in home_range_lyr.getFeatures() if ft['colour'] == hr_75_color]
    hr_75_lyr = homerange_lyr.materialize(QgsFeatureRequest(hr_75_ids))
    dissolve_75_params = {'INPUT':hr_75_lyr,
                        'FIELD':[],
                        'OUTPUT':'TEMPORARY_OUTPUT'}
    hr_75_lyr_dissolved = processing.run("native:dissolve", dissolve_75_params)['OUTPUT']
    vector_layers['75_pcnt_homerange'] = hr_75_lyr_dissolved
    
    hr_95_ids = [ft.id() for ft in home_range_lyr.getFeatures() if ft['colour'] == hr_95_color]
    hr_95_lyr = homerange_lyr.materialize(QgsFeatureRequest(hr_95_ids))
    dissolve_95_params = {'INPUT':hr_95_lyr,
                        'FIELD':[],
                        'OUTPUT':'TEMPORARY_OUTPUT'}
    hr_95_lyr_dissolved = processing.run("native:dissolve", dissolve_95_params)['OUTPUT']
    vector_layers['95_pcnt_homerange'] = hr_95_lyr_dissolved

    for lyr_name, vl in vector_layers.items():
        zonal_stats_params = {'INPUT':vl,
                                        'INPUT_RASTER':cibo_lyr,
                                        'RASTER_BAND':1,
                                        'COLUMN_PREFIX':'_',
                                        'STATISTICS':[3,5,6],
                                        'OUTPUT':'TEMPORARY_OUTPUT'}
        zonal_stats_results = processing.run("native:zonalstatisticsfb", zonal_stats_params)['OUTPUT']
        homerange_pcnt_feat = next(zonal_stats_results.getFeatures())
        med = homerange_pcnt_feat['_median']
        min = homerange_pcnt_feat['_min']
        max = homerange_pcnt_feat['_max']
        raster_stats[lyr_name] = [med, min, max]
    # Returns a dictionary of layer name and list of stats e.g. [median, min, max]
    return raster_stats
#############################################################################################################

output_csv = r'C:/Users/qw2/Desktop/Paddock_Power_GPS/home_range_geopackage_files/BIG_MUDGEE/Big_Mudgee_homerange_stats.csv'
results_tbl = open(output_csv, mode='w', newline='')
writer = csv.writer(results_tbl)
writer.writerow(['Paddock',
                'Year',
                'Month',
                'Cibo_Layer',
                'All_Pdk_Med',
                'All_Pdk_Min',
                'All_Pdk_Max',
                '50%_Homerange_Med',
                '50%_Homerange_Min',
                '50%_Homerange_Max',
                '75%_Homerange_Med',
                '75%_Homerange_Min',
                '75%_Homerange_Max',
                '95%_Homerange_Med',
                '95%_Homerange_Min',
                '95%_Homerange_Max'])

for file in os.scandir(homerange_source_folder):
    # Folder names end in '_gpkg'
    if file.name.split('_')[1] == 'gpkg':
        paddock = file.name.split('_')[0][:-4]
        folder_year = file.name.split('_')[0][-4:]
#        print(paddock, folder_year)
        subfolder = os.path.join(homerange_source_folder, file.name)
        file_dict = {}
        for file in os.scandir(subfolder):
            # These are actual geopackages
            if file.name.split('.')[1] == 'gpkg':
                f_name = file.name
                dt = get_file_date(f_name)
                file_dict[f_name]=dt
        sorted_gpkgs = sorted(file_dict.items(), key=lambda x:x[1])
        for i in sorted_gpkgs:
            # i is a tuple containing gpkg file name & its associated datetime
            file_name = i[0]
            paddock_and_month = file_name.split('.')[0]
            file_date = str(i[1])
            yr = file_date.split('-')[0]
            mnth = file_date.split('-')[1]
            yr_and_month = f'{yr}{mnth}'
            homerange_path = os.path.join(subfolder, file_name)
            homerange_lyr = QgsVectorLayer(f'{homerange_path}|layername=homerange', f'{paddock_and_month}_{yr}', 'ogr')
            paddock_lyr = QgsVectorLayer(f'{homerange_path}|layername=paddock', f'{paddock_and_month}_{yr}', 'ogr')
            tc_path = tc_file_path(yr_and_month)
#            print(f'TC path: {tc_path}')
            if tc_path is not None:
                tc_lyr = QgsRasterLayer(tc_path, f'Cibo_TC_{yr}{mnth}', 'gdal')
                tc_stats = calculate_raster_stats(paddock_lyr, homerange_lyr, tc_lyr)
#                print(tc_stats)
                writer.writerow([paddock,
                                yr,
                                mnth,
                                'TC',
                                tc_stats['Entire_paddock'][0],
                                tc_stats['Entire_paddock'][1],
                                tc_stats['Entire_paddock'][2],
                                tc_stats['50_pcnt_homerange'][0],
                                tc_stats['50_pcnt_homerange'][1],
                                tc_stats['50_pcnt_homerange'][2],
                                tc_stats['75_pcnt_homerange'][0],
                                tc_stats['75_pcnt_homerange'][1],
                                tc_stats['75_pcnt_homerange'][2],
                                tc_stats['95_pcnt_homerange'][0],
                                tc_stats['95_pcnt_homerange'][1],
                                tc_stats['95_pcnt_homerange'][2]])
            tsdm_path = tsdm_file_path(yr_and_month)
#            print(f'TSDM path: {tsdm_path}')
            if tsdm_path is not None:
                tsdm_lyr = QgsRasterLayer(tsdm_path, f'Cibo_TSDM_{yr}{mnth}', 'gdal')
                tsdm_stats = calculate_raster_stats(paddock_lyr, homerange_lyr, tsdm_lyr)
#                print(tsdm_stats)
                writer.writerow([paddock,
                                yr,
                                mnth,
                                'TSDM',
                                tsdm_stats['Entire_paddock'][0],
                                tsdm_stats['Entire_paddock'][1],
                                tsdm_stats['Entire_paddock'][2],
                                tsdm_stats['50_pcnt_homerange'][0],
                                tsdm_stats['50_pcnt_homerange'][1],
                                tsdm_stats['50_pcnt_homerange'][2],
                                tsdm_stats['75_pcnt_homerange'][0],
                                tsdm_stats['75_pcnt_homerange'][1],
                                tsdm_stats['75_pcnt_homerange'][2],
                                tsdm_stats['95_pcnt_homerange'][0],
                                tsdm_stats['95_pcnt_homerange'][1],
                                tsdm_stats['95_pcnt_homerange'][2]])

results_tbl.close()
print('Done')
