import Module.Kernel.define_value
import Module.Kernel.week_stage
def AutoOffset(connection, server_id, group_serial):  
  # 一階段:1~3周
  # 二階段:4~10周
  # 三階段:11~30周
  # 四階段:31~40周
  # 五階段:41周~

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

    # 目前的最大可視範圍
    week_offset = level_offset[Module.Kernel.week_stage.week_stage(now_week)]

    temp = now_week + week_offset
    ans.append(temp)  # 自身最大可視範圍
    if temp > Module.Kernel.define_value.Stage.two.value and Module.Kernel.define_value.Stage.two.value > now_week :
      ans.append(Module.Kernel.define_value.Stage.two.value + level_offset[1]) # 以第一階段為基準的最大可視範圍
    if temp > Module.Kernel.define_value.Stage.three.value and Module.Kernel.define_value.Stage.three.value > now_week :
      ans.append(Module.Kernel.define_value.Stage.three.value + level_offset[2]) # 以第二階段為基準的最大可視範圍
    if temp > Module.Kernel.define_value.Stage.four.value and Module.Kernel.define_value.Stage.four.value > now_week :
      ans.append(Module.Kernel.define_value.Stage.four.value + level_offset[3]) # 以第三階段為基準的最大可視範圍
    if temp > Module.Kernel.define_value.Stage.five.value and Module.Kernel.define_value.Stage.five.value > now_week :
      ans.append(Module.Kernel.define_value.Stage.five.value + level_offset[4]) # 以第四階段為基準的最大可視範圍
    week_offset = min(ans) - now_week

    cursor = connection.cursor(prepared=True)
    sql = "UPDATE princess_connect.group SET week_offset=? WHERE server_id = ? and group_serial = ?"
    data = (week_offset, server_id, group_serial)
    cursor.execute(sql, data)
    cursor.close
    connection.commit()
  else:
    raise NO_DATA("autooffset找不到戰隊資料")