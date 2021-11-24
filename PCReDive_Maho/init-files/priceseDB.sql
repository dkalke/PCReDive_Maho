/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- 傾印 princess_connect 的資料庫結構
CREATE DATABASE IF NOT EXISTS `princess_connect` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;
USE `princess_connect`;

-- 傾印  資料表 princess_connect.group 結構
CREATE TABLE IF NOT EXISTS `group` (
  `server_id` bigint(20) unsigned NOT NULL DEFAULT 0,
  `group_serial` int(11) NOT NULL,
  `now_week` int(10) unsigned NOT NULL,
  `now_week_1` int(10) unsigned NOT NULL,
  `now_week_2` int(10) unsigned NOT NULL,
  `now_week_3` int(10) unsigned NOT NULL,
  `now_week_4` int(10) unsigned NOT NULL,
  `now_week_5` int(10) unsigned NOT NULL,
  `week_offset` tinyint(3) unsigned NOT NULL DEFAULT 0,
  `week_offset_1` tinyint(3) unsigned NOT NULL DEFAULT 10,
  `week_offset_2` tinyint(3) unsigned NOT NULL DEFAULT 5,
  `week_offset_3` tinyint(3) unsigned NOT NULL DEFAULT 3,
  `week_offset_4` tinyint(3) unsigned NOT NULL DEFAULT 3,
  `week_offset_5` tinyint(3) unsigned NOT NULL DEFAULT 1,
  `now_boss` int(10) unsigned NOT NULL,
  `table_channel_id` bigint(20) DEFAULT NULL,
  `sign_channel_id` bigint(20) DEFAULT NULL,
  `info_channel_id` bigint(20) DEFAULT NULL,
  `log_channel_id` bigint(20) DEFAULT NULL,
  `table_message_id` bigint(20) DEFAULT NULL,
  `knife_pool_message_id` bigint(20) DEFAULT NULL,
  `info_message_id` bigint(20) DEFAULT NULL,
  `controller_role_id` bigint(20) DEFAULT NULL,
  `boss_change` datetime NOT NULL DEFAULT current_timestamp(),
  `boss_change_1` datetime NOT NULL DEFAULT current_timestamp(),
  `boss_change_2` datetime NOT NULL DEFAULT current_timestamp(),
  `boss_change_3` datetime NOT NULL DEFAULT current_timestamp(),
  `boss_change_4` datetime NOT NULL DEFAULT current_timestamp(),
  `boss_change_5` datetime NOT NULL DEFAULT current_timestamp(),
  `table_style` tinyint(4) NOT NULL DEFAULT 0,
  `upload` tinyint(1) unsigned zerofill DEFAULT 0,
  `policy` int(10) unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`server_id`,`group_serial`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='設定檔';

-- 取消選取資料匯出。

-- 傾印  資料表 princess_connect.group_captain 結構
CREATE TABLE IF NOT EXISTS `group_captain` (
  `server_id` bigint(20) unsigned NOT NULL DEFAULT 0,
  `group_serial` int(10) unsigned NOT NULL DEFAULT 0,
  `member_id` bigint(20) unsigned NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='戰隊隊長';

-- 取消選取資料匯出。

-- 傾印  資料表 princess_connect.keep_knifes 結構
CREATE TABLE IF NOT EXISTS `keep_knifes` (
  `serial_number` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `server_id` bigint(20) unsigned NOT NULL DEFAULT 0,
  `group_serial` int(11) unsigned NOT NULL,
  `member_id` bigint(20) unsigned NOT NULL DEFAULT 0,
  `comment` varchar(150) NOT NULL DEFAULT '',
  PRIMARY KEY (`serial_number`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=309 DEFAULT CHARSET=utf8mb4;

-- 取消選取資料匯出。

-- 傾印  資料表 princess_connect.knifes 結構
CREATE TABLE IF NOT EXISTS `knifes` (
  `serial_number` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `server_id` bigint(20) unsigned NOT NULL DEFAULT 0,
  `group_serial` tinyint(4) unsigned NOT NULL,
  `member_id` bigint(20) unsigned NOT NULL DEFAULT 0,
  `week` tinyint(4) unsigned NOT NULL,
  `boss` tinyint(4) unsigned NOT NULL,
  `comment` varchar(150) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp(),
  `done_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `knife_type` tinyint(4) NOT NULL DEFAULT 0,
  `real_damage` int(10) unsigned NOT NULL DEFAULT 0,
  `estimated_damage` int(10) unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`serial_number`)
) ENGINE=InnoDB AUTO_INCREMENT=5412 DEFAULT CHARSET=utf8mb4 COMMENT='每刀資料';

-- 取消選取資料匯出。

-- 傾印  資料表 princess_connect.members 結構
CREATE TABLE IF NOT EXISTS `members` (
  `server_id` bigint(20) unsigned NOT NULL,
  `member_id` bigint(20) NOT NULL,
  `group_serial` bigint(20) unsigned NOT NULL,
  `knifes` tinyint(3) unsigned NOT NULL DEFAULT 0,
  `period` tinyint(3) unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`server_id`,`member_id`,`group_serial`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 取消選取資料匯出。

-- 傾印  資料表 princess_connect.month 結構
CREATE TABLE IF NOT EXISTS `month` (
  `day1` timestamp NULL DEFAULT NULL,
  `day2` timestamp NULL DEFAULT NULL,
  `day3` timestamp NULL DEFAULT NULL,
  `day4` timestamp NULL DEFAULT NULL,
  `day5` timestamp NULL DEFAULT NULL,
  `day6` timestamp NULL DEFAULT NULL,
  `boss1_s1` int(11) DEFAULT NULL,
  `boss1_s2` int(11) DEFAULT NULL,
  `boss1_s3` int(11) DEFAULT NULL,
  `boss1_s4` int(11) DEFAULT NULL,
  `boss1_s5` int(11) DEFAULT NULL,
  `boss2_s1` int(11) DEFAULT NULL,
  `boss2_s2` int(11) DEFAULT NULL,
  `boss2_s3` int(11) DEFAULT NULL,
  `boss2_s4` int(11) DEFAULT NULL,
  `boss2_s5` int(11) DEFAULT NULL,
  `boss3_s1` int(11) DEFAULT NULL,
  `boss3_s2` int(11) DEFAULT NULL,
  `boss3_s3` int(11) DEFAULT NULL,
  `boss3_s4` int(11) DEFAULT NULL,
  `boss3_s5` int(11) DEFAULT NULL,
  `boss4_s1` int(11) DEFAULT NULL,
  `boss4_s2` int(11) DEFAULT NULL,
  `boss4_s3` int(11) DEFAULT NULL,
  `boss4_s4` int(11) DEFAULT NULL,
  `boss4_s5` int(11) DEFAULT NULL,
  `boss5_s1` int(11) DEFAULT NULL,
  `boss5_s2` int(11) DEFAULT NULL,
  `boss5_s3` int(11) DEFAULT NULL,
  `boss5_s4` int(11) DEFAULT NULL,
  `boss5_s5` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='每月王的血量，開戰日期與時間';

-- 取消選取資料匯出。

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
