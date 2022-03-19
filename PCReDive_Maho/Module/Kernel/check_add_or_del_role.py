async def check_add_or_del_role(send_obj, cursor, server_id, group_serial, member_id, base_date, fighting_role_id):
  # 檢查該成員(包含分身)的剩餘刀數，若為0則移除身分組，反之則增加身分組
  member = send_obj.author.guild.get_member(member_id)
  if member:
    if fighting_role_id:
      role = send_obj.guild.get_role(fighting_role_id)
      if role:
        # 取得總刀數
        sql = "SELECT SUM(IFNULL(b.normal, 3)), SUM(IFNULL(b.reserved, 0)) FROM members a\
                LEFT JOIN knife_summary b ON a.serial_number = b.serial_number AND day = ?\
                WHERE server_id = ? AND group_serial = ? AND member_id = ? \
                GROUP BY member_id"
        data = (base_date, server_id, group_serial, member_id)
        cursor.execute(sql, data)
        row = cursor.fetchone()
        if row:
          if int(row[0]) == 0 and int(row[1]) == 0: # 移除出刀中身份組
            await member.remove_roles(role)
          else:
            await member.add_roles(role)  # 加入出刀中身份組
  