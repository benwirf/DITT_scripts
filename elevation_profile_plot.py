import matplotlib.pyplot as plt

line_lyr = QgsProject.instance().mapLayersByName('New scratch layer')[0]
rl = QgsProject.instance().mapLayersByName('S17E130')[0]

line_geom = [f.geometry() for f in line_lyr.getFeatures()][0]

line_length = line_geom.length()

num_profile_pts = 25

interp_dist = line_length/num_profile_pts

total_dist = interp_dist

sample_geoms = []

while total_dist < line_length:
    sample_geoms.append(line_geom.interpolate(total_dist))
    total_dist+=interp_dist
    
#print(sample_pts)

plot_vals = [rl.dataProvider().sample(geom.asPoint(), 1)[0] for geom in sample_geoms]

print(plot_vals)

