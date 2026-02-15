-- 安全加固：添加用户安全字段
-- 执行日期：2026-02-15
-- 用途：添加登录失败次数、账户锁定时间、最后登录信息等安全字段

USE web_b2b;  -- 请替换为你的数据库名

-- 1. 添加密码字段长度支持bcrypt
ALTER TABLE `b_user` MODIFY COLUMN `password` VARCHAR(255) NULL;

-- 2. 添加密码加密类型字段
ALTER TABLE `b_user` ADD COLUMN `password_hash_type` VARCHAR(20) DEFAULT 'bcrypt' NULL COMMENT '密码加密类型' AFTER `password`;

-- 3. 添加登录失败次数字段
ALTER TABLE `b_user` ADD COLUMN `login_attempts` INT DEFAULT 0 NULL COMMENT '登录失败次数' AFTER `exp`;

-- 4. 添加账户锁定时间字段
ALTER TABLE `b_user` ADD COLUMN `lock_time` DATETIME NULL COMMENT '账户锁定时间' AFTER `login_attempts`;

-- 5. 添加最后登录时间字段
ALTER TABLE `b_user` ADD COLUMN `last_login_time` DATETIME NULL COMMENT '最后登录时间' AFTER `lock_time`;

-- 6. 添加最后登录IP字段
ALTER TABLE `b_user` ADD COLUMN `last_login_ip` VARCHAR(50) NULL COMMENT '最后登录IP' AFTER `last_login_time`;

-- 查看修改结果
DESCRIBE `b_user`;
