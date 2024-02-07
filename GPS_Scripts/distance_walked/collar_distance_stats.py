import statistics

lyr = QgsProject.instance().mapLayersByName('Daily_Tracks_Conkerberry_1106')[0]

daily_distances = [ft['Distance'] for ft in lyr.getFeatures()]

max_dist = max(daily_distances)
min_dist = min(daily_distances)
mean_dist = statistics.mean(daily_distances)

print(f'Maximum daily distance walked: {max_dist} km')
print(f'Minimum daily distance walked: {min_dist} km')
print(f'Average daily distance walked: {round(mean_dist, 3)} km')
