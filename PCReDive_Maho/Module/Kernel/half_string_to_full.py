# 半形轉全形
def half_string_to_full(s):
  rstring = ""
  for uchar in s:
      u_code = ord(uchar)
      if u_code == 32:  # 全形空格直接轉換
          u_code = 12288
      elif 33 <= u_code <= 126:  # 全形字元（除空格）根據關係轉化
          u_code += 65248
      rstring += chr(u_code)
  return rstring
