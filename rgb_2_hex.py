
rgb = '228, 218, 170'

r = rgb.split(',')[0].strip()
g = rgb.split(',')[1].strip()
b = rgb.split(',')[2].strip()

rgb_col = QColor(int(r), int(g), int(b))

hex_col = rgb_col.name()

print(hex_col)