from osgeo import gdal
import numpy as np
import csv

# Create output csv
csv_path = 'Mulga_Park_FPC/OUTPUT/brices_fpc_hist.csv'
csv_file = open(csv_path, mode='w', newline='')
writer = csv.writer(csv_file)

writer.writerow(['FPC_VALUE', 'COUNT'])

raster_path = 'Mulga_Park_FPC/brices_fcp.tif'

ds = gdal.Open(raster_path, gdal.GA_ReadOnly)

arr = ds.ReadAsArray()

unique_values = np.unique(arr)

for i in unique_values:
    if i == -9999.0:
        continue
    val_count = (arr == i).sum()
    print(f'{str(round(i, 8))}: {val_count}')
    writer.writerow([str(round(i, 8)), str(val_count)])
    
csv_file.close()
del writer
print('Done')
