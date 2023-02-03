from osgeo import gdal
import numpy as np

lyr = QgsProject.instance().mapLayersByName('202206.12months.growth.tot.nt')[0]

path = lyr.source()

ds = gdal.Open(path)

arr = ds.ReadAsArray()

#total_count = np.shape(arr)[0]*np.shape(arr)[1]
#print(total_count)

class1_count = ((arr > 0)&(arr <= 1000)).sum()
class2_count = ((arr > 1000)&(arr <= 2000)).sum()
class3_count = ((arr > 2000)&(arr <= 3000)).sum()
class4_count = (arr > 3000).sum()
no_data_count = (arr == 0).sum()

#print(class1_count)
print(f'0-1000: {class1_count}')
#print(class2_count)
print(f'1000-2000: {class2_count}')
#print(class3_count)
print(f'2000-3000: {class3_count}')
#print(class4_count)
print(f'>3000: {class4_count}')
#print(no_data_count)
print(f'No Data: {no_data_count}')

total_pixel_count = sum([class1_count, class2_count, class3_count, class4_count, no_data_count])
total_pixel_count_greater_than_zero = sum([class1_count, class2_count, class3_count, class4_count])

print(f'Total pixels: {total_pixel_count}')
print(f'Total pixels excluding no data: {total_pixel_count_greater_than_zero}')


