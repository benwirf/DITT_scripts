from osgeo import gdal

lyr = QgsProject.instance().mapLayersByName('No_1_PDK')[0]

path = lyr.source()

ds = gdal.Open(path)

arr = ds.ReadAsArray()

pixel_x_size = ds.GetGeoTransform()[1]
pixel_y_size = ds.GetGeoTransform()[5]
pixel_area = pixel_x_size * -pixel_y_size
#print(pixel_x_size)
#print(-pixel_y_size)
#print(pixel_area)

#total_count = np.shape(arr)[0]*np.shape(arr)[1]
#print(total_count)
b1 = ds.GetRasterBand(1)

min_val = b1.GetMinimum()
max_val = b1.GetMaximum()
max_dist = math.ceil(max_val/500.0)*500.0

print(min_val)
print(max_val)
print(max_dist)

no_classes = int(max_dist/500)

print(no_classes)

class_min = min_val
step = 500

all_areas = []

for i in range(no_classes):
    class_max = class_min + step
    class_count = ((arr > class_min)&(arr <= class_max)).sum()
    class_area = class_count*pixel_area
    all_areas.append(class_area)
    print(f'Paddock area between {int(class_min)}m and {int(class_max)}m from water: {round(class_area/10000, 2)}ha')
    class_min+=step

total_area = sum(all_areas)

print(round(total_area, 2))
