def AutoOffset(connection, server_id, group_serial):  
  # 一階段:1~3周
  # 二階段:4~10周
  # 三階段:11~34周
  # 四階段:35~44周
  # 五階段:45周~

  cursor = connection.cursor(prepared=True)
  sql = "SELECT now_week, week_offset, week_offset_1, week_offset_2, week_offset_3, week_offset_4, week_offset_5 FROM princess_connect.group WHERE server_id = ? and group_serial = ? limit 0, 1"
  data = (server_id, group_serial)
  cursor.execute(sql, data)
  row = cursor.fetchone()
  cursor.close
  if row:
    # 列舉所有階段的最大可能值，動態調整。
    ans = list()
    now_week = row[0]
    week_offset = row[1]
    level_offset = [row[2], row[3], row[4], row[5], row[6]]
    week_threshold = [1,4,11,35,45]

    # 目前的最大可視範圍
    if week_threshold[0] <= now_week and now_week < week_threshold[1]:
      week_offset = level_offset[0]
    elif week_threshold[1] <= now_week and now_week < week_threshold[2]:
      week_offset = level_offset[1]
    elif week_threshold[2] <= now_week and now_week < week_threshold[3]:
      week_offset = level_offset[2]
    elif week_threshold[3] <= now_week and now_week < week_threshold[4]:
      week_offset = level_offset[3]
    elif week_threshold[4] <= now_week:
      week_offset = level_offset[4]

    temp = now_week + week_offset
    ans.append(temp)  # 自身最大可視範圍
    if temp > week_threshold[1] and week_threshold[1] > now_week :
      ans.append(week_threshold[1] + level_offset[1]) # 以第一階段為基準的最大可視範圍
    if temp > week_threshold[2] and week_threshold[2] > now_week :
      ans.append(week_threshold[2] + level_offset[2]) # 以第二階段為基準的最大可視範圍
    if temp > week_threshold[3] and week_threshold[3] > now_week :
      ans.append(week_threshold[3] + level_offset[3]) # 以第三階段為基準的最大可視範圍
    if temp > week_threshold[4] and week_threshold[4] > now_week :
      ans.append(week_threshold[4] + level_offset[4]) # 以第四階段為基準的最大可視範圍
    week_offset = min(ans) - now_week

    cursor = connection.cursor(prepared=True)
    sql = "UPDATE princess_connect.group SET week_offset=? WHERE server_id = ? and group_serial = ?"
    data = (week_offset, server_id, group_serial)
    cursor.execute(sql, data)
    cursor.close
    connection.commit()
  else:
    raise NO_DATA("autooffset找不到戰隊資料")