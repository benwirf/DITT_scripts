from osgeo import gdal
import numpy as np
import statistics

lyr = QgsProject.instance().mapLayersByName('Roper-06months')[0]

path = lyr.source()

ds = gdal.Open(path)

arr = ds.ReadAsArray()

valid_pixels = (arr > 0)&(arr <= 100)

nodata = (arr == -999).sum()
data = (arr != -999).sum()

pixels_to_calc = []

for i in arr:
    for j in i:
        if j != -999:
            pixels_to_calc.append(j)
            
total = len(pixels_to_calc)
ras_min = min(pixels_to_calc)
ras_max = max(pixels_to_calc)
ras_mean = statistics.mean(pixels_to_calc)
ras_median = statistics.median(pixels_to_calc)

print(f'Min: {ras_min}\nMax: {ras_max}\nMean: {ras_mean}\nMedian: {ras_median}')