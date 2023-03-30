# PCReDive_Maho
Princess Connect Discord Bot  
Discord 公主連結報刀機器人   
  
此機器人為報刀機器人，可支援同一DC群多戰隊同時使用。  
權限由高而低主要區分為四者:管理員、戰隊隊長、控刀手、一般成員，  
各自擁有不同的指令可以使用。  
  
指令全方面支援全形半形繁體/簡體/英文，亦有斜線指令可供使用。  
此外，英文縮寫對照表可於[Wiki常見問題](https://github.com/dkalke/PCReDive_Maho/wiki/5.-%E5%B8%B8%E8%A6%8B%E5%95%8F%E9%A1%8C)中查詢。

　    
邀請連結 : https://discord.com/oauth2/authorize?client_id=806421470368104449&scope=bot  
  
使用說明 : https://github.com/dkalke/PCReDive_Maho/wiki  
更新紀錄 : https://github.com/dkalke/PCReDive_Maho/wiki/4.-%E6%9B%B4%E6%96%B0%E6%AD%B7%E5%8F%B2  
TOPGG :  https://top.gg/bot/806421470368104449

如果需要自行部屬，請參考以下章節。
　  
　  
   　  

## 特別感謝
[Fredrick9122](https://github.com/Fredrick9122) : 協助code編寫  
[hsuCasper](https://github.com/hsuCasper) : 協助撰寫說明文件  
[yungpingxu](https://github.com/YungPingXu) : [手動軸時移功能](https://github.com/YungPingXu/pcr-bot)  
[IanDesuyo](https://github.com/IanDesuyo) : [補償計算功能](https://github.com/IanDesuyo/AIKyaru/blob/6ffdb105f44aa6dd0822ff9393ba706131393010/cogs/clan/cbre.py)
　      
　    
## 部屬須知
### 環境
- python 3.9 (mudule list in requirement.txt)
- MariaDB 10.5.15
可利用[script](https://github.com/dkalke/PCReDive_Maho/blob/master/PCReDive_Maho/init-files/priceseDB.sql)產生依賴資料表
　    
     

### 設定啟動參數
修改[env](https://github.com/dkalke/PCReDive_Maho/blob/master/PCReDive_Maho/init-files/.env)內部參數，並置於PCReDive_Maho目錄下。
- SQLHOST : MariaDB ip位址
- SQLPORT : MariaDB 連接埠
- SQLDB : MariaDB 資料庫名稱
- SQLID : MariaDB 使用者名稱
- SQLPW : MariaDB 使用者密碼
- TOPGG_TOKEN : [top.gg](https://top.gg/)申請token填入
- TOKEN : [discord](https://discord.com/developers/applications)申請token填入

最終目錄必備結構如下  
PCReDive_Maho/  
├── .env   
├── Event  
├── Module  
└── PCReDive_Maho.py  

### 執行
python3 PCReDive_Maho.py  
