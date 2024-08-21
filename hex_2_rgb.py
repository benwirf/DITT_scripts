
hex_code = '#645c2a'

hex_col = QColor(hex_code)
rgb_col = hex_col.rgba64()
r_val = rgb_col.red8()
g_val = rgb_col.green8()
b_val = rgb_col.blue8()

print(f'{r_val}, {g_val}, {b_val}')