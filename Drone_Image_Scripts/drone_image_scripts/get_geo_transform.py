from osgeo import gdal, osr

# Define input and output file paths
in_path = 'C:\\Users\\qw2\\Desktop\\Drone\\Beatrice\\ODM_Results\\subset_2_results\\Middle-Point-19-05-2023-orthophoto.tif'

raster = gdal.Open(in_path)

# Get input raster bands
input_bands = [raster.GetRasterBand(i+1) for i in range(raster.RasterCount)]

# Get input raster data type
data_type = input_bands[0].DataType

# Create list of bands read into arrays
band_arrays = [band.ReadAsArray() for band in input_bands]

geotransform = raster.GetGeoTransform()
originX = geotransform[0]
originY = geotransform[3]
pixelWidth = geotransform[1]
pixelHeight = geotransform[5]
cols = raster.RasterXSize
rows = raster.RasterYSize

#print(geotransform)

print(f'Top Left X: {originX}\n',
    f'Top Left Y: {originY}\n',
    f'Pixel Width: {pixelWidth}\n',
    f'Pixel Height: {pixelHeight}\n',
    f'Columns: {cols}\n',
    f'Rows: {rows}')