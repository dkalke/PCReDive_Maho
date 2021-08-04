# PCReDive_Maho
Princess Connect Discord Bot  
Discord 公主連結報刀機器人

## 機器人邀請連結
邀請即用  
https://discord.com/oauth2/authorize?client_id=806421470368104449&scope=bot


## 部屬
### 環境
- python 3.6.9
  - mysql-connector-python (8.0.24)
  - discord.py (1.7.3)
  - discord-py-slash-command (2.3.1)
  - dblpy (0.4.0)
- MariaDB 10.1.48  
可利用[script](https://github.com/dkalke/PCReDive_Maho/blob/9f609367341f8e8b3edda1c375be4c6298fcb112/init/priceseDB.sql)產生依賴資料表

### 設定啟動參數
修改[env](https://github.com/dkalke/PCReDive_Maho/blob/9f609367341f8e8b3edda1c375be4c6298fcb112/init/.env)內部參數，並置於PCReDive_Maho目錄下。
- SQLHOST  
  MariaDB ip位址
- SQLPORT  
  MariaDB 連接埠
- SQLDB  
  MariaDB 資料庫名稱
- SQLID  
  MariaDB 使用者名稱
- SQLPW  
  MariaDB 使用者密碼
- TOPGG_TOKEN  
  [top.gg](https://top.gg/)申請token填入
- TOKEN  
  [discord](https://discord.com/developers/applications)申請token填入

最終目錄結構如下  
PCReDive_Maho/  
├── .env  
├── Discord_client.py  
├── Event  
├── Module  
├── Name_manager.py  
├── PCReDive_Maho.py  
├── PCReDive_Maho.pyproj  
└── TopGG.py  

### 執行
cd PCReDive_Maho  
python3 PCReDive_Maho.py  


## 外部連結
- [使用者說明書](https://hackmd.io/7xSl9FBESkqW20sAv0SHPA)  
- [TOPGG](https://top.gg/bot/806421470368104449)
