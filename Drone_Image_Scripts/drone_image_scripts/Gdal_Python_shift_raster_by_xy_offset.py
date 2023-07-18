from osgeo import gdal, osr

# Define input and output file paths
in_path = 'C:\\Users\\qw2\\Desktop\\Drone\\Beatrice\\ODM_Results\\subset_2_results\\Middle-Point-19-05-2023-2-orthophoto.tif'
out_path = 'C:\\Users\\qw2\\Desktop\\Drone\\Beatrice\\ODM_Results\\Middle-Point-orthophoto-2_shifted.tif'

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

# Define desired X and Y offsets in input raster Spatial Reference System (SRS) units...
# ...using a meter-based SRS e.g. an appropriate UTM 
x_offset = 0.7710161834256724
y_offset = 1.2068079374730587

driver = gdal.GetDriverByName('GTiff')
outRaster = driver.Create(out_path, cols, rows, len(input_bands), data_type)
outRaster.SetGeoTransform((originX+x_offset, pixelWidth, 0, originY+y_offset, 0, pixelHeight))

# Write array from each input band to each output band
for index, array in enumerate(band_arrays):
    outband = outRaster.GetRasterBand(index+1)
    if outband:
        outband.WriteArray(array)
        outband.FlushCache()
    
outRasterSRS = osr.SpatialReference()
outRasterSRS.ImportFromWkt(raster.GetProjectionRef())
outRaster.SetProjection(outRasterSRS.ExportToWkt())

outRaster = None