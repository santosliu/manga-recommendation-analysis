CREATE TABLE `books` (
	`id` INT(11) NOT NULL AUTO_INCREMENT,
	`book_id` INT(11) NOT NULL DEFAULT 0,
	`book_name` VARCHAR(150) NOT NULL DEFAULT '0',
	`book_url` VARCHAR(250) NOT NULL DEFAULT '0',
	`book_cover` VARCHAR(250) NULL DEFAULT NULL,
	`last_update` DATE NOT NULL DEFAULT '1970-01-01',
	`created_at` TIMESTAMP NOT NULL DEFAULT current_timestamp(),
	`updated_at` TIMESTAMP NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
	PRIMARY KEY (`id`),
	UNIQUE INDEX `book_id` (`book_id`)
)
COLLATE='utf8mb4_general_ci'
ENGINE=InnoDB
;
