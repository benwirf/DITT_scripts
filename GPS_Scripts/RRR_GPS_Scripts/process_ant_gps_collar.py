import os

src_dir = r'R:\LID\Common-KRS\Sustainable_Pastoral_Development\Research\2022_RainReadyRangelands_CP_RC\PROJECT-Research\BARKLY\Anthonys Cattle Data\GPS ANT 23_24 wet season'
src_file = 'No5West_Anthonys_RRR_1212.csv'
tgt_dir = r'C:\Users\qw2\Desktop\Ant_GPS_Collars'

def process_collar(input_dir, file_name, output_dir):

    pdk_lyr = QgsProject.instance().mapLayersByName('Trial_Pdks')[0]

    pdk_map = {'No4': 'No. 4',
                'No5East': 'No. 5 East',
                'No5West': 'No. 5 West'}

    wpt_lyr = QgsProject.instance().mapLayersByName('ANT_waters_plus_waterholes')[0]
    #print(file_name)
    output_prefix = file_name.split(".")[0]
    collar_no = output_prefix.split('_')[3]
    #print(collar_no)
    output_folder_name = f'{output_prefix}_Output'
    output_folder_path = os.path.join(output_dir, output_folder_name)
    if not os.path.exists(output_folder_path):
        os.mkdir(output_folder_path)
    dtw_gpkg = f'{output_prefix}.gpkg'
    dtw_gpkg_path = os.path.join(output_folder_path, dtw_gpkg)
    
    pdk_name = file_name.split('_')[0]
    pdk_ft_name = pdk_map[pdk_name]
    
    id_list = [ft.id() for ft in pdk_lyr.getFeatures() if ft['NAME'] == pdk_ft_name]
    ft_req = QgsFeatureRequest(id_list)
    filtered_pdk_lyr = pdk_lyr.materialize(ft_req)
    
    pdk_waterpoints = processing.run("native:clip",
                                    {'INPUT':wpt_lyr,
                                    'OVERLAY':filtered_pdk_lyr,
                                    'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']
                                    
    pdk_buff = processing.run("native:buffer",
                                {'INPUT':filtered_pdk_lyr,
                                'DISTANCE':100,
                                'SEGMENTS':25,
                                'END_CAP_STYLE':0,
                                'JOIN_STYLE':0,
                                'MITER_LIMIT':2,
                                'DISSOLVE':True,
                                'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']
    csv_path = os.path.join(input_dir, file_name)
    uri = f'file:///{csv_path}?type=csv&maxFields=10000&detectTypes=yes&xField=Longitude&yField=Latitude&crs=EPSG:4326&spatialIndex=no&subsetIndex=no&watchFile=no'
    csv_lyr = QgsVectorLayer(uri, 'Collar_CSV', 'delimitedtext')
    if not csv_lyr.isValid():
        print('CSV layer is not valid!')
        return
    #QgsProject.instance().addMapLayer(csv_lyr)

    csv_clipped = processing.run("native:clip",
                                    {'INPUT':csv_lyr,
                                    'OVERLAY':pdk_buff,
                                    'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']
    print('CSV clipped')
    
    # Add QDateTime field
    add_dt_params = {'INPUT':csv_clipped,
                    'DATE_FIELD':'Time',
                    'DATE_STRING_FORMAT':'="%Y-%m-%d %H:%M:%SZ"',
                    'TIME_FIELD':'Time',
                    'TIME_STRING_FORMAT':'="%Y-%m-%d %H:%M:%SZ"',
                    'OUTPUT':'TEMPORARY_OUTPUT'}
                    
    dt_added = processing.run("ditt-lid:adddatetimefield", add_dt_params)['OUTPUT']
    print('QDateTime field added')
    
    # Add a separate Date field (for Excel)
    src_flds = [fld for fld in dt_added.fields()]
    new_flds = src_flds[:2]
    new_flds.append(QgsField('Date', QVariant.Date))
    for fld in [fld for fld in src_flds[2:]]:
        new_flds.append(fld)
    #print(new_flds)
    temp_lyr = QgsVectorLayer('Point?crs=epsg:4326', 'TEST', 'memory')
    temp_lyr.dataProvider().addAttributes(new_flds)
    temp_lyr.updateFields()
    for ft in dt_added.getFeatures():
        atts = ft.attributes()
        atts.insert(2, ft['q_datetime'].date())
        feat = QgsFeature(temp_lyr.fields())
        feat.setGeometry(ft.geometry())
        feat.setAttributes(atts)
        temp_lyr.dataProvider().addFeature(feat)
    print('Date field added')
    
    # Add distance to water attribute
    add_dtw_params = {'INPUT':temp_lyr,
                        'SOURCE_FIELDS':[fld.name() for fld in temp_lyr.fields()],
                        'WATERPOINTS':pdk_waterpoints,
                        'WP_TYPE_FIELD':'type',
                        'WP_NAME_FIELD':'name',
                        'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:9473'),
                        'OUTPUT':dtw_gpkg_path}
                        
    dtw_added = processing.run("ditt-lid:adddist2water", add_dtw_params)['OUTPUT']
    print('Distance to water added')
    
    #Save GeoPackage as spreadsheets
    output_xlsx = os.path.join(output_folder_path, f'{output_prefix}.xlsx')
    save2xlsx_params = {'LAYERS':[dtw_gpkg_path],#File path string
                        'USE_ALIAS':False,
                        'FORMATTED_VALUES':False,
                        'OUTPUT':output_xlsx,
                        'OVERWRITE':False}
    processing.run("native:exporttospreadsheet", save2xlsx_params)
    print('DTW gpkg saved to spreadsheet')
    
    tracks_gpkg = f'{pdk_name}_{collar_no}_daily_tracks.gpkg'
    tracks_gpkg_path = os.path.join(output_folder_path, tracks_gpkg)
    
    tracks_xlsx = f'{pdk_name}_{collar_no}_daily_tracks.xlsx'
    tracks_xlsx_path = os.path.join(output_folder_path, tracks_xlsx)
    
    daily_movement_params = {'INPUT':dtw_gpkg_path,
                            'PADDOCK_NAME':pdk_ft_name,
                            'COLLAR_ID':collar_no,
                            'DATETIME_FIELD':'q_datetime',
                            'OUTPUT':tracks_gpkg_path,
                            'OUTPUT_CRS':QgsCoordinateReferenceSystem('EPSG:9473'),
                            'OUTPUT_XL':tracks_xlsx_path}
    processing.run("ditt-lid:dailymovementstats", daily_movement_params)
    print(f'{collar_no} Done')
    
process_collar(src_dir, src_file, tgt_dir)