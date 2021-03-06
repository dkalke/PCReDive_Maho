#!tr [秒數]
#[刀軸]
# 刀表調整器
# author: YungPingXu
# source: https://github.com/YungPingXu/pcr-bot/blob/main/code.py

# this version is modified by: dkalke

import re
import datetime


def checktime(number): # 檢查是不是合法的時間
  return (number >= 0 and number <= 130) and \
          ((number // 100 == 0 and number % 100 <= 59 and number % 100 >= 0) or \
          (number // 100 == 1 and number % 100 <= 30 and number % 100 >= 0))


def transform_time(original_time): # 轉換秒數
  result = ""
  if original_time < 60:
      if original_time < 10:
          result += "00" + str(original_time)
      else:
          result += "0" + str(original_time)
  else:
      if 60 <= original_time < 70:
          result += str(original_time // 60) + "0" + str(original_time % 60)
      else:
          result += str(original_time // 60) + str(original_time % 60)
  return result


async def timeline_shifter(send_obj, content):
  tr = re.match(r"\s*\!tr\s*(\d+)\s*\n([\s\S]+)", content)
  if tr:
      time = int(tr.group(1))
      if 1 <= time <= 90:
          lines = tr.group(2).split("\n")
          resultline = ""
          for line in lines:
              tmp = ""
              for c in line: # 全形轉半形
                  if c in ("，", "、", "。"):
                      tmp += c
                  elif 65281 <= ord(c) <= 65374:
                      tmp += chr(ord(c) - 65248)
                  elif ord(c) == 12288: # 空格字元
                      tmp += chr(32)
                  else:
                      tmp += c
              filter = tmp.replace(":", "").replace("\t", "") # 過濾特殊字元
              match = re.match(r'(\D*)(\d{2,3})((\s*[~-]\s*)(\d{2,3}))?(.*)?', filter) # 擷取時間
              if match:
                  content1 = match.group(1) # 時間前面的文字
                  timerange = match.group(3) # 056~057 這種有範圍的時間
                  time1 = int(match.group(2)) # 有範圍的時間 其中的第一個時間
                  time2 = 0
                  if timerange is not None and match.group(5) is not None:
                      time2 = int(match.group(5)) # 有範圍的時間 其中的第二個時間
                  rangecontent = match.group(4) # 第一個時間和第二個時間中間的字串
                  content2 = match.group(6) # 時間後面的文字
                  if checktime(time1) and ((timerange is None and match.group(5) is None) or (timerange is not None and match.group(5) is not None and checktime(time2))):
                      totaltime1 = time1 % 100 + (time1 // 100) * 60 # time1的秒數
                      newtime1 = totaltime1 - (90 - time)
                      result = ""
                      if newtime1 < 0: # 如果時間到了 後續的就不要轉換
                          continue # 迴圈跳到下一個
                      if match.group(5) is None:
                          result = content1 + transform_time(newtime1) + content2
                      else:
                          totaltime2 = time2 % 100 + time2 // 100 * 60 # time2的秒數
                          newtime2 = totaltime2 - (90 - time)
                          result = content1 + transform_time(newtime1) + rangecontent + transform_time(newtime2) + content2
                      resultline += result
                  else:
                      resultline += tmp
              else:
                  resultline += tmp
              resultline += "\n"
          await send_obj.send(resultline)
      else:
          await send_obj.send("您輸入的補償秒數錯誤，秒數必須要在 1～90 之間！")
  else:
      await send_obj.send("您輸入的秒數格式錯誤！正確的格式為\n!tr 補償秒數\n文字軸\n\n(補償秒數後面請直接換行，不要有其他字元)")
  