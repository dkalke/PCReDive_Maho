# 全形轉半形
def full_string_to_half_and_lower(s):
  rstring = ""
  for uchar in s:
      u_code = ord(uchar)
      if u_code == 12288:  # 全形空格直接轉換
          u_code = 32
      elif 65281 <= u_code <= 65374:  # 全形字元（除空格）根據關係轉化
          u_code -= 65248
      rstring += chr(u_code)
  return rstring.lower() # 小寫轉換
