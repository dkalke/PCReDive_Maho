def Check_week(group_progress, week): # (now_week,now_boss,week_offset), week
  if week >= group_progress[0] and week <= group_progress[0] + group_progress[2]: # ÀË¬d¶g¥Ø
    return True
  else:
    return False