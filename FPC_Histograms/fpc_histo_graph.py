from osgeo import gdal
import numpy as np
import matplotlib.pyplot as plt

raster_path = 'Mulga_Park_FPC/marys_fcp.tif'

ds = gdal.Open(raster_path, gdal.GA_ReadOnly)

arr = ds.ReadAsArray()

unique_values = np.unique(arr)

plot_values = []
value_counts = []

for i in unique_values:
    if i == -9999.0:
        continue
    plot_values.append(i)
    val_count = (arr == i).sum()
    value_counts.append(val_count)
    #print(f'{str(round(i, 8))}: {val_count}')
    
plt.plot(plot_values, value_counts, label='FPC Value Distribution', color='blue', linewidth=3)

plt.title("Mary's Paddock 5km Watered Area FPC Histogram")
plt.legend(fontsize=10)
plt.xlabel("FPC Values")
plt.ylabel("Value Count")
plt.xticks(np.arange(0, 30, step=5), fontsize=6, rotation=90)
plt.yticks(np.arange(0, 30000, step=5000), fontsize=12)
#plt.yticks(np.arange(0, 11000, step=2000), fontsize=12)
plt.gca().yaxis.grid(linestyle='dashed')

#plt.show()

#plt.gcf().set_size_inches(10, 7)
plt.savefig('Mulga_Park_FPC/OUTPUT/marys_fpc_hist.png', bbox_inches='tight')
plt.cla()
    
print('Done')
