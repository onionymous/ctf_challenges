-- import to SQLite by running: sqlite3.exe db.sqlite3 -init sqlite.sql

PRAGMA journal_mode = MEMORY;
PRAGMA synchronous = OFF;
PRAGMA foreign_keys = OFF;
PRAGMA ignore_check_constraints = OFF;
PRAGMA auto_vacuum = NONE;
PRAGMA secure_delete = OFF;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS `note`;

CREATE TABLE `note` (
`id` INTEGER NOT NULL,
`title` TEXT NOT NULL,
`body` text NOT NULL,
`owner_id` INTEGER NOT NULL,
PRIMARY KEY (`id`),
FOREIGN KEY (`owner_id`) REFERENCES `user` (`id`)
);
DROP TABLE IF EXISTS `user`;

CREATE TABLE `user` (
`id` INTEGER NOT NULL ,
`username` TEXT NOT NULL,
`password` TEXT NOT NULL,
PRIMARY KEY (`id`)
);
INSERT INTO `user` VALUES (1,'admin','ADMIN_PASSWORD_HASH');
INSERT INTO `note` VALUES (1,'secret_flag','dice{THE_FLAG}', 1);


CREATE INDEX `note_owner_id` ON `note` (`owner_id`);
CREATE UNIQUE INDEX `user_username` ON `user` (`username`);

COMMIT;
PRAGMA ignore_check_constraints = ON;
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
