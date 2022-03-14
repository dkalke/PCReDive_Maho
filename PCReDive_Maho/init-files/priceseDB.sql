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
  `group_serial` int(11) unsigned NOT NULL,
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
  `table_channel_id` bigint(20) DEFAULT NULL,
  `sign_channel_id` bigint(20) DEFAULT NULL,
  `info_channel_id` bigint(20) DEFAULT NULL,
  `log_channel_id` bigint(20) DEFAULT NULL,
  `table_message_id` bigint(20) DEFAULT NULL,
  `knife_pool_message_id` bigint(20) DEFAULT NULL,
  `info_message_id` bigint(20) DEFAULT NULL,
  `controller_role_id` bigint(20) DEFAULT NULL,
  `fighting_role_id` bigint(20) DEFAULT NULL,
  `boss_change_1` datetime NOT NULL DEFAULT current_timestamp(),
  `boss_change_2` datetime NOT NULL DEFAULT current_timestamp(),
  `boss_change_3` datetime NOT NULL DEFAULT current_timestamp(),
  `boss_change_4` datetime NOT NULL DEFAULT current_timestamp(),
  `boss_change_5` datetime NOT NULL DEFAULT current_timestamp(),
  `table_style` tinyint(4) NOT NULL DEFAULT 0,
  `upload` tinyint(1) unsigned zerofill DEFAULT 0,
  PRIMARY KEY (`server_id`,`group_serial`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='設定檔';

-- 取消選取資料匯出。

-- 傾印  資料表 princess_connect.keep_knifes 結構
CREATE TABLE IF NOT EXISTS `keep_knifes` (
  `serial_number` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `server_id` bigint(20) unsigned NOT NULL DEFAULT 0,
  `group_serial` int(11) unsigned NOT NULL,
  `member_id` bigint(20) unsigned NOT NULL DEFAULT 0,
  `comment` varchar(150) NOT NULL DEFAULT '',
  PRIMARY KEY (`serial_number`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=327 DEFAULT CHARSET=utf8mb4;

-- 取消選取資料匯出。

-- 傾印  資料表 princess_connect.knifes 結構
CREATE TABLE IF NOT EXISTS `knifes` (
  `serial_number` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `server_id` bigint(20) unsigned NOT NULL DEFAULT 0,
  `group_serial` tinyint(4) unsigned NOT NULL,
  `member_id` bigint(20) unsigned NOT NULL DEFAULT 0,
  `sockpuppet` int(10) unsigned NOT NULL DEFAULT 0,
  `week` tinyint(4) unsigned NOT NULL,
  `boss` tinyint(4) unsigned NOT NULL,
  `comment` varchar(150) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp(),
  `done_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `knife_type` tinyint(4) NOT NULL DEFAULT 0,
  `real_damage` int(10) unsigned NOT NULL DEFAULT 0,
  `estimated_damage` int(10) unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`serial_number`)
) ENGINE=InnoDB AUTO_INCREMENT=5453 DEFAULT CHARSET=utf8mb4 COMMENT='每刀資料\r\nsockpuppet固定為0，跟隨本尊(報刀不區分本尊分身，此處留下是為了外鍵)';

-- 取消選取資料匯出。

-- 傾印  資料表 princess_connect.knife_summary 結構
CREATE TABLE IF NOT EXISTS `knife_summary` (
  `serial_number` int(11) unsigned NOT NULL,
  `day` datetime NOT NULL DEFAULT current_timestamp(),
  `normal` int(11) DEFAULT 0,
  `reserved` int(11) DEFAULT 0,
  PRIMARY KEY (`serial_number`,`day`) USING BTREE,
  CONSTRAINT `FK_knife_summary_members` FOREIGN KEY (`serial_number`) REFERENCES `members` (`serial_number`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='統計刀表';

-- 取消選取資料匯出。

-- 傾印  資料表 princess_connect.members 結構
CREATE TABLE IF NOT EXISTS `members` (
  `serial_number` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `server_id` bigint(20) unsigned NOT NULL,
  `group_serial` int(11) unsigned NOT NULL,
  `member_id` bigint(20) unsigned NOT NULL,
  `sockpuppet` int(11) unsigned NOT NULL DEFAULT 0,
  `period` tinyint(3) unsigned NOT NULL DEFAULT 0,
  `is_captain` tinyint(3) unsigned NOT NULL DEFAULT 0,
  `last_sl_time` datetime NOT NULL DEFAULT current_timestamp(),
  `now_using` tinyint(3) unsigned NOT NULL DEFAULT 1,
  PRIMARY KEY (`serial_number`),
  KEY `FK_members_group` (`server_id`,`group_serial`),
  CONSTRAINT `FK_members_group` FOREIGN KEY (`server_id`, `group_serial`) REFERENCES `group` (`server_id`, `group_serial`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4;

-- 取消選取資料匯出。

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
