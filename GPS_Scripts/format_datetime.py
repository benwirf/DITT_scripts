from datetime import datetime

dt_txt = '2020/08/25 21:53:00'

dt = datetime.strptime(dt_txt, '%Y/%m/%d %H:%M:%S')

print(QDateTime(dt))