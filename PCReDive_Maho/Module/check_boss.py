def Check_boss(group_progress, week, boss): # (now_week,now_boss,week_offset), week, boss
  if boss > 0 and boss < 6 :  
    if week == group_progress[0] and boss < group_progress[1]:
      return False
    else:
      return True
  else:
    return False