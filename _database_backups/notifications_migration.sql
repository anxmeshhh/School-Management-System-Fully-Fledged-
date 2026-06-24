-- Migration: Create notifications table
-- Run this against your school_db database

CREATE TABLE IF NOT EXISTS `notifications` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `recipient_type` ENUM('admin', 'teacher', 'student', 'parent') NOT NULL,
  `recipient_id` INT NOT NULL,
  `sender_type` ENUM('admin', 'teacher', 'student', 'parent', 'system') DEFAULT 'system',
  `sender_id` INT DEFAULT NULL,
  `category` VARCHAR(50) NOT NULL COMMENT 'leave, attendance, circular, homework, marks, timetable, exam, fee, student, class, user, study_material, profile, auth',
  `title` VARCHAR(255) NOT NULL,
  `message` TEXT NOT NULL,
  `action_url` VARCHAR(500) DEFAULT NULL COMMENT 'URL to navigate when notification is clicked',
  `is_read` TINYINT(1) NOT NULL DEFAULT 0,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_recipient` (`recipient_type`, `recipient_id`, `is_read`),
  KEY `idx_recipient_created` (`recipient_type`, `recipient_id`, `created_at` DESC),
  KEY `idx_created` (`created_at`),
  KEY `idx_category` (`category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
