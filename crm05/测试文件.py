


import datetime

now_time = datetime.datetime.now().date()
print(now_time)
print(datetime.timedelta(days=15))
deadline_time = now_time - datetime.timedelta(days=15)
print(deadline_time)