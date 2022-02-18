import datetime
def get_closest_end_time(in_time: datetime) -> datetime:
  if in_time.hour >= 5:
    in_time = in_time + datetime.timedelta(days = 1)
  return datetime.datetime(in_time.year,in_time.month,in_time.day,5)