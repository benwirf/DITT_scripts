lyr = iface.activeLayer()
# pr = lyr.dataProvider()
# # print(dir(pr))
# print(pr.subLayers()[0].split(pr.sublayerSeparator()))
##########################################################

from osgeo import ogr

gpkg_uri = lyr.source().split('|')[0]
print(gpkg_uri)
sub_lyrs = [l.GetName() for l in ogr.Open(gpkg_uri)]
for n in sub_lyrs:
    print(n)