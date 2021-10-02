def Check_week(group_progress, week): # (main_week,week_offset), week
  if week >= group_progress[0] and week <= group_progress[0] + group_progress[1]:
    return True
  else:
    return False