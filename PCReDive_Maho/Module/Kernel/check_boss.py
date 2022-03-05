def Check_boss(now_week, week, boss): # (now_week, week_offset), week, boss
  if boss > 0 and boss < 6 :  
    # 檢查當前的該王的討伐狀況(週目)
    # 要報的週目>=該王週目才能報
    if week >= now_week[boss-1]:
      return True
    else:
      return False
  else:
    return False