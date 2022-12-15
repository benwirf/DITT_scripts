import os

layers = iface.layerTreeView().selectedLayers()

pipe = QgsRasterPipe()
project = QgsProject().instance()

for layer in layers:
#    file_name = os.path.join('P:\\VSS_SHARE\\01_PROJECTS\\IMAGERY\\AIM_POINTS\\MATERIAL\\ELLSWORTH_REQUEST\\DEV', f'{layer.name()}.tif')
    file_name = os.path.join('C:\\Users\\qw2\\Desktop\\test', f'{layer.name()}_rendered.tif')
    pipe.set(layer.dataProvider().clone())
    pipe.set(layer.renderer().clone())
    file_writer = QgsRasterFileWriter(file_name)
    file_writer.mMode=QgsRasterFileWriter.Image
    file_writer.writeRaster(pipe,
                           layer.width(),
                           layer.height(),
                           layer.extent(),
                           layer.crs(),
                           project.transformContext())