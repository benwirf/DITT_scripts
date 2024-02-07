from datetime import datetime

date_string = '2023/05/10'

time_string = '2023-05-10 05:56:30Z'

dtt = datetime.strptime(time_string, '%Y-%m-%d %H:%M:%SZ')
print(dtt.date())

dtd = datetime.strptime(date_string, '%Y/%m/%d')
print(dtd.date())

