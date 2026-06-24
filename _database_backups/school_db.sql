-- MySQL dump 10.13  Distrib 8.0.43, for Linux (x86_64)
--
-- Host: localhost    Database: school_db
-- ------------------------------------------------------
-- Server version	8.0.43-0ubuntu0.24.04.2

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `admin_attendance`
--

DROP TABLE IF EXISTS `admin_attendance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_attendance` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL,
  `name` varchar(255) NOT NULL,
  `admission_number` varchar(100) NOT NULL,
  `class` varchar(50) NOT NULL,
  `section` varchar(10) DEFAULT NULL,
  `date` date NOT NULL,
  `status` enum('present','absent','leave') NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `student_id` (`student_id`,`class`,`date`),
  UNIQUE KEY `unique_admin_attendance` (`student_id`,`class`,`section`,`date`),
  CONSTRAINT `admin_attendance_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `student_page1` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_attendance`
--

LOCK TABLES `admin_attendance` WRITE;
/*!40000 ALTER TABLE `admin_attendance` DISABLE KEYS */;
INSERT INTO `admin_attendance` VALUES (1,2,'Deepa Menon','8998','10','A','2025-05-21','present','2025-05-26 17:54:06'),(3,18,'Hari Pillai','3986','10','B','2025-05-21','present','2025-05-26 17:54:09'),(5,10,'Chitra Patel','4826','6','A','2025-05-26','leave','2025-05-26 18:06:38'),(6,3,'Bala Patel','4746','6','C','2025-05-26','present','2025-05-26 18:07:10'),(7,3,'Bala Patel','4746','6','C','2025-05-27','absent','2025-05-26 18:32:27'),(8,4,'Bala Patel','8327','10','A','2025-05-26','present','2025-05-26 19:04:45'),(9,6,'Ezhil Nair','4347','1','B','2025-05-30','present','2025-05-30 07:16:12'),(10,3,'Bala Patel','4746','7','C','2025-05-30','present','2025-05-30 07:24:18'),(11,20,'Arun Rao','7558','7','C','2025-05-30','absent','2025-05-30 07:24:19'),(12,20,'Apu','7558','1','C','2025-06-07','present','2025-06-07 10:01:14'),(14,17,'Deepa Menon','7561','6','B','2025-06-11','absent','2025-06-11 17:51:55'),(17,6,'Ezhil Nair','4347','1','B','2025-06-11','absent','2025-06-11 17:52:34'),(19,17,'Deepa Menon','7561','6','B','2025-06-09','present','2025-06-11 17:53:02'),(22,20,'Apu','7558','1','C','2025-06-14','present','2025-06-13 20:03:08'),(23,20,'Apu','7558','1','C','2025-06-15','leave','2025-06-15 11:48:38');
/*!40000 ALTER TABLE `admin_attendance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_login`
--

DROP TABLE IF EXISTS `admin_login`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_login` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_login`
--

LOCK TABLES `admin_login` WRITE;
/*!40000 ALTER TABLE `admin_login` DISABLE KEYS */;
INSERT INTO `admin_login` VALUES (1,'admin','admin123','2025-05-05 18:03:29'),(2,'testuser','testpass','2025-05-05 18:03:29');
/*!40000 ALTER TABLE `admin_login` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_manage_users`
--

DROP TABLE IF EXISTS `admin_manage_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_manage_users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `email` varchar(255) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` varchar(50) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_manage_users`
--

LOCK TABLES `admin_manage_users` WRITE;
/*!40000 ALTER TABLE `admin_manage_users` DISABLE KEYS */;
INSERT INTO `admin_manage_users` VALUES (13,'verrgroup','verrgroup@gmail.com','verrgroup_13','verr','teacher','2025-06-22 12:14:36','2025-06-22 12:14:36'),(14,'dileep medisetti','dileepmedisetti12@gmail.com','dileep_medisetti_12','2222222222','Teacher','2025-08-10 06:38:05','2025-08-10 06:38:05'),(15,'adi','adityanair5002@gmail.com','adi_123','12345678','Teacher','2025-10-08 17:21:28','2025-10-08 17:21:28');
/*!40000 ALTER TABLE `admin_manage_users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_student_batch`
--

DROP TABLE IF EXISTS `admin_student_batch`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_student_batch` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `academic_year` varchar(9) NOT NULL,
  `created_at` timestamp NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  UNIQUE KEY `academic_year` (`academic_year`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_student_batch`
--

LOCK TABLES `admin_student_batch` WRITE;
/*!40000 ALTER TABLE `admin_student_batch` DISABLE KEYS */;
INSERT INTO `admin_student_batch` VALUES (1,'2017-2018','2025-05-21 10:14:15'),(2,'2020-2021','2025-05-21 10:23:22'),(3,'2022-2023','2025-05-21 10:23:25'),(4,'2019-2020','2025-05-21 10:35:07'),(6,'2024-2025','2025-05-21 10:35:18'),(7,'2016-2017','2025-05-21 11:33:40');
/*!40000 ALTER TABLE `admin_student_batch` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_student_classes`
--

DROP TABLE IF EXISTS `admin_student_classes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_student_classes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `admin_id` int NOT NULL,
  `class` varchar(10) NOT NULL,
  `section` varchar(10) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_admin_class_section` (`admin_id`,`class`,`section`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_student_classes`
--

LOCK TABLES `admin_student_classes` WRITE;
/*!40000 ALTER TABLE `admin_student_classes` DISABLE KEYS */;
INSERT INTO `admin_student_classes` VALUES (2,1,'2','A','2025-05-20 21:50:27'),(3,1,'2','B ','2025-05-20 21:53:15'),(5,26,'2','A','2025-05-20 23:38:46'),(6,1,'2','G','2025-05-20 23:40:52'),(7,28,'3','B','2025-05-20 23:43:00'),(8,1,'3','B','2025-05-20 23:48:45'),(9,1,'1','A','2025-05-21 09:09:14'),(10,29,'2','V','2025-05-21 09:16:54'),(11,1,'2','v','2025-05-21 09:18:31'),(12,30,'2','A','2025-05-21 09:33:39'),(13,1,'5','B','2025-05-21 11:34:00'),(14,1,'3','C','2025-06-04 09:13:28'),(15,1,'12','C','2025-06-11 19:04:59'),(16,41,'10','C','2025-06-13 09:57:14');
/*!40000 ALTER TABLE `admin_student_classes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admins`
--

DROP TABLE IF EXISTS `admins`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admins` (
  `id` int NOT NULL AUTO_INCREMENT,
  `full_name` varchar(100) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admins`
--

LOCK TABLES `admins` WRITE;
/*!40000 ALTER TABLE `admins` DISABLE KEYS */;
INSERT INTO `admins` VALUES (1,'Animesh Gupta  ','apurvasingh@gmail.com','aniapu','2025-05-03 18:09:01','2025-05-03 18:09:01'),(2,'verrgroup','verrgroup@gmail.com','verr','2025-05-03 18:29:27','2025-05-03 18:29:27'),(3,'ADITYA NAIR','adityanair5002@gmail.com','12345678','2025-06-22 11:57:47','2025-06-22 11:57:47'),(4,'adi','adi@gmail.com','1234567890','2025-06-26 05:40:20','2025-06-26 05:40:20'),(5,'Harsh','harshbro@gmail.com','1234567890','2025-07-05 08:56:40','2025-07-05 08:56:40'),(6,'Vignesh Raja','vigneshrajatamil@gmail.com','12345','2025-07-06 12:48:49','2025-07-06 12:48:49'),(7,'Pratik bhai','pratik@gmail.com','8109805643','2025-07-13 18:12:29','2025-07-13 18:12:29'),(8,'dileep medisetti','dileepmedisetti12@gmail.com','1234567890','2025-08-10 06:17:44','2025-08-10 06:17:44'),(10,'Animesh Gupta','guptaanimesh020@gmail.com','1234567890','2025-08-13 19:23:58','2025-08-13 19:23:58'),(13,'Dileep','dileep@gmail.com','9999999999','2025-09-07 14:12:59','2025-09-07 14:12:59'),(14,'ADITYA NAIR','an9103@srmist.edu.in','1234567','2025-10-08 16:04:12','2025-10-08 16:04:12');
/*!40000 ALTER TABLE `admins` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `attendance`
--

DROP TABLE IF EXISTS `attendance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `attendance` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL,
  `class` varchar(50) NOT NULL,
  `date` date NOT NULL,
  `status` enum('present','absent','leave') NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `section` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `student_id` (`student_id`,`class`,`date`),
  UNIQUE KEY `student_id_2` (`student_id`,`class`,`date`),
  UNIQUE KEY `unique_attendance` (`student_id`,`class`,`section`,`date`),
  CONSTRAINT `attendance_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `student_page1` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attendance`
--

LOCK TABLES `attendance` WRITE;
/*!40000 ALTER TABLE `attendance` DISABLE KEYS */;
INSERT INTO `attendance` VALUES (1,2,'10','2025-05-21','present','2025-05-26 17:51:58','B'),(3,18,'10','2025-05-21','present','2025-05-26 17:54:09','B'),(4,10,'6','2025-05-26','leave','2025-05-26 18:06:38','A'),(5,3,'6','2025-05-26','present','2025-05-26 18:07:10','C'),(6,3,'6','2025-05-27','absent','2025-05-26 18:32:27','C'),(7,4,'10','2025-05-26','present','2025-05-26 19:04:45',NULL),(9,6,'1','2025-05-30','present','2025-05-30 07:16:12','B'),(10,3,'7','2025-05-30','present','2025-05-30 07:24:18','C'),(11,20,'7','2025-05-30','absent','2025-05-30 07:24:19','C'),(12,20,'1','2025-06-07','present','2025-06-07 10:01:14','C'),(14,17,'6','2025-06-11','absent','2025-06-11 17:51:55','B'),(15,21,'6','2025-06-11','present','2025-06-11 17:51:56','B'),(17,6,'1','2025-06-11','absent','2025-06-11 17:52:34','B'),(19,17,'6','2025-06-09','present','2025-06-11 17:53:02','B'),(20,21,'6','2025-06-09','present','2025-06-11 17:53:02','B'),(22,20,'1','2025-06-14','present','2025-06-13 20:03:08','C'),(23,20,'1','2025-06-15','leave','2025-06-15 11:48:38','C');
/*!40000 ALTER TABLE `attendance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$870000$VLnPC5DyP2PlKeMSUE4Otm$Y9kkK03GBXDjGxxocUvlJoT8hBlyo3iUHN6UbQgv96M=','2025-04-23 17:58:27.424052',1,'anxmeshhh','','','guptaanimesh020@gmail.com',1,1,'2025-04-23 17:50:33.866541');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'auth','user'),(5,'contenttypes','contenttype'),(6,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2025-03-04 17:42:30.939640'),(2,'auth','0001_initial','2025-03-04 17:42:31.253981'),(3,'admin','0001_initial','2025-03-04 17:42:31.326209'),(4,'admin','0002_logentry_remove_auto_add','2025-03-04 17:42:31.330343'),(5,'admin','0003_logentry_add_action_flag_choices','2025-03-04 17:42:31.335781'),(6,'contenttypes','0002_remove_content_type_name','2025-03-04 17:42:31.384971'),(7,'auth','0002_alter_permission_name_max_length','2025-03-04 17:42:31.419102'),(8,'auth','0003_alter_user_email_max_length','2025-03-04 17:42:31.432347'),(9,'auth','0004_alter_user_username_opts','2025-03-04 17:42:31.437143'),(10,'auth','0005_alter_user_last_login_null','2025-03-04 17:42:31.466311'),(11,'auth','0006_require_contenttypes_0002','2025-03-04 17:42:31.468829'),(12,'auth','0007_alter_validators_add_error_messages','2025-03-04 17:42:31.473563'),(13,'auth','0008_alter_user_username_max_length','2025-03-04 17:42:31.507362'),(14,'auth','0009_alter_user_last_name_max_length','2025-03-04 17:42:31.541020'),(15,'auth','0010_alter_group_name_max_length','2025-03-04 17:42:31.553999'),(16,'auth','0011_update_proxy_permissions','2025-03-04 17:42:31.560242'),(17,'auth','0012_alter_user_first_name_max_length','2025-03-04 17:42:31.601221'),(18,'sessions','0001_initial','2025-03-04 17:42:31.621466');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('1kqglt6jnjheyay6xkjdf8ydpn2e6jio','eyJ1c2VyX2lkIjo2LCJ1c2VybmFtZSI6InZlcnJncm91cCJ9:1uQk4y:ea24mZ2G62jRPf_umf3PwAu-tO5A-q9ujEAUV2ynCPM','2025-06-29 09:55:08.524632'),('1yr3h0xjmj7bbkxh2thk5lgnvy8zjo7a','eyJ1c2VyX2lkIjo2LCJ1c2VybmFtZSI6InZlcnJncm91cCJ9:1u6llj:O8bQLthaJ7eU4755g63VVE-6m6PGWvjSE1UYbvFOZaA','2025-05-05 07:40:43.166148'),('2vyp76m6d5ng0n2xmtudakwg6xftdoyv','eyJ0ZWFjaGVyX2lkIjoxLCJ1c2VybmFtZSI6IkFwdXJ2YSBBbmltZXNoIiwidXNlcl9pZCI6MjB9:1uRxW7:HDTk6S2S6hiR4SCsF-82y6PXZ-kU5UL_E_7EcgkIpOI','2025-07-02 18:28:11.459933'),('34kdokicv3253lhnqd4tvd8f084hreuk','.eJydVMlu2zAQ_ZVA57jelDjJLQWaoofkkg8gRuRIGpSLwiWGG-TfS9qyRCnupTpp3sy82flRgFCkGYniYb267iUNCouH4lGTQtde_Qydh-K6cD4I1J4JiOLDRxEc2qPn7XXRWVOTRNYR98Em76VCQbDs6gi55a4SsFuJervjd-WNqGC1qUtRwmp7vyk35Zbdfut0U3whYh34NrG9g13u9_vlK2-NkYtn0NCgiuksXg_Oo1o8BSkPiyeJokGx-M_ofeU__rQkr16AbHHqiXNkYl-CqtBGfbktd1HDJTgXxXVqDnIfbaL0PUrWSDma36_uyghi5Enkz79e16v43USsQS2ONi_Lx8RolAqa_GFAPCiS54mcIGGq4V9Digoyd6mkMYI11oRuwJTxbZyWN7oJIxOH2LpBsiipOdVwAjoJHJmpWUX2OIUTDCBagDFpQQ4qmqRAgimwv9dzYDOGDtamZTr3sKceev0v_IBZ5BGOOzkWggpIZkbCYsbFjfbA_aiXMYsZxk3Q3o71OJ_z87zUjjQ3AiemYYzWmngm4zQReJrDHqwY-55Ru85Y79hbMOnGziEsvjN3XPwpVpmcp4bjjCe7kmHsuErzjZhYZ9jMuueZ96l3mMO99XQOve0U7C3fQlzhmjj4fP96j8vK3tNwHrqLbhc0vU-a2NeqZ2gTYm8J9LRDAzoveVBM6-PxIRFM0jvF92UYODVtHHLa8qQeE0HBLh1vPDAEh9k5SIm2oQxJzx0njfniuY48jKkIw705387n5193Dt_n:1umH8b:__lZPNnGPnF9WJ9aVilID5jYD15xgs-09R30yxtEEYA','2025-08-27 19:27:53.480362'),('447r58qq6mjs333nfn32x0f6q4imywue','eyJ1c2VyX2lkIjo2LCJ1c2VybmFtZSI6InZlcnJncm91cCJ9:1uSuVn:esMjpHp8F5wWINYrM7sACOd7sEdFm88Ef7ULG4nWe88','2025-07-05 09:27:47.909829'),('5sqwvacl5hft4c2agm2mi7tdfigel10u','eyJhZG1pbl9pZCI6MSwiYWRtaW5fbmFtZSI6IkFuaW1lc2ggR3VwdGEgICJ9:1uE1Dj:ch0c1kjSVXPGkgjqTqspDDlV1i4aphUp1EQvEz_riHU','2025-05-25 07:35:35.065464'),('6hfor6lpjqr8oy06w9bpfbv8esnbwv2o','eyJhZG1pbl9pZCI6MSwiYWRtaW5fbmFtZSI6IkFuaW1lc2ggR3VwdGEgICJ9:1uRz4r:EnHbGR_nVsy3gGFPr7qcLgmk4TmKZ-uJ9KsHQEvuUy8','2025-07-02 20:08:09.794027'),('8g37aeb64m1yggvhn76wusstwuzvcr43','eyJhZG1pbl9pZCI6OCwiYWRtaW5fbmFtZSI6ImRpbGVlcCBtZWRpc2V0dGkifQ:1ulAgd:AQIY2R52SZAecu6zDLP0WS10boeVb7pWYFW5n-z6V-o','2025-08-24 18:22:27.274309'),('8i99vfb93k3mim618hmjb2ozkemyi6bt','.eJyrVkpMyc3Mi89MUbIyNNGB8vISc1OVrJQcXTxDIh0V_Bw9g5R0lEpSE5MzUosgSo2MdZRKi1OLoCqBfCWIAFja1KgWAOCwGzY:1v6XxQ:bq05egz-VLwNnpCNaKbHLXTZ47I1bucUqjsbrQjDh5o','2025-10-22 17:28:08.165439'),('9njsok53n2n1obb8llghjhl79wedefpd','eyJ1c2VyX2lkIjoyMCwidXNlcm5hbWUiOiJBcnVuIFJhbyJ9:1uXyew:MdavCfdG4TColcTOxp6uwT8gICKTXrF2xxxOMqWmTpI','2025-07-19 08:54:10.942177'),('a2sm23mroee0vehqnfcp0ateosjlahzs','.eJyrViotTi2Kz0xRsjKx1AFz8hJzU5WslFIyc1JTCxRyU1Myi1NLSjKVdJQSU3Iz88BqLWAc3IpLUhOTM6BGGxrVAgByfCP2:1up8UW:dgKGAXGCaTgAfNdFAomMhKWE2AcM1YY2Nbo7ARKpXCI','2025-09-04 16:50:20.030518'),('b4kya776xesd0tm313vk12g54dh7vj8j','eyJhZG1pbl9pZCI6NiwiYWRtaW5fbmFtZSI6IlZpZ25lc2ggUmFqYSJ9:1uYOnj:P3KX4YEEfwm-5A126kOFv4gzhkHzzsENjooj-1vXX08','2025-07-20 12:48:59.591345'),('bv6rk8w892jwlk849u5wtxg9yv3hp9fk','eyJhZG1pbl9pZCI6MTAsImFkbWluX25hbWUiOiJBbmltZXNoIEd1cHRhIn0:1umH4v:9CQ2D3dSaU7dpIVFVF6x-Og2F-wiwjz9y7lDI-9WETg','2025-08-27 19:24:05.725747'),('dsmxai2r3hfil6ih7sa58m63h23yo1qy','.eJzVfXmT4ri35VepyH_pKizZlqzfxEQMmH3ft4kXFQYMGBvbeGF78b77yEBWYpDNknRHT1d3R6URoPRyj84991z994fvqs5vbfrxH8j9dfzBVFbqx38-UrbvbJQfKVNbqe7i468PZbrSzONI8PnD59DTmB953_aUHz_oWM1TV-7Hf_77Y2Gt1K3l6B__-b__9deH6_nTffDX__nrY6YZajCE_nXsG_pv3zYsZfp7qngKHfHfH-fPzh4WmvGjuFed8xRcV7PoN_urMT1EvztTBRzH0RcnhuLSD_xA9O-uOvHoMPpTmv7kWIbx9Q6U5gA9qNKPCj6_WmwHH3D8iLlqTo9jqoqhBh9prVa-qXl0zh_tDj3gKSvN-M2a2tQa00OQA-AngD-BQA-ZSjAHxTi9v2hONcWkh8eGZU1_zx3Lt4P5pxP02MryFvQyeJY599XT9yt7-t8qmITiesExeaF6nqYEX-aohjY__X5tTQ8ujm0oE_W3Nfs91hxvcRptmooWnDRlulCU4LcSIc8hQcKQiDiYsuYqY-08veCiTX-vFEcHwfdbhvrDMn8Y6sz7MVmoqv71Orx43dHmC--H4hzn6TuOanq_L6_D1wX7PMqHju7V48QgB0HoOL0L1PPxnxz_E5DjBVM0gx5Ug9P-S6OnHeP_o-6UlW2ov-iVOn7A1FGPX4PBj6qimT9a9J7664dsaaux4lnO6aKanjLx6CCCAAQCFPng4xWDTv3rJSxIgEM8h4_v8E3P-XMRg_vLO02wE9wPP2rK1A-Gnc5kx9Emi31wTTRzYk2DYYjeXgSf3-cH80vR-3MTzGZh0WeOHmip0-D-UpVJcCNsFYc-Zx-mFVzs4zcd_-raluO5v9e-FTwkp2O2o25-u5OFZRmny3g8MLZOn0B_ninHe-t802ZU1VZ-tDVzvgi_9vt4b9-MON-Z53fn6Hhtpfxo0F_fCL_65_3XY87fcXFuoSRAgJAgfH3Cxau8hEQgcQL4eu_npZ8GU_vlBlO7uvLnj_kcODvN4ZcdzOFq6Pkz1z59MmfaRDkHimo63f76oJtXf7UnX--1JhPf_nwp7dMJ0btudXy6z-8PjchYE3rvfb09uC-OpxMRBEXp611_XhCIALnghblPryONG58XIE2DAr3fNOfytYuTJ3AYSpwkoV_c5YjP8zKmb_9Fw4JzdU4m9JGa_ja0DT21dFhf8xb0-gWPsxvcgcFT7v4OnuJgHB2QP39wMHV1-psV0mh0URU3CPEfGU0Zq57qHp8yQ3Xm2vFwg4Zl9fwR2iQ4h6cbdmG5tuYpx3uJ3u-a-6PweSSIs8dzST_U-fWj4Wh75eN__vqDFinHp8-8YsVhBbjAChzCitQNVuAUBxlYAe5hhXyNFRcT-4MU4k8O_4Tco0hRZwFFQaODL0AiT0PVVL3CiGCQzwKJNp36KgQRmEMi_Y8IEkHXEFGgwZreHz-KK5veQSt6c4RBIwwR6eA7gh8CnDDVic6ACMyECCECIrgIiOACxD1j-uk2V-jZ_uUoFojEB0F4BB-EIwgQjr_FBwEjTAA4vvQcPlTpT84RmcMAAflYgMg76vFhiYaI_fEJu8KI08EwSJTprRs8OT962nR_XGlcw0Y7mP-P9PGnawSRF5rnKD-qqmmZERByNSSMIadlU091VkoEgoRH3OIH5kWJF3hJZOMHJyAEBMLf4sfkOK9fq2Be8QByWmRsgik8Bh-Nxa9MNHykf8mXb34SP7LmnI5QWQgCBAlKCDAgBPFA4kUGhJwvzifAM1FEECHi6E3JRpHzaWThMAtILsDiFklyx1-IiSP1KxhJuUFAuQYRVTH9I0pdokjRXNDQ5oTBJG_R62kGcSsSUCiTMZ7FE3iBJ-QO9yDpY8C4xhP4Djzh0E9O_AnAw8zjJwNPygplDVPlHqI8wzoIgAImhDIjnotnHc9zDPIMxwBhRvIHQAAKOAaELACJRhCMQwjy5xe_XOfydKErcZhBLziKsIh-M3oaPr6-KQwfiMTCx1A1DGv7Hvy4SzJKylwxf7QXSiiCh2L81ZAwRJwoyOn2ZgHE5eu38EDJAwyIOMeEB4EQggjAwi08LIM5_XKPc4qHhxMRoTfIvxscgAQAuUDJL3AQOB6xwCGvmEEmp-yvlCiKgUTIA4w5iQ0O8-Mn_NKDT_gmy4jBhmPwuocNj4BCyqYB2nqcYQSPKEXPz8VJJCrwH1EZqVuWgVKcwEAF_hIVcvT83uBC-gYXrqb3Bxso16BR7omsFAscWFmpNg0mU99Qpz_k45FXiQeCCAIJc3T59k3i8XpuKnz0i3iE8eSLePA_OUo8xAvc0I6n_7RuhNHZKT7EPr4IwcVTRuiyTpB4Am6xAwkigEA8EdmnsOPztIeRQ4pHjjcSjweB4zP6ROPG5wh2diqOW1yPYbALEfF0uSJc5GVCuStEJAwlKQo-WIEvIjv1BL0455-islOn3BULQC7g4Un0kCTIM5kFxMGjygAPNmCwQOLNYJC-QoNrjsBKNDHR4E6-6Zoe_El1aoZxWvVGwYFwAQfSHTiQUueYEoYD4S4c3EoUNxO8TD7RNa_0KCDUWXhwnXw65yUf4Am38Z8nPCICDzgMxHiWcE-bYIR7iRnuw0e_aEL4-BdNkI4Yyl-E-z9p5uPpJVJkwBdDZOGPQhCm3IgXKC9gxHtJhKKEyfNSRCivdSVHxAd9phxxCunv1SPOC5YrsSAUsq-GsKgCQ62I0DMYdAFKEPNR8Z4DgkCvi4Ru4_0Z7FkaA5MusPIlL4kR6V8ddXLxy4Qi-kWWI0u_yNqrakTs75yuLos4QALow8iI_TxCokgYsf_M52KSSoCXKBnmeMjmDWfy9WBO6WVxov4SVLi-oZlPEYeWsgxk8-tc0jlERuKE-BxOIAZOiHdxos5OJ53ndgUR-FsQcYxKFxDBFrGrvmtoKxZQhCLYF1pIksBJAg8h4m_Q4h5buIcfjwgXzwFKOEv1BSjkKABdAsox7xToczHKhXgJJZ9AevGcSQKlURyPpVskwfSEEXhKCbyDOYgoFkTShq_GEgcWiLB4Q1uZOJRhBlfWu0YUOd3O3qDKOY3xZ9nDgpXrMWFcOb_KkDCuP-BKCLmMeABLHOIEtk4hiTyRCOQZOsU5h3JaVsRDy3koS9L491AJuqyBkLDghFAuITDg5CxSxCjdHAzOHUQRaaizRvGg1v2yRHGFJlFK9-MixR1YuWYgBRrrHqAf6CNKo5BvYIXIx6KXa1hBH89qFOG5XcoUws_jIv91meI-85AXjuZ6pw98SKag3EPkEJAAPioBIUjpaS59TN6Yf3pOtxAj8IMCtBQWvhf0lJ_DhhTNRgi8K10ADAgWBcBQvnkJASQIx_Xye5RvEF8a9f-VdHHDuGNLpK7wKXSWKXpg6ahZMTRuQZKOWapb7HhcxAiz18fA41OreB49vtjGUyVSBPMSZkEHgoTHkAEdbLxgYcQL3OIJSSICC65A4ONZifqWWJz58R2ZGkcyi1sIkORj8dk1BOAXmEVochfUAnA_j_f26xjAUiOeK3_6ikcXarXEcyJdI9PbizwJA_84sYipiKIQGxK0z7kKR7GQGIkLEN7LUmGKkZiiAgMWsIQECKHAPQ0LUYq28ELF7GWKigkKjBxV2_tFf29n_wctHqmCOt_XcYW0V0PCOHF-MY5fXA25xQhKggEU0DEKMjJXlBsTAhC-xYjz3fBAIe155BP0Il7rPr_6vcRVWBS_RQwAJcxADMwDHoXIQiiHeC7kZ3ENEhRDYYlgNtc4pfeCivTvUo2q9WZ4eVch1FVdQCTKSBcoE5a9b1EGyRxhoIx0F2VudY6r6f3BGeEnR34eF7HfkL1va6Kq_pR-0nUWK5ZyMBRvgeeJCOgyTrpTF_WC4sEWuMMmi4dw5Fw1wKruIHwkkiD8SHktpRiAcAKPbtFEFAX6wEHx-UxVjOYhxlfYvsmCkUn1fjT8saFNrvEkLlUVKmZipZluqqE-rrMkLAwJj2CI3RzFD8IDdoqKwwhiiRejU1S3JVBXABKdh3kpPRWDH_dLpdgIc6N7C0FNLQM_oITQMZZc40dojcvCD7qgpFwaQMLGj6_F2d-Yqronkj8CHE9rHke7yv30FInkJrcltFL6WNh3jRrkLmpUb6ulwtP7gxqBm-An97DwwXTwdVTDn_sfcSmqKHH8z8L7Qh0XJCBBSAMiD96OFc-JGTHJKIoVl5zjaDY6JRdgdCkUd7cUCogACyLPMUqhKHyQIE3yvlzUkb98Kxf1sKjxDdrxslx-FPri6qNCAxiUg8K1BAUSVRzFIYzJUfB4WSw_amDvK42KNu69rmcATqILN1ZWCgeJA8zACDYysNDgzbzh2ox3FfbfJnhfM4ar2zAq9oNL6_bxhzjKADgZMMzbIGTefjT6X83wT_jngrQ6fFigYPryWMkpur6c7p-gDEyVAhHIY5Hn0dE3-lbhmwENIMwM7pm4YQSPgEG6D14KFZfhQBKixe5HaIQIicjTE8Pd4gMUARCRIAlvw4djvcG_o1j2ZJOLJg6Xr4dR4LjuiUs9hQbcogBF-8DQI7EN3AiLMMihMkqmTra6u6ThuHJ4m6QdwxniRYnoAikcGLcvpJkvVYJDJ2vJPxv_40ueHrNjX2HAx3dTRkf5955PAly6sa_C_23FE-BSgOHHBiE_9oPCRGh64e4d_MOebHb3juuiJ6YqEV3zxFj_Q0B4TJEJnCqyn1El2hPFCaL-jMbNhapMP54WqyNAICKZBMKm7i-CgANWBS6TSUe1-rjSixElhHuahASCUirMCv9A4DmenrjnNYlIegBjw__diqeHNYmYiqc4fnBcvsf5J0IDmCVPMdmk8IhbXAhqAwhBEaW0Igc5CSPCwIXjmv8B58Q56_R4NullNeJFuVoKVmcs00TQ8YRniQ9HqP2MQ6zkEb2zBUp_iRDT0oNFl96bPHoJQ97iuLvuJxMJJZdG7PsKN2AYsUHIiM3WHm6A5Hp-lzyCP9nDHsMSFpQ86Md-UnoQJQTowxh0i7mRHp4z2zHggp1OCqeNHkwnAemDYbYIzjOJBgwJ380oQUAplCSc-MqVjE0DmASRBJ-GjCgZm8QXyb7LaRGHGEWZITyc6EE4ljP4wy0cfHyWQMV1gQqPYFAIhIkYyDxMqBA4EYqYYIZ2faIQDAS4gopTHdQTDaDioeLlyqYHRQdMwzxLtBYx4o_M-Z8lFHFYEJ9Q-i6NuIn_D3UABNF-a1YHQMDwW4NX_NbMHoCB5gyekJ3ZzolrAYEtOkfTCIbizCGCeV4A-LYTx7fDPltxDmeEHlKc8clz8ly7P_6OKUIMuqwIpxXYVcQnNNoj6dQu4i2d_kB8iuiNEsJ1nL-J8UeSG50huniZIROwKlzDPOK6TDa0akV0pS8JF0nyy-gvEI6XAGZQgSMpvJshOhIGZpFrZOHq2TP3DyaJoAQhy0RHl_NE-ltEgrjS1RiN4EEbQ2xof9I6fbp_zqVxkVH90jZ937cAGLZp8IBtmm2H-5zcn6guHbPYD_fQeMgy_YamrpIk8Qhj8Y5t-m4AZ3sSoprxRfdrBTCc6j89qsHJRNGuNpHcS_MQHtF4IbJUYElE-Hgano7gbFvbMZ_4fAB_qfb0tVX7ecERvWo_D2B7E6IbK4VHMFwJAsECD2CEV5rjecTxrATPF4o_5kl4W2ulGKf0Hf33sYU7PSFQZCnBoog5zKoW-rcE-Sfa6X28QQi-qwQ8Z30GDOszuG99jpaBb6QA7rkOGY838n7OpMBQAwB9AoO1hcjhZ9WAv7s8KK5JK_gJ0Qe7VxKJ9iSId71qIicEf449za-RARGJIxJ5vj4oKpsjxS_uXzMlvLS2Py5S4rqwhgYwBOBYi1p4BAsJIF3cIu4i1x2S5AUMJElg5G-Oy4EHOrBeVI-9x5r2ciFQ9AqfxwjxLBlYDB7QyP7dcd31AIUNDiAhovXq8aw82lvvdcn4Wy283-U5uPJZRgLHpbn5fqs9wDA3g5C5-VHguJrfZfaHO4W61-uHHpKQH--uhJAoCRIflOI862r7vn78XGYoptkeCmeGLp2uca62u72XkABFAQrHssXrNt9AoiveU7HV23wIx40P_h0JorOiG8MnwiNYzZfiyknDIxgtMkjA6SAXsRWEQIKK3KPBje0_uM8oTuasJ-pJ72WKvrUVRLx1DUDC8fDiXHx5Dzh4wtp_cV0Rm1C8EyHY-z3czSI9Z30GDOszCFmfH-_QzcohwSd6KjH9aA9YC6JVAZbnmUcCT59EXiLiDTq8f9MHNp-IKimNgQP-lIxj5JmijWkSud-1mxCAOcQxxGEUrDYgPjrD34YGMJ5RsEuK3iwQM51pEa1SY9upMmhGXG--0ACGiIA5nuPEyyR6CLYRJ2EsMNAhrsMqi2c80ZrvHjzEppy-DRCcgE4e5ptOShInHhNvz5ubRQhEIEQxjqfMzS-35XutgyvDpfDsjkHhjGckhDznawYMXzMI-Zof2mAuPLeLGtUg9H3Pn3DNL9ji8uMEQ8AS4oQgFXpcyj2sQzwCGGz-8MIuQVy4WfdFrjlGmODuKMuEBnACAC8w4EIQiYh58flaIrYugeJ1iZfa7b3Ss_XzvoyrM70ewwAGxkthYLj6_MszC7EARBKxAxBHIMZIOi5mIoDhgVrTyFTLP51_ekyIECWOcBedQL5Ki3j6YLJyUWdmF1d7GvS-5XlRiGh8cSZhf3f16UNE4xGK8aRy8XkPf-ZQI9Hh0r98PwMFGf5lEPIvP4UOn7O73OsBPqFTPy5cfKe_d-CXIQRJRMDvzUC9jiAv1SZxlxLGZzQ5prNhTM_Wu42VpMBYS2MaoxUGBhjznIjfpm7Ht1V6m4Xh_i5zsawjtgXfzSCmkyGOeVwNuYUYUaKBE4eyMZck8VhwgAljG4jPm-KRFnznAPoE_Xi5SvWPZeHJVuACR0TE2kOI8PSff9c2EA-KFu_XuMPdz6NwAl56ne9L3JDhdIb3nc63SBGe3WUjVukZf8KjTfhuYeKZfYD4YOtGumIRjxs4PpWL-r5U8Zx3IWY_OfgTXFKNi-b2QnQVa1jrZsIEgkFjUMAgGxxBCIkQvs_qLH0TKB6kGy_iBCt1FJ1bYvZNihMurobc4oMgYgIQROzcFBBxcKkEBgWJTDixOye9bQ_S9_dmBZwAEbOvtwB5HvzzNugn2uddY8LfvO_DPQoBL33Q91sgQYYLGt7blZohYYfmdiFSBAvdxwtdH-p_FLtR3JP-NQB5hI-pePQ0SLytAuoFRxv4yV062r5KYUhMC4z7BVAIC0FRJmQUQFG2xVMk5Z7fOyiyWXe8ne2R4ti3AQOzQvZ7e8hFb10dtbs1IzuFeEHkUAQ0iFiiGC4eXcJX0PDwDnIxG1m_lp16S1_WGKBASMCs5JQIoCj-8_2S_kld-1lF4rRtwh2zM4zedZrljIAMszO8t-v0LVyEpnZV7_SP9Et6yu3Gc5KAuUArvnG7vb9Klu2eCB99pEdG0Bf9ssjptKNDcMqjK5zAPY0CcoJIiAAYBU5QwJjAt3bQe8098UKG6RoObqAgvANJpAMuYgugqPpZdoEtCwYoXQsa2TJhAEHK2IKt5W5h4GIXjwdccO8DgW9K14_pFFgiSGK1VxV4jJg6xbeh4MV80mM48P1k0i1lOGn295ptw-f2mIYMzzN8xfMcnt0lDMDTbmavt7v4m7aLQ4hwkohgsGvyk1Dw8SaxIYItxLTMC_pfXCLBqRDjuDjkY-gCeaRlXlAKTBARGHvESZgTadwSns8jxdQ43ema9yppYJW8pmn0pPffJ224xghmLulsAYqpgg2PYNvqYhonXQ1hVDoFNQTnPUdusUIiQBIhEhh9uM8umseddY_3TrqLFvLlu9_NGXhMb09WRwy6ZEHw32Ssu26I8bI8_dLuP6FWjZFQcWmkxnegAqcgw0gNQ0bqhxTq0NQuZQd0klG_UQJ7hRNP7v_GKoIVMSGIsnbCSzf7v327OUZ4vX8vgxTTQQ-eHIm3jTJxtIUOiY9AAl2QAgxPiuZ1Gz3AU_5-zlG-Y9vQv2e_NwZDuAMGzPxRqCFbpLDALng9w0RcZdPVkFsoCGRnDISI5qr0MogYiTxDeI7sBHeFBGfIeKK06d521O8Agth227yImFhA7yYCoqteP2MP02iHOSKKIhbjyl5Z3Oqtzbn_6f1DIxwU9zx28DlzNmSYs2HInP2EPHFjsDttTP1NBLluxMFINkUVNzG3jYP0JiWEruPA04rEx5tk6ihLdkxXbmarjuP5jum1JNzJNnECJwo8OfbHvyYXHI94XiTPV8RG9FqC8Va6iHbcr3TqiN7Wh4kipwAUp0-HRzBViNgOTNdjGB5tChMSBlxEtw4e04skEIZH-xT8Hteon2nE9PL207EFTJE0AiEJ8MzGegKSjhuh_4uUh2s4eEZ5eKMX4u6GPfDScv1I127IMF3DeztK3_bsvpngRfIp-Pd7nutvaxCs9kzBDvBBN3y6gkHPAsM9GeIbzbsjal9jxGtw3hKJvXtwDP3A9_uxihBRXIAio6wp8JUQKKLnBeyYdBT-Nmq8t0NfnFgdGhBGiVOrp1iQuBrCKHPlg2a3XESZqyRiSQAYMDb0OYoUD0jVp85Pb0SIaB_FawgBIBF4zOrTxwOJouTfARGvtnB6sQv382VMkdhwpw8rvPRah3Xp2zomkoYMrzW8v810tBniqhPrqYnTsa3361Thtgf307IEAxiCLd3o6otDIrjp3PdPAANbsI6yYce0-zt3ur3GhSAjLURr1uQei8CQC3IdhLHVNOIBL-BTceVbHBGv9eP4W_DgSHljmnJfvs7MPd1KFBEiBoMv8DwkAPPsnk4Yipj-YVkejrzxfkvuaK3iRUvdqxWtd0zWgkAkxGzrRAjEf0sXjhcl6gfzR1eA8BQSsK0O97r5wUvD9EMMgWGZhnct0xE9ma57-R25wWnvmW9Y4h7ci-GZtBEQsMAhzEPp-c4b90DgEa36ua194pxx8Ce4dMadKhmPyWgJRRcuCXdrWwVI_9A7gVG6JIoYCxig52WJiGSS-I_1ZYrc-zNOno5jCdHCw8eN0TfGDhdtdwgMbwIEERtFUwoBAP1ftED9-OY-T7VqetVyHUsVHitkIsF2RqxeTVgQCYL_ItpwY4z7hytaz5nKuzWt0TZqVpMNnmGjhve3gb7NKl1N7w934H9ywhN9_FIP6Qxv2b6HA3StBtB5MfKPU4e3VThJP7lL-eGcTT5tCipF2-T4h3YF5SVREk_tOa93fOADZy96wSoXk1NC3waPv9lYfXWbs1DkagirmVNcsik84hZDOI4nEsQCO9dEb-qgepjli7i8MR7p5vRMsilW2v57bRESpgSaZZ9DhK4L_00bRKQeFaof1iYe7_b3XzTQ-ob-26cnWZl-hhvTN4zwC19ocfGUafQXA_TpOP7ax59Q8OLK_u1qcxrWfSc4rTQoKf_RVspcTdrm_H-N6S-JhL-0Xrre2nLl_NxK0X9q7e4i253Tv7W39H9pXU4Ng-NSqsmnjv8Mau0WV0w5rjBBzVQqW-iVWtlcV81hz2yqzUq321tsSK413A67XdebcK1We7sf5lo9si7Pc6tMKp3SrPVI46rNUt_OVbfpaq40t5bptmFl98NJqStac3Eul4fdbCc3HeNpwdaCrVZIlTSmHOEONvJXvIOnaFo3k3xjZSaQyqHpYFTtNqupZnXeLTb7jUI_u105vFGqzuVCU27mDj4nbpfqaDWTiuVUdTA_LKf6nKvD3CTVL7nFpiIXm3sTZPbLbKXcak-q3Z0nevpk3tJgebc4pKUp_Z10vF1Yzno-wD7SE-N5W26YpfRiPMg02mDhTRstvCxmXT0_B4eGYvXKhT6ZbNHATtb0DOxVm8X1frrtuRydazvfQqnZsN9rIKI79crecCb9olzSkq1mi58nFolFpt-dGoVxebosycaQrHWjptLTLpmKf2jqzphwZn04aQilrNcaNPnZZqJUeoMSHo-qdXFt9w1vdOBmDXmY2E5Mt9xJk8w2nR4urFQLLMvZ6sbHB-LaK4SzWG-5iameqjd7udrC6ch5t1xzJon8vJiQC1oyVdnmBmWNZHujQfOg7AjOZzoE-nV_uk2SDlptG6siaS3qVhPsm7P8tGNbvFAt95O7YmbaqcqlpD2uWN2t0G7JbT-_X_KePsquGwNvDpr79L5dbRqOXM3J4003paSKrVRnPpazuV6toxOQHcqk5GN7Vsh3mkZRSW2mJu67-4qbOsCNk8bg4GW5tWuY7YU9hsQuuanmPrVPt6YHrdVbjkihoB8yK1PdTyu-UQT7pd2jZy8DYUFXU-PCGtdSKTw_jMpYrqc0Z5xIVNZ4tkINr1g3nLa5b07LdXO5Gwwyucwwq2rl7dA4zOiJ48BAGZDMrjQVC1xK1zdtpZHv5yyA9_SyL8dymS59nNzGq9R1ud3eS6bYU5KddmNWsvtdWPOwIpmVSrOdsgrCAaQP5c183-5LJWs8LlVTHaXYysy20xnXr1Wq9VW2ZmddPKzv_XpzuS3N0s12Z5NbpdZKYsKbbb2QahkLsZ-wNX0ubgFv-LKzSGaMRnpUSY38vZJpWGq-tp-4EwF1a56d4eZVA6tqt57FbZv-niYo25M8HE-EQaa6qpXmE-AW0U4az7hJe7DtbUpI73EWankVMaHYzmqhy1IrO6z0s7nSZiwY3nK4XXf1WffQbrSb026zN9uMtUrKGvCbrjdoqJKXL6_k3myyg6t5ab9Vu5m6lejVSiXdEZVBz9XNEUx31vSpHKUm80mxVJZyzsier5biICtsnIUxnEwMb1fZpJvD9DK1ySlgX20u9GZuueIy9BsW6dJYVDhH6eAemdq7gdYp960ineY8JZUUvlotdT3dK6Wz3b07WpG5s7cHMumk5eq-Im6EuZct5jdy2-qZxRVKObnFhAeNtk0AJzWq42pX0_ttO9Ov-Pltais7zWWlYDesmVeXnXLFqWbnmeQA2jMJpOsrpZYpllJlqai0Sg27tiyOXHvta80G4DNzzKsjc8vjmtaSdDTNjzvbaqY-9kuroZ9K9HOjpZ1zF5XBpDsaz7qtcXdCf6OF0pqu9SXccwvkr9ujmuK2SCG9yO1HCx4285X0ZrqbWia9brrh7s1ht9jnDSPnrqQl6i5KlW1is7KS44TXrPG7emeVXqcbjf1CrRaVrKukxuMCSDtFbTzZO6UMh72OpySEUUpuzrsdMDfmmV1ht5-WVbuuO5yHZpV-noyBnBDzO2jW1Mq2MKunDX5Wa6_z_WxtDMT2zpYbydmoN6kv07onCJuU07e0XLM0L07l_oZeY0cd5qE0r8A0aectJ1-fQqS0-VG1lfLH5n54aOnjjIL6JhwUl52lXVErCX01Nptg7RxcTt2qnUEKz7CCJT07l1cFg66D3Vo-x-1mCg2XNmqlkx6umTTorK26NUqU5Q7eLwsysrwJ4a2sNha7nMtPsj1uhmQsK_OWPG8MMglsHgoDyUdKOjXRQXWUasJsSSENVNYOSt6cig2uwRn8kjhtrdgsENdcWS0x6Qhi2ceWPtNVP1kpFffbydDE69Js4uX71epwXuk7BPQ625FXVq29TqNpZ9zY9dObEuF82KyYa17R1zTSLnvEG2wa-409EUuJWlmld0xdL2yIyrVgZzHnLFBZJepiB9YSopFdJLbLnDXcF0ZpFe6zuVanvphUhhWsbey8N7AJnkxK85UGE0ZJ04uLhN_XHTy3zRwQsbBA43EP1RfVFo3mgBT8ZbK_ktYubDlt3awgrk4yS5Jfc4l9icfSqp1P5cb71j7tNFdOq-bUCnl62dzBYNsk5aKRwMZALzr5OXZU-pw3MbZBa9RDyVVL7wBTmZYTq3qO5yd6clIgWa2MF3KdM0FvbMrYlKwF2Yi58bKcmXS4JVorm8Oga8x0s10sVcp4sO636VdvYAFOyGKXkwbZ8bDbT0_b_kLFxnaxaExpBFj0NWjmWuN0UXGwvzZHOeQBu-MNpP66mSvXV4lVhd7CSFwfaEDYm8sM8lpQNvy8OXdanHPY1xeZyrrqtNBiZ5fWPTOd21aElCy3N9p676uoXNWxepDmwwE_zrqSXBmvJbOrlFIUNCeF6XYwNFq6XNU9vG4YZW6rbsq6J6rjgalshxDNfBoNdbJHwrSWH-5dXsuXFrMpbq9KyM-JSopk0G6pIHjgvOwspVUytVFbbBp5mJuma90pP1yuRA2lDCexRVU48PUEmknEXqqHfJ7X7WqhpCmuJi4dsu9KnUPemU75PCeJQkZpgBmut5JNdw8dY55KV6RS2con7E7LXjiDhAH5aQ6a097czvhCSluXtNVqYosGbvXos99TSVvjB2K9NR7VXb0hVQ0JFYiN17aVUHEbrTebfG_gDiuNleQtxynNV9dVWFpvN36xTeZ8R1kir1p0FuW90alOrFJvuJSNfc1L5pWgV7FhTnOWwynyUlU3a6QogC_pu0Fujbr2cqAMR2sxV7d6c2-xr6VpzBvWPMolaVDfzLHfk7lygzu0gTCya6bu1PhSNt1b7Ty3pdV9rzqoFMqWl3Xthu56COf2dX_ktppbf5ZtVqvl8gKCTtVO1gf02dN73UnOqPYb3iY5GhQ6wlQsWmNn0ESNQn1c0eSdaFZqoyxRa826BpvVhJRJbzf7WQpmm42kM7EzpOoU1cakwzcrRqG87w2qk6JyMC23tqxO_RGsZDu25peHhfFw1SrJ1XXXV5vJjZlZrreJrJGoeE1Vzbb3473oLkr1w2JWEfSUzs9KqglWCU_bpQuz3gYo1WplvQCbWV9vS1VSRlbDlskC8UuvNOitMACLcY-fDAY1TumN-Zo-nSmp_QI7NXveAa5cJCvDn2b727KysoqdqpNvV5rictDSnIxCp7VN4tV6WlmOB24Rmq1ZXWsVyq06qfdsMu0VVatfVh1P0quwPdW85Ohg7-TdaKjaxZJPf-PNICE7bXnU9Yc9mNDmfYfH_cK2ZfslZd4bjvvtUUYFLTWTr5j6DIGF1LfoWUzPp16wekdcHwynrVGTS1Q1qalW7UFTH_Vn9R1F8qyZXWYNr1YszJvZmp_dEnpPGHKV3qEUdUqNcqUN7B2NOoZt2F0e7QZk5vTwvkP4NTfIeoU6yjtFpW9MRLlWWUqjRqrZ3qRLqVZ-jFualuh5aezaxm5sl3qeXeumc6Q_SMxLs6Jn0BNjjVaokxTd4mDmyNxomeU7Db_ktXL9vj6lq45RY1Bv8tx01hK2C-xXQGXmTPfzSgct946l46bnpKfp7HJVHWyW6_Z8mPf8XrOfneGe3lPH3MIRNm2P4DRQ190BDTDT4bib95L9GuyXZhXJ7NvZwVos-NgBc9PJzs0WVD3iyc2Omk3VcFkDZs6f8-Vya9YbOaoHanQBUS_L_QS9tM1VNW_jUeHgC1VNT8NFus9ND1heaL1s0c-UEl26blwmOq2h7Nr53aI46ZXXXqlanuzk2kLvFsvGcq0PXAlk1zl67sVOZ8CpaX6S8Tkvl-sdMKIxfaVjGltKw15yLY1Lum662fTM7vHY0VKbfWIzTq19UbVbIKGWemjUSg4q8_wgm-7bA1AckHmz7btyMl2eyr3sNldXMv2qNau7HOrkmt6qLdddUEyqycaoNDAmnRy_0vYlu2TJZjbXb1X2rfJMVHOmtt2YJYAzLXUxq5ftciZtzFKbFWovRX7oGcWcVKcxopWwyu1D1t8MNpuVrCk1UpIaan6Y3-YMM-3UGplpzlV2qX5qnEa-NvQsydByg_osuzjk18NkDu17Sr-ft1294ImG0CByqz-SlrUOp_vISe3cLSyMM33P6elKtZlJymV7hA07bW82vMblevlBob-v98oHiU5-UO9P1tKkp6woo7PXS7vUrdi53r51yPY6ue6wMc4WdNynjHnL5XvcsDMqVMxherwvOpmysqumijnKLbvpYabiFtd1uoZzhIo4Vf2c0qmN9opfH5O2oMg1qz9Buopm9WXGSU2npFSZ19J-nVesjb6Rd3pVXEnj9TYt1nMzXC7PvJrn5HHHQQca8CZkRblzfZLOFpW9RsNQWdqN--MRdhteChSSKVRKUsKGs6V8uoI9caMlxwNldJhtimZrgRNrRyxjv72Xl2ue5Cc1wzks0h13m3QTiltp8eVFFnYq7eImqSegXEGzZbk-EAdmZWLt0n3JEGudbaEu5d1Eogpn-x6oFzt7mc91KvK6OpSMSStTs_SaX8nVs2ung1e1Fa70VacAa7lNgtvNjbGxMQbjhG-nfaEipHU_n5ou-_WEk90OU-26u62OGmRamnAySjq6qbl9lN1NVQCHm241fyjzrljbJsZia8BzvUUy207xtf6infMopRsTTFcwgN6_i311bC2z6fa-7azqYK0me9qkndJHQ32YqXUS-1Uv67Q3o8bEK7q5sT4aZXqlMeyJymY0HdcSztAb92C-ze1sxStpyz4PO8XNykYNOdGyKmidVVernG5Uu2rW79YmlfLOtkv8qK5Pkz7uFseZtDXSlU6LDHjYLnr2AHUra7XfGHeFVKu3cgtoaGyVpFka-81mF5S3Uqlf96qKmVGWJVyerzudDlGyHLbkbkFxLXq55fnw0OygjL5spzvt4bp1sBM9lF4ZQAeF3n6jZ0plb8jrEBc5N7uspPfVrNvM-EsKN2WKLZY-t3dcdZytqLu6ODWrtXQL9BbDSrsvIH5e7a2QTNdBBO6WquQ0duJi2fRNjU-pPZwsbhvyCDn7xATwmk9qpNBfdxKLXa1zSFmjbF-vW_ktziaroyHRdmVxU1quE81Db9xvuOLMbrTc4q7Qr-W6ZJGbuOWe5DtQwG6ht_MtwjdHZm1pFdq7WUcplebdolbW-LnrWql2MmvkuXo5kaoOd83EqJ3mbRcuW8tFpW87uJ2uFmomBHvSUib6IjHvbkcS6LaypAMLm8JON326KK7Lw8OyrG-K471uCQdZnvguTwqqi2eFonbo7-SUI-Zq9YlSXbeMUdbL-aPivJgueDO6DvUnoFmb57toJLTbLQmuB2V7PWkXZn2XLLq8om5rwzkou8Vuu2EXfH9W8XV6gYrrypzbZoyhoZR3abSfNLPVmouGzW6zlpayBSmbmI7qI4opmXzS7_kltTovLvYL2Ewgowz0smhUE-X1vm8UWqACNvsOsnby9EARoDsoQMvuD5fAaKGGLW6KcLsp8t5om9mIGy6LZbnUGA6bPZHPL7otwax7_M7aWUkdt5vZUbvWMXueeDA5B9FT2uAqiS0Wa2suV-QnrotHPKrOh8VmLz0da4tKZZAhFa2-nrSKZOC2KY9UR8qkKGtFtJhSHgRccV4w1Wr2sN2Uttou11-M58PJiBNtmNTdfmXcMRd7bd7R1XRy3C6mesXasLjeppar4To_l_PbpZVqGeZKLrZStfmwUlBLq_XYavYOPbOSK-1tEw-zLjx4fX6055xprqTtDlbWwL1Epb5KToyaLmdFrdrpzdu1oWBxGSFRclwdpivbFl2v7RdeKptPlSmwpIr5fLa2mLXmeDrfTjqy5bRzm3TFRgpwZLRee7XDdjXMWMVVoQ48vltwMs4EOpgQU12VlANULYVUDwVr2PE662Xz0Fx0KsvWoa-0Sv1cVtpZQyVVHKeK815KUqyOIcD6wqnLyznpgnRt2FwVh4f8Kj_yd6680FM7ubGd9XcFby5NtnVzckwJt7u9eqssysNi8X8HQqK_-m2rjmZN3Y__gP_5f23WopY:1uQBgS:FftjcZaHn8l8uLAPkLqBEt0iBy5GJHK-6R9Urumh5a4','2025-06-27 21:11:32.889302'),('e0zm8uken9skfc6m01kftsegkdaqxpvl','eyJ1c2VyX2lkIjo0MywidXNlcm5hbWUiOiJBZGl0eWEifQ:1uTJIx:EWejfkMBakbVhgx4FrDPxJbCmXYsOqxP2pPIpWlrmMk','2025-07-06 11:56:11.968600'),('e2ugqdx6wsdwn1jv22a56qouievhbhcs','.eJyrViotTi2Kz0xRsjIx1gFz8hJzU5WslBxTMksqE5V0lAoSi1LzSuBKSlITkzOgWgwNawHHsRVO:1uQkfI:R_3OSIOod9LQfrYXJotErbO1skMol93mSdcVdGkRo4Y','2025-06-29 10:32:40.267913'),('ebmdet2ftqmmsisn1e5f6o49s3i905x7','eyJ1c2VyX2lkIjo2fQ:1tqzgW:ijbLZ3Zj04OFh3_fxbso0Nob1Y9zfbnREoO1S0MqP4c','2025-03-22 19:18:08.531717'),('f79zakm5vrbg7nlwrc97loi57jcepkq8','.eJxVjssOwiAURP-FtSFcKBRcuvcbmgtcbH3Qpo-V8d-F2BjdTWbOTObJOtzWvtsWmrshsiMDdvj1PIYb5RrEK-bLyMOY13nwvCJ8Txd-HiPdTzv7N9Dj0pd2I7QE1CYIGZ2RDUTbtAactag9QEIRVHCGgGLQkLykZF3BrFIiqba--n50H53xQWUZp4293nU_QDo:1u7f2b:U4auXppn92PoqDhHwkxHmKX1BSSScczoRk0bhy4UlGc','2025-05-07 18:41:49.210732'),('fgzbwhctkwhtdwktp27l13u55jr1n8sw','.eJyrVkpMyc3Mi89MUbIyNNCB8vISc1OVrJQc8zJzU4szFNxLC0oSlXSUSotTi8AqjQwgHJi6otI8haDEfKVaABc_Ggc:1uvbeG:pl9MBc_ybvF7CWIZbIYfx4Qr13fQf7ySXjYkhJ9UB2g','2025-09-22 13:11:08.998671'),('g79fcikp88k3msq95070tuno495arg7e','.eJydVNtu4zYQ_RVBr41tWVc7T-sm62zQJljUBdo3YSzSEhuK1FKkU2Ox_74ztBTZmxYoCvjBPHPR4Tkz_Bq6nptSsPA2TW78QUHLw9tww4Q9QXgTAmuFOmeMhyEFmMB4bx3jypYMLIS3X6eGcXQTdkYfhORlJyrrDBUtWs4ELLoDQv2iSPfJmidRvD_kaZJVEB3yLGXRepkvizyqyjia_9XV4btOZQe2oXZHMIvX19fFrmq0lrMnUFDzFgnNdqfe8na2dVKeZlvJWc3Z7P9-flSlc4MkfS80KuHaPTcYKLJshZFKQt_jcUnC8MpiDp7u8GS0lFN6mhSUwrEPnj4-Pe6WURQt14jVXDGf8wSSU0vdtk6hGQg9cMUNSEQttEKORmyMU8FvoBFneo9AHMXZLMpnUeapEw2Q5xaPCu-vEN5LrVlZG-06hH_-CaFW2wbNs1rVjvr-Th8hCoBK0ue189zwNlyK-ny5nXhpyB8JFS_1odwL4525a7hSQBMCwBoAulISF-m6SPKsWBVEVvSwFwOxZ63ouoKVLZiX5TskJkm05IFWgRF1YwMwLZFzxtD8XUo_GTSi8RV64p4OyhRd4TjD_FK-wnsEKAJOO4o8N6DT6AP_G9pO8jla48uZ4eePRMETCLRCA7sJJgEqrSxUFjPWqwInJV6vUiqUyPoytEyWcZRFvsIpa9788mt25uY9CZ6B0SBWZ-l2OCnEpBOq0oyycpymohjKHHHb4DAeSc5G44aS49LR0XKoyPRXMLiz4Yn3ZK__1Pl_32lj-_KL07TfA9gZfix7v3LU-_5uE-xGeK_Prf68v98idgA_VJej-llI6YW5iJV-ot9lDCM5VH8CI4JfHI7Ddeit-Cph6H4hcZSt83y1SpdT-UU0jlerPInyfKq9Mr_zpH5wf2gzJjZIYP5CBH7IGxp-cbiIB1HB8DQ8zXfV1OVfokOtrirXjaEHfcS3mh664CN-Rp84n_r8h8yhJ02MlzbPkmK1nlq8BXAu05QkqR36im_HaMYzCBNc4pOUSZzgL40vo6NCtessgBIt7xvcvw814YNIVSMkK6U4ClVj6h_CNsHD0IDGkta-L2mtKREztv4WxJqz8h9eNHxhOPScFuD58Ve_c5KbWnjkMwflbH-uFpVQHn1UvZNC-U3pO2GBSG9xB0QffBoRemgrq-kRuTfzYKPwat--fQfm716_:1uUfNm:xvtxvAnsDezTzQd5Sy7lollAbBaTG7shRpJPwXB1a1g','2025-07-10 05:42:46.000703'),('grkbn4enq6673lgvao2cw5nv5csazt6a','eyJ1c2VyX2lkIjo2fQ:1tqsxx:FRTaEJYZ1ogh94yWhvQJhW9CcJs2ectQ5FGVfP3u_GE','2025-03-22 12:07:41.522774'),('hc6kd3lc4ong872vwonl8afswumra0s7','.eJydVMlu2zAQ_RVD57jelDjJLQWaoofkkg8gRuRIIspF4WLDDfLvJS1ZpBT3Up_MN2_e7PoogEmuCGfF4-ZmeCiQWDwWT4pLtO3ip-8cLBbFTeEtmjN1u-4fA_OAxjRG-y5wrPMMlSMMHBSPH8nn7qbojK65QNJx6ryJniuJjMOqqwNkV_uKwX7N6t2e3pe3rIL1ti5ZCevdw7bcljty961TTfFFiHTg2qh2ALM6Ho-rN9pqLZYvoKBBGdJZvp2sQ7l89kKcls8CWYNs-Z_Rh6p__Gm5WLwCN0XfOWu5Dt3zskIT7OWu3AcLFWBteG5ic5C6wAmv7-FltBCJ_rC-LwOIQSeKv_x626zD7zZgDSp25ryunqKiltIr7k4j4kBycZlbDzFdjf8VxKggcpdKaM1IP7ULJrVrw7ScVo1PShRC68aXQcGbvoYe6ARQJLomFTfnKfQwAGsBUtKMW6j4JAXOiATzezMHtim0NyYu06WHg_TY63_hJ8wiJzjsZCoEJXCRkZjBTItq5YC6ZBchixlGtVfOpHqsy_VpXmrHFdUMJ1SforU6nEmaJgKNcziCYanvmbTttHGWvHsdb-wSwuCB2PPiT7FK5zo1nGc82ZUMI-dVmm_EhJ1hM_agM-_T4DCHB_Z0DgN3Cg7Mdx9WuOYUXL5_g8d14-CpKfXdVbcrlsEnTuxr1TO08aG3HNS0QyM6L3k0TOuj4UPCiOAHHr4v48B504Yhxy2P5pQIMnLteMOBIVjMzkEINA3PkPi5o1xhvni24w5SKkxTpy-38_n5F6nR7Cg:1uTnEQ:ka9_IEP-y6vehfbNbvG1wC5jLaPbn8d0K8-qs07SZMU','2025-07-07 19:53:30.207114'),('i4f6r8620ihifh0dua4an563bv72lt7p','eyJ1c2VyX2lkIjo2fQ:1u4PSg:UVwbKh-rrnrI9wxUEqXKMmIna0ColCYXbu4GNKotajY','2025-04-28 19:27:18.657143'),('idxsbm3fk7gdrbt6xrkk5itadkk1pyi2','eyJ1c2VyX2lkIjo2LCJ1c2VybmFtZSI6InZlcnJncm91cCJ9:1uQkRl:mN98_vMxbugsfs1fooNabeOLhi1Y-pLvSg5d11cV8rM','2025-06-29 10:18:41.040585'),('iluz9iq4s3mx1vbwx5fg29jsy8px5fae','eyJ1c2VyX2lkIjo2fQ:1u2P4c:mGtm5yS_EChTSbnyUpga3qoMtTX5-Fifd5Ph9K7Tqk4','2025-04-23 06:38:10.253450'),('j9bf9oohgudim7s5gb85dvcku3qcyz7c','eyJ1c2VyX2lkIjo2fQ:1tybvv:KuNAzVRVvjIC39TEudqN_3OLo4Mhm9bOEq8SscnjvGs','2025-04-12 19:33:31.190424'),('lfzfi2uh0wfsj2qnw9dksdilob8zbkzf','.eJyrVkpMyc3Mi89MUbIyNNaB8vISc1OVrJRcMnNSUwuUdJRKi1OLwEpMDSEcqIKy1KKi9KL80oLMEqVaAK0eGWw:1uvGBP:eO5JiP29VFTH536ehC9m7xyMFIcxMjulg1FmQfyZdcE','2025-09-21 14:15:55.267300'),('lgtxd82hfsni8osva2we9p8gw184fiou','eyJ0ZWFjaGVyX2lkIjoxLCJ1c2VybmFtZSI6IkFwdXJ2YSBBbmltZXNoIn0:1uQlvY:SKzHYYbYqPqw42ZhxNSvXD4qltaZ5wTrEK7-ufA13AY','2025-06-29 11:53:32.245712'),('nnrogso3cz4td1wy0myuv5s5viq0s61v','eyJ1c2VyX2lkIjo2LCJ1c2VybmFtZSI6InZlcnJncm91cCJ9:1uSGTR:R7QHexE1HMAn_gD3Zv7w9JOOIXxlWWCK0SzIm9kEP0c','2025-07-03 14:42:41.545791'),('rvehmp64f42qa5o0osb13gy9ur3zyfw0','.eJydVduO4zYM_RXDr83Ft9hJnnY6s5kdtBksmgLtm8HYiq2OLHl1yTRY7L8vKTuTZKcFigJ-sA7JI-qQlL6GzjBd8jpc5xP_L6Fj4To8Mq0brVwfTkKoOy69T3xejF53knfMtMGj6y0EAfpaBlU7MsbpJDTW1UzasgYL4frrZbskmoS9VgcuWNnzyjpNhPOO1Rzm_QEhMy-yfbpiaZTsD3mWLiqIDvkiq6NVnMdFHlVlEs3-6pvwHVPZg22J7gh6_vr6Ot9VrVJiugUJDeswoenuZCzrphsnxGm6EaxuWD39v9uf5ejdKJcxXKFKrtszjYZisViipRJgDC5j_DessuiDq3tcaSXExT1LC3JhyIOrj9unXRxFUbxCrGGy9j5bEIwoVdc5ye0JoUcmmQZBVYCOi7ciaSeD30AhXqs9AkmULKZRPo0WPnVKA8RA8STx_BLhvVCqLocOWIc__4RQpyxV1irZOOL9nTahFACVpO2V87nhaZjgzXC4HX9pqT4CKlaqQ7nn2lfmvmVSAie5oG4B6EhpUmSrIs0XxbKgZLmBPR8Te1aSjsvrsgP9Er9DEpJECRYoGWjetDYA3VFyTmvqv2vpLwU6o8kNemI-HZQpusGxh9m1fIWvEaAI6xBQ5JkGlUUf2N_Q9YLNsDQ-vNZs2CQKtsCxFArqSXARoFLSQmXRY7UssFOS1TKjQIFZX5viNE6iReQjnLT6rV7UTXbIzdckeIaaGrEapNthp1AmPZeVqskrx24qijHMUW532IxHkrNVOKFUceHY1Ti_gsaZDU_MUHn9VsO_6ZW2pvziFM33CPaaHUvjR464H-7vgt0Z3quB6s-Hhw1iB_BNdd2qn7kQXpgrW-k7-p3H2JJj9CfQPPjFYTvcmt6CbxxG9iuJo8Uqz5fLLL6EX1mTZLnM0yjPL7E3xe99Uj9Uf6Q5O7aYwOyFEvjBbyT84nAQD7yC8WrYznbVheVfrGOsqirXn02PCi9wSRdd8BG3USfGLjz_wXPkpI7x0uaLtFiuLhRvBuzLLCNJGod1xbvjXIxn4Dq4xi9SpkmKX5ZcW88KNfSSwPCs4Px9aAgfRapaLupS8COXDbr-wS29PAMBtSWNvSlprMkRPTb-FJQ1q8t_uNHwhmFgGA3A89OvfuYE0w33yGcG0lkzRPOKS48-SeMEl35STM8tUNIbnAFugk9nhC7ayiq6RB70LMBXUoTfvn0Ho-ppKQ:1uTcfg:nBDd9zlNU4xg_Rj1jBTrULn0wo5XnIpDc43Ry9Fz7e0','2025-07-07 08:36:56.687439'),('rxl9u9vnobttzimqhqmcfl7fhw84nd0z','.eJyrViotTi2Kz0xRsjLTAbPzEnNTlayUHAtKi8oSFRzzMnNTizOUdJRKUhOTM6BKDXWUElNyM_NQOTCdEC0K7qUFJYkKCkq1AKXjIUo:1uQoWO:xWev1PWAtVz87UxyTrFanfX4m6EVqZ8EM5FmmoPHaEA','2025-06-29 14:39:44.630890'),('s0834galt3xoit9fyw09ijxx1rme0e9x','.eJyrViotTi2Kz0xRsjLTAbPzEnNTlayUylKLitKL8ksLlHSUElNyM_PAagxhHKgqx7zM3NTiDAX30oKSRAUFpVoAVhsa_w:1uCMkY:H5kTY3LUFC5mNYjd_ISjKJVHME9q0sClDsSSrGkKXz8','2025-05-20 18:10:38.945897'),('s757qi1qpyj4hmfcysbiga1iftjbbskw','eyJ1c2VyX2lkIjo2LCJ1c2VybmFtZSI6InZlcnJncm91cCJ9:1uSCUZ:gg_gUSYICCm_qYBO9CaSf256qLyz9_pqmz11wuWgIMw','2025-07-03 10:27:35.073269'),('s7m7w1y52tzlv5l5t7ir1ak4u97f151g','.eJydVNtu20YQ_RWCr7UkilfJT1HsyDFaGUEUoH0jRuSK3Hi5y-xFrhDk3zOzokwpboGiAB-4Zy579szlewh1x2XJ6_A2uxkOEjoW3oYfQZs2vAmNdTWTtqzBQnj7PXSGaR8QRzdhr9WeC1b2vLJOU9isYzWHWb9HyMyKdJcsWRLFu32eJlkF0T7P0jpazvN5kUdVGUfTr30TvslU9mBbSncAPXt5eZltq1YpMdmAhIZ1SGiyPRrLusnaCXGcrAWrG1ZP_u_1w6NXvQtPOhjDFWrhuh3TaCiybIGWSoAxeJyTMKyy6IOnOzxpJcToniYFuTDMg6cPm8ftPIqi-RKxhsna-2xAMEqpus5Jbo8IPTDJNAhELXRcnEux0k4Gn0EhXqsdAnEUZ5Mon0SZp040QJxSPEp8v0R4J5Sqy0Yr1yP8_jeEOmVbLJ5VsnGU9wtdQhQAlaTrlfPc8DVM8Ob0uC1_pjboBVSsVPtyx7WvzF3LpAROckHdAtCTkrhIl0WSZ8WiILLcwI4PxJ6UpOfyuuxAP8_fIDFJogQLlAw0b1obgO6InNOa-u9S-rFAZzS-Qo_M00GZoisce5hdylf4GgGKcBsCijzVoNLoHfsbul6wKZbGh9eanS6Jgg1wLIWC-iYYBaiUtFBZ9FguCuyUeLlIKVAg60vTPJnHURb5CCetfq2XH7MTN1-T4AlqasTqJN0WO4WY9FxWqiavHLupKIYwR9xW2IwHkrNVOKFUceHoaBlUVPQX0Diz4ZEZKq-_6vRveqWtKb85RfM9gL1mh9L4kaPc93erYHuGd-qU6q_7-zVie_BNddmqn7gQXpgLW-k7-o3H0JLjzuHB7w7b4dr0GnzlMGS_kDjKlnm-WKTzMfzCGseLRZ5EeT7GXhW_96R-qf6Q5uzYIoHpMxH4xW9I-M3hIO55BcNq2Ey31ZjlX6xDrKoq159ND-rAtKRFF3zAa9SRsTHPf_AcclLHeGnzLCkWyzHFqwH7Mk1JksZhXXF3nIvxBFwHl_goZRIn-KXxpfWsUON6CyB5x0yL8_euIXwQqWq5qEvBD1w26Pont23wMCSgtqSxNyWNNTmix9q_glizuvyHjYYbhoFhNABPj3_4mRNMN9wjnxhIZ80pmldcevRRGie49JNiem6BSK9xBrgJPp4RWrSVVbRE7vU0WEl82o8fPwFcH1Ti:1uXyho:pA7rH0dLRcgiIUwQEn1pTC9ukfgM5t1jTbQZDWqtxj4','2025-07-19 08:57:08.042945'),('t1rhmlzvfkt2oi5h9rwae0y2s08g7a1d','.eJyrViotTi2Kz0xRsjLTAbPzEnNTlayUylKLitKL8ksLlHSUElNyM_PAaoxgHAxVtQC77hnG:1uTJTw:3Yf77QJvOFWWHfwbVIrb3DlKzamyIblAvUwMa9JmW3o','2025-07-06 12:07:32.527858'),('u1ur34cji3myu8jtsbwffkxo6jec54e8','eyJhZG1pbl9pZCI6MTQsImFkbWluX25hbWUiOiJBRElUWUEgTkFJUiJ9:1v6Wp1:j72Ewjx39pPHAqDwcBEMSy2fqcASswV-67ZN6ahvlDg','2025-10-22 16:15:23.599004'),('vh393ogjvuviiyqjrczvrgs4ajf871os','.eJyrViotTi2Kz0xRsjIy0AFz8hJzU5WslBwLSovKEhUc8zJzU4szlHSUSlITkzOgag11lBJTcjPzUDkwnRAtCu6lBSWJCgpArXmlufEFqUWZ-SnFSlZmtQD-Iyb7:1uRV95:qigRNgGziW624HHduxLh7JEDWbfcbqOw7x3OANMeK5E','2025-07-01 12:10:31.331309'),('wvbsvodubnrs82rvwdzqvtpcdjkp18ur','.eJyrViotTi2Kz0xRsjLXAbPzEnNTlayUEvMyc1OLM5R0lBJTcjPzwCqMYByomrLUoqL0ovzSAqVaAHp0GMA:1uBJSU:6n3HKqrj45Gw7FizSPrBqzwy8TyCyCFBJNde2Nano_I','2025-05-17 20:27:38.699165'),('x9h1z57q8ag7jswy20iet7kkzgnh1xc6','eyJ1c2VyX2lkIjo2fQ:1tqwc3:XQ6-wMxKt5y3vXJa_RHSC_MHsMglrnsBj_ZEC1qnbms','2025-03-22 16:01:19.682350'),('xsoyucpy2bdgscxx1ic9eqpx0vxa0f6e','eyJ1c2VyX2lkIjo0MiwidXNlcm5hbWUiOiJhcHVydmFzaW5naCJ9:1uQkQO:8YetzdjcmPFAv-z7scOuXOIHrO7LzUV_ICl8LtiVQOw','2025-06-29 10:17:16.601073'),('z0lk2dw0vcb6qm38046hg0ter6foooqs','eyJhZG1pbl9pZCI6NywiYWRtaW5fbmFtZSI6IlByYXRpayBiaGFpIn0:1ub1Bn:zc_s4ELoxOqffIpB8w-id_s-pqcbOfJxtvTJhhCTtjU','2025-07-27 18:12:39.484095'),('zcquvquvtbz7gae865ync0acolvoxyru','.eJyrViotTi2Kz0xRsjLTAbPzEnNTlayUylKLitKL8ksLlHSUSlITkzOgqgwNdZQSU3Iz88A8YxgHqsvRxTMk0lHBz9EzSKkWAKXiHfU:1uTcgr:2Xih-EfivVTX9GWyADnRdeFWvBOgTZC_S8QT5lhuDFA','2025-07-07 08:38:09.864576');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `homework`
--

DROP TABLE IF EXISTS `homework`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `homework` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL,
  `submission_date` date DEFAULT NULL,
  `file_path` varchar(500) DEFAULT NULL,
  `class` varchar(50) NOT NULL,
  `section` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `homework_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `homework`
--

LOCK TABLES `homework` WRITE;
/*!40000 ALTER TABLE `homework` DISABLE KEYS */;
INSERT INTO `homework` VALUES (10,6,'testing homwork','2025-05-12','uploads/1acd1d3548314b4ca43f8f9d06885949_attendance_record_2.pdf','',NULL),(11,6,'testing homework ','2025-06-05','uploads/4f9121ddc9444894ad91493cce56fe34_Arun Kumar_ProgressCard (2).pdf','1','B'),(12,6,'testting man ','2025-06-05','uploads/460006e7b50245b1968554611d7a88e9_Arun Kumar_ProgressCard (2).pdf','1','B');
/*!40000 ALTER TABLE `homework` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `leave_requests`
--

DROP TABLE IF EXISTS `leave_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `leave_requests` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_name` varchar(100) DEFAULT NULL,
  `leave_reason` text,
  `leave_start_date` date DEFAULT NULL,
  `leave_end_date` date DEFAULT NULL,
  `leave_duration` varchar(10) DEFAULT NULL,
  `half_day_type` varchar(10) DEFAULT NULL,
  `requested_by` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `requested_by` (`requested_by`),
  CONSTRAINT `leave_requests_ibfk_1` FOREIGN KEY (`requested_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `leave_requests`
--

LOCK TABLES `leave_requests` WRITE;
/*!40000 ALTER TABLE `leave_requests` DISABLE KEYS */;
INSERT INTO `leave_requests` VALUES (1,'Animesh ','hahaa','2025-04-08','2025-04-09','full',NULL,6),(2,'Animesh ','hahahahaha','2025-04-02','2025-04-02','full',NULL,6),(3,'Animesh ','nothing ','2025-04-20','2025-04-20','half',NULL,6),(4,'Animesh ','nothing ','2025-04-20','2025-04-20','half',NULL,6),(5,'Animesh ','nothing ','2025-04-20','2025-04-20','half',NULL,6),(6,'Animesh ','nothing ','2025-04-20','2025-04-20','half',NULL,6),(7,'mayur','sprite','2025-04-20','2025-04-20','full',NULL,6),(8,'mayur','sfdsfdsfd','2025-04-20','2025-04-20','full',NULL,6);
/*!40000 ALTER TABLE `leave_requests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `otherusers_profile_pic`
--

DROP TABLE IF EXISTS `otherusers_profile_pic`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `otherusers_profile_pic` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `profile_pic_url` varchar(255) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `otherusers_profile_pic_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `admin_manage_users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `otherusers_profile_pic`
--

LOCK TABLES `otherusers_profile_pic` WRITE;
/*!40000 ALTER TABLE `otherusers_profile_pic` DISABLE KEYS */;
/*!40000 ALTER TABLE `otherusers_profile_pic` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `parents`
--

DROP TABLE IF EXISTS `parents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `parents` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(150) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(128) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `parents`
--

LOCK TABLES `parents` WRITE;
/*!40000 ALTER TABLE `parents` DISABLE KEYS */;
INSERT INTO `parents` VALUES (2,'verrgroup','verrgroup@gmail.com','verr','2025-05-31 02:02:32','2025-05-31 02:02:32');
/*!40000 ALTER TABLE `parents` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `profile_pics`
--

DROP TABLE IF EXISTS `profile_pics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `profile_pics` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `image_path` varchar(255) NOT NULL,
  `uploaded_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `profile_pics_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `profile_pics`
--

LOCK TABLES `profile_pics` WRITE;
/*!40000 ALTER TABLE `profile_pics` DISABLE KEYS */;
INSERT INTO `profile_pics` VALUES (1,20,'pfpics/eee1baf8b0274fd195472abb9da98203_20.jpg','2025-09-08 13:15:06'),(2,6,'pfpics/7bda70df37c845dba02f4d4a03924243_6.png','2025-06-15 10:19:06'),(3,45,'pfpics/30d5908c2181468bb044ea975d6a865b_45.png','2025-06-15 10:39:16'),(4,51,'pfpics/aee978933d074574a34252d5ebce91ce_51.png','2025-09-07 14:17:06');
/*!40000 ALTER TABLE `profile_pics` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `profile_pics_teachers`
--

DROP TABLE IF EXISTS `profile_pics_teachers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `profile_pics_teachers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `teacher_id` int NOT NULL,
  `profile_pic_url` varchar(255) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `teacher_id` (`teacher_id`),
  CONSTRAINT `profile_pics_teachers_ibfk_1` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `profile_pics_teachers`
--

LOCK TABLES `profile_pics_teachers` WRITE;
/*!40000 ALTER TABLE `profile_pics_teachers` DISABLE KEYS */;
/*!40000 ALTER TABLE `profile_pics_teachers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `school_marks`
--

DROP TABLE IF EXISTS `school_marks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `school_marks` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL,
  `subject_id` int NOT NULL,
  `marks` int NOT NULL,
  `max_marks` int NOT NULL,
  `grade` char(1) NOT NULL DEFAULT 'E',
  PRIMARY KEY (`id`),
  UNIQUE KEY `student_id` (`student_id`,`subject_id`),
  KEY `subject_id` (`subject_id`),
  CONSTRAINT `school_marks_ibfk_2` FOREIGN KEY (`subject_id`) REFERENCES `school_subjects` (`id`) ON DELETE CASCADE,
  CONSTRAINT `school_marks_student_id_fk` FOREIGN KEY (`student_id`) REFERENCES `student_page1` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `school_marks_chk_1` CHECK ((`marks` >= 0)),
  CONSTRAINT `school_marks_chk_2` CHECK ((`max_marks` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=57 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `school_marks`
--

LOCK TABLES `school_marks` WRITE;
/*!40000 ALTER TABLE `school_marks` DISABLE KEYS */;
INSERT INTO `school_marks` VALUES (1,1,3,66,100,'B'),(2,1,5,44,100,'C'),(3,1,4,56,100,'C'),(4,1,1,55,100,'C'),(5,1,2,33,100,'D'),(6,2,3,44,100,'C'),(7,2,5,44,100,'C'),(8,2,4,55,100,'C'),(9,2,1,67,100,'B'),(10,2,2,44,100,'C'),(11,3,3,34,100,'D'),(12,3,5,44,100,'C'),(13,3,4,66,100,'B'),(14,3,1,77,100,'B'),(15,3,2,55,100,'C'),(16,4,3,67,100,'B'),(17,4,5,55,100,'C'),(18,4,4,88,100,'A'),(19,4,1,54,100,'C'),(20,4,2,55,100,'C'),(26,6,3,99,100,'A'),(27,6,5,88,100,'A'),(29,6,4,98,100,'A'),(30,6,1,78,100,'B'),(31,6,2,89,100,'A'),(32,7,3,99,100,'A'),(33,7,5,88,100,'A'),(34,7,4,87,100,'A'),(35,7,1,98,100,'A'),(36,7,2,89,100,'A'),(41,30,102,77,100,'B'),(42,30,104,88,100,'A'),(43,30,133,87,100,'A'),(44,30,103,77,100,'B'),(45,30,100,87,100,'A'),(46,30,101,77,100,'B'),(47,20,72,88,100,'A'),(48,20,74,67,100,'B'),(49,20,73,87,100,'A'),(50,20,70,88,100,'A'),(51,20,71,78,100,'B');
/*!40000 ALTER TABLE `school_marks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `school_students`
--

DROP TABLE IF EXISTS `school_students`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `school_students` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `roll_number` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`,`roll_number`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `school_students`
--

LOCK TABLES `school_students` WRITE;
/*!40000 ALTER TABLE `school_students` DISABLE KEYS */;
INSERT INTO `school_students` VALUES (1,'Ani','375'),(7,'Animesh','375'),(6,'Apurva','376'),(3,'bhai ka report','444'),(5,'new bro','121'),(4,'nothjing','7777'),(2,'SOHARSH','666');
/*!40000 ALTER TABLE `school_students` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `school_subjects`
--

DROP TABLE IF EXISTS `school_subjects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `school_subjects` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `max_marks` int NOT NULL,
  `class` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_class_unique` (`name`,`class`),
  CONSTRAINT `school_subjects_chk_1` CHECK ((`max_marks` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=134 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `school_subjects`
--

LOCK TABLES `school_subjects` WRITE;
/*!40000 ALTER TABLE `school_subjects` DISABLE KEYS */;
INSERT INTO `school_subjects` VALUES (1,'Math',100,'10'),(2,'Science',100,'10'),(3,'English',100,'10'),(4,'History',100,'10'),(5,'Geography',100,'10'),(70,'Math',100,'1'),(71,'Science',100,'1'),(72,'English',100,'1'),(73,'History',100,'1'),(74,'Geography',100,'1'),(75,'Math',100,'2'),(76,'Science',100,'2'),(77,'English',100,'2'),(78,'History',100,'2'),(79,'Geography',100,'2'),(80,'Math',100,'3'),(81,'Science',100,'3'),(82,'English',100,'3'),(83,'History',100,'3'),(84,'Geography',100,'3'),(85,'Math',100,'4'),(86,'Science',100,'4'),(87,'English',100,'4'),(88,'History',100,'4'),(89,'Geography',100,'4'),(90,'Math',100,'5'),(91,'Science',100,'5'),(92,'English',100,'5'),(93,'History',100,'5'),(94,'Geography',100,'5'),(95,'Math',100,'6'),(96,'Science',100,'6'),(97,'English',100,'6'),(98,'History',100,'6'),(99,'Geography',100,'6'),(100,'Math',100,'7'),(101,'Science',100,'7'),(102,'English',100,'7'),(103,'History',100,'7'),(104,'Geography',100,'7'),(105,'Math',100,'8'),(106,'Science',100,'8'),(107,'English',100,'8'),(108,'History',100,'8'),(109,'Geography',100,'8'),(110,'Math',100,'9'),(111,'Science',100,'9'),(112,'English',100,'9'),(113,'History',100,'9'),(114,'Geography',100,'9'),(115,'Math',100,'11'),(116,'Science',100,'11'),(117,'English',100,'11'),(118,'History',100,'11'),(119,'Geography',100,'11'),(120,'Math',100,'12'),(121,'Science',100,'12'),(122,'English',100,'12'),(123,'History',100,'12'),(124,'Geography',100,'12'),(133,'Hindi',100,'7');
/*!40000 ALTER TABLE `school_subjects` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_attendance`
--

DROP TABLE IF EXISTS `student_attendance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_attendance` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `student_name` varchar(100) NOT NULL,
  `roll_number` varchar(20) NOT NULL,
  `class_number` varchar(20) NOT NULL,
  `section` varchar(10) NOT NULL,
  `date` date NOT NULL,
  `status` varchar(10) DEFAULT 'Present',
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_attendance`
--

LOCK TABLES `student_attendance` WRITE;
/*!40000 ALTER TABLE `student_attendance` DISABLE KEYS */;
INSERT INTO `student_attendance` VALUES (1,6,'Animesh Gupta','221112','1','A','2025-05-04','Present'),(2,6,'Animesh Gupta','221115','1','A','2025-05-06','Present'),(3,6,'Animesh Gupta','221112','2','A','2025-05-07','Present'),(4,6,'Animesh Gupta','2211189','1','A','2025-05-21','Absent'),(5,6,'ADI BRO','257','1','A','2025-05-04','Present');
/*!40000 ALTER TABLE `student_attendance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_leave_requests`
--

DROP TABLE IF EXISTS `student_leave_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_leave_requests` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `student_name` varchar(255) NOT NULL,
  `reg_number` varchar(20) NOT NULL,
  `class_number` varchar(10) NOT NULL,
  `leave_reason` text NOT NULL,
  `leave_start_date` date NOT NULL,
  `leave_end_date` date NOT NULL,
  `leave_duration` enum('full','half') NOT NULL,
  `half_day_type` varchar(20) DEFAULT NULL,
  `status` enum('Pending','Approved','Rejected') NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `student_leave_requests_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_leave_requests`
--

LOCK TABLES `student_leave_requests` WRITE;
/*!40000 ALTER TABLE `student_leave_requests` DISABLE KEYS */;
INSERT INTO `student_leave_requests` VALUES (1,6,'Animesh Gupta','RA2311026010375','1','hello','2025-05-04','2025-05-06','full',NULL,'Approved','2025-05-06 15:02:31','2025-05-06 16:25:40'),(2,6,'Animesh Gupta','RA2311026010375','2','out of station','2025-05-07','2025-05-10','full',NULL,'Approved','2025-05-06 16:32:27','2025-05-06 16:33:00'),(3,6,'Animesh Gupta','RA2311026010375','2','OUT OF STATION','2025-05-05','2025-05-12','full',NULL,'Approved','2025-05-06 16:36:44','2025-05-06 16:38:49'),(4,6,'apurva','376','1','asdfghj','2025-05-07','2025-05-07','full',NULL,'Approved','2025-05-07 09:07:24','2025-05-07 09:08:06'),(5,6,'ADI BRO','257','2','pet kharab','2025-05-11','2025-05-15','full',NULL,'Approved','2025-05-10 19:22:37','2025-05-10 19:23:03'),(6,20,'ADI BRO','376','1','iuodfsduhfbdsufbhv','2025-05-23','2025-05-30','full','','Approved','2025-05-30 08:28:50','2025-05-30 17:58:46'),(7,20,'Animesh Gupta','RA2311026010375','5','duhfusdhfv','2025-05-20','2025-05-30','full',NULL,'Rejected','2025-05-30 14:01:32','2025-05-30 17:58:48'),(8,20,'Soumya','5352','10','hfvhuias gia so9dfhwbf u 9uhw','2025-05-30','2025-05-30','half','first','Approved','2025-05-30 14:02:01','2025-05-30 17:58:50'),(9,20,'new request','5353','9','fever','2025-05-30','2025-05-31','full',NULL,'Approved','2025-05-31 08:14:12','2025-06-03 08:09:05'),(10,20,'apurva','RA2311026010376','9','Feeling very heavy','2025-06-15','2025-06-19','full',NULL,'Rejected','2025-06-15 12:10:20','2025-06-15 12:18:17');
/*!40000 ALTER TABLE `student_leave_requests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_page1`
--

DROP TABLE IF EXISTS `student_page1`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_page1` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `name` varchar(255) NOT NULL,
  `admission_number` varchar(100) NOT NULL,
  `class` varchar(50) NOT NULL,
  `section` varchar(10) DEFAULT NULL,
  `roll_number` int NOT NULL,
  `emis` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `admission_number` (`admission_number`),
  KEY `student_page1_ibfk_1` (`user_id`),
  CONSTRAINT `student_page1_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=271 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_page1`
--

LOCK TABLES `student_page1` WRITE;
/*!40000 ALTER TABLE `student_page1` DISABLE KEYS */;
INSERT INTO `student_page1` VALUES (187,1,'Jagan Singh','1055','9','A',1362,'EMIS100000'),(188,2,'Deepa Menon','8998','8','A',1955,'EMIS100001'),(189,3,'Bala Patel','4746','6','C',5384,'EMIS100002'),(191,6,'Ezhil Nair','4347','1','B',9084,'EMIS100005'),(192,7,'Hari Pillai','3973','8','C',3327,'EMIS100006'),(193,1,'Jagan Kumar','9559','9','A',118,'EMIS100000'),(194,2,'Fathima Kumar','7808','10','B',6294,'EMIS100001'),(195,3,'Arun Rao','6025','7','C',5439,'EMIS100002'),(196,4,'Bala Patel','8327','10','A',2361,'EMIS100003'),(198,6,'Ganesh Singh','6137','10','A',7926,'EMIS100005'),(199,7,'Bala Iyer','4695','9','A',3152,'EMIS100006'),(200,8,'Fathima Kumar','2918','8','A',9145,'EMIS100007'),(201,9,'Chitra Iyer','1190','8','A',6072,'EMIS100008'),(202,10,'Chitra Patel','4826','6','A',7085,'EMIS100009'),(203,11,'Chitra Rao','7241','7','A',7330,'EMIS100010'),(207,15,'Ezhil Verma','1521','8','C',848,'EMIS100014'),(208,16,'Hari Menon','2730','7','A',3580,'EMIS100015'),(209,17,'Deepa Menon','7561','6','B',1693,'EMIS100016'),(210,18,'Hari Pillai','3986','10','B',1884,'EMIS100017'),(211,19,'Jagan Nair','3447','7','A',8027,'EMIS100018'),(212,20,'Apu','7558','1','C',4371,'EMIS100019'),(236,21,'Ezhil Pillai','3394','6','B',6764,'EMIS100000'),(237,22,'Chitra Kumar','2017','9','C',4442,'EMIS100001'),(238,23,'Hari Menon','8931','9','A',7505,'EMIS100002'),(240,25,'Ganesh Iyer','4201','9','C',8330,'EMIS100004'),(241,26,'Hari Nair','7722','10','C',4101,'EMIS100005'),(242,27,'Chitra Pillai','1356','6','C',2763,'EMIS100006'),(244,29,'Chitra Iyer','1437','7','B',2071,'EMIS100008'),(245,30,'Arun Kumar','4175','7','A',3040,'EMIS100009'),(246,31,'Chitra Patel','6360','8','C',4295,'EMIS100010'),(248,33,'Bala Pillai','4672','6','A',4672,'EMIS100012'),(249,34,'Jagan Patel','6705','9','A',1546,'EMIS100013'),(251,36,'Indira Verma','3650','7','C',5840,'EMIS100015'),(252,37,'Ezhil Iyer','5476','7','A',9912,'EMIS100016'),(253,38,'Bala Verma','7625','9','B',6802,'EMIS100017'),(254,39,'Fathima Menon','3589','9','A',3927,'EMIS100018'),(255,40,'Bala Verma','9205','9','B',7118,'EMIS100019'),(270,41,'Avinash','8888','10','C',98989,'1');
/*!40000 ALTER TABLE `student_page1` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_page2`
--

DROP TABLE IF EXISTS `student_page2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_page2` (
  `user_id` int NOT NULL,
  `gender` varchar(10) DEFAULT NULL,
  `community` varchar(50) DEFAULT NULL,
  `tamil_name` varchar(255) DEFAULT NULL,
  `dob` date DEFAULT NULL,
  `nationality` varchar(50) DEFAULT NULL,
  `blood_group` varchar(5) DEFAULT NULL,
  `mother_tongue` varchar(50) DEFAULT NULL,
  `caste` varchar(50) DEFAULT NULL,
  `religion` varchar(50) DEFAULT NULL,
  `place_of_birth` varchar(255) DEFAULT NULL,
  `aadhaar` varchar(12) DEFAULT NULL,
  `disability` varchar(100) DEFAULT NULL,
  `id_mark1` varchar(255) DEFAULT NULL,
  `id_mark2` varchar(255) DEFAULT NULL,
  `current_class` varchar(20) DEFAULT NULL,
  `admission_class` varchar(20) DEFAULT NULL,
  `admission_year` int DEFAULT NULL,
  `admission_date` date DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `aadhaar` (`aadhaar`),
  CONSTRAINT `student_page2_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `student_page1` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_page2`
--

LOCK TABLES `student_page2` WRITE;
/*!40000 ALTER TABLE `student_page2` DISABLE KEYS */;
INSERT INTO `student_page2` VALUES (1,'Male','MBC','Jagan Singh','2011-11-04','Indian','O+','Kannada','Mudaliar','Hindu','Coimbatore','195747563049','Hearing Impairment','Mole on left cheek','Birthmark on neck','9','2',2017,'2017-10-08'),(2,'Female','MBC','Deepa Menon','2014-05-08','Indian','AB+','Tamil','Scheduled Caste','Sikh','Madurai','799313641676',NULL,NULL,NULL,'8','8',2015,'2015-07-17'),(3,'Female','OC','Bala Patel','2011-08-21','Indian','O+','Hindi','Chettiar','Muslim','Coimbatore','595367572984','Hearing Impairment','Scar on forehead',NULL,'6','6',2015,'2015-07-19'),(4,'Female','MBC','Bala Patel','2012-08-14','Indian','O-','Malayalam','Scheduled Caste','Muslim','Trichy','708091469777','Hearing Impairment','Scar on forehead','Mole on right arm','10','10',2020,'2020-03-01'),(6,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(7,'Male','MBC','Hari Pillai','2009-02-07','Indian','AB+','Tamil','Gounder','Muslim','Salem','633437085664','Visual Impairment',NULL,'Birthmark on neck','8','1',2016,'2016-06-27'),(8,'Female','OC','Fathima Kumar','2011-08-30','Indian','B-','Tamil','Chettiar','Hindu','Chennai','952823118479','Hearing Impairment',NULL,NULL,'8','2',2016,'2016-12-10'),(9,'Female','BC','Chitra Iyer','2010-08-25','Indian','AB+','Hindi','Scheduled Caste','Hindu','Coimbatore','211289018721','Hearing Impairment','Scar on forehead',NULL,'8','2',2018,'2018-12-13'),(10,'Female','OC','Chitra Patel','2009-05-01','Indian','A+','Kannada','Gounder','Sikh','Salem','992962472554','Visual Impairment','Scar on forehead','Mole on right arm','6','1',2022,'2022-06-10'),(11,'Female','OC','Chitra Rao','2015-08-13','Indian','O+','Hindi','Nair','Hindu','Trichy','50924285838','Hearing Impairment',NULL,'Birthmark on neck','7','3',2020,'2020-10-25'),(15,'Male','OC','Ezhil Verma','2008-12-24','Indian','A-','Telugu','Gounder','Muslim','Madurai','53441783182','Visual Impairment','Scar on forehead','Birthmark on neck','8','2',2023,'2023-01-02'),(16,'Female','MBC','Hari Menon','2007-03-07','Indian','O+','Telugu','Chettiar','Christian','Madurai','883129982321','Visual Impairment','Mole on left cheek','Birthmark on neck','7','5',2023,'2023-04-13'),(17,'Female','BC','Deepa Menon','2014-02-10','Indian','B-','Hindi','Chettiar','Christian','Chennai','365405880549','Visual Impairment','Mole on left cheek','Mole on right arm','6','3',2020,'2020-11-29'),(18,'Female','BC','Hari Pillai','2005-02-12','Indian','A-','Tamil','Gounder','Christian','Salem','502372698159',NULL,'Mole on left cheek','Mole on right arm','10','2',2021,'2021-03-17'),(19,'Female','ST','Jagan Nair','2010-09-25','Indian','AB-','Tamil','Scheduled Caste','Christian','Coimbatore','489342863029',NULL,'Scar on forehead',NULL,'7','2',2019,'2019-06-02'),(20,'Male','General','Arun Rao','2025-06-05','Indian','B+','Tamil','Gounder','Sikh','Chennai','327497365787','None','None','Mole on right arm','1','2',2020,'2025-06-07'),(21,'Male','SC','Ezhil Pillai','2014-10-19','Indian','AB+','Hindi','Nair','Christian','Chennai','675238037889','Hearing Impairment',NULL,'Mole on right arm','6','6',2019,'2019-01-31'),(22,'Male','SC','Chitra Kumar','2012-12-25','Indian','B-','Hindi','Mudaliar','Muslim','Salem','31412744881',NULL,NULL,NULL,'9','5',2016,'2016-07-17'),(23,'Female','BC','Hari Menon','2012-01-30','Indian','AB-','Telugu','Nair','Sikh','Trichy','86293890998','Visual Impairment','Scar on forehead','Birthmark on neck','9','3',2022,'2022-09-04'),(25,'Female','BC','Ganesh Iyer','2011-02-20','Indian','A-','Telugu','Nair','Muslim','Coimbatore','553881674011',NULL,NULL,'Birthmark on neck','9','1',2017,'2017-01-30'),(26,'Male','OC','Hari Nair','2008-10-07','Indian','AB-','Tamil','Nair','Hindu','Coimbatore','205658169193','Visual Impairment','Mole on left cheek','Mole on right arm','10','1',2019,'2019-07-06'),(27,'Female','SC','Chitra Pillai','2011-06-04','Indian','A-','Tamil','Gounder','Sikh','Trichy','255505183719',NULL,NULL,NULL,'6','1',2016,'2016-12-31'),(29,'Female','BC','Chitra Iyer','2005-06-11','Indian','AB+','Kannada','Reddy','Muslim','Coimbatore','930936860089','Hearing Impairment',NULL,'Birthmark on neck','7','3',2020,'2020-08-23'),(30,'Male','OC','Arun Kumar','2012-03-17','Indian','B+','Telugu','Gounder','Hindu','Chennai','678356562231',NULL,'Mole on left cheek','Birthmark on neck','7','1',2016,'2016-08-22'),(31,'Female','MBC','Chitra Patel','2015-02-05','Indian','B+','Tamil','Chettiar','Christian','Trichy','775589454172',NULL,'Scar on forehead',NULL,'8','3',2021,'2021-07-31'),(33,'Male','BC','Bala Pillai','2013-07-21','Indian','AB+','Tamil','Chettiar','Muslim','Madurai','429569120258',NULL,NULL,NULL,'6','5',2016,'2016-04-15'),(34,'Male','SC','Jagan Patel','2015-07-10','Indian','A+','Kannada','Reddy','Christian','Salem','273732592447','Visual Impairment','Mole on left cheek','Mole on right arm','9','5',2018,'2018-01-21'),(36,'Male','OC','Indira Verma','2010-06-14','Indian','AB+','Tamil','Mudaliar','Hindu','Chennai','481594682105','Visual Impairment',NULL,'Mole on right arm','7','1',2020,'2020-07-19'),(37,'Female','ST','Ezhil Iyer','2011-06-14','Indian','AB-','Malayalam','Mudaliar','Sikh','Coimbatore','319685527952','Hearing Impairment',NULL,'Mole on right arm','7','2',2021,'2021-09-11'),(38,'Female','ST','Bala Verma','2014-08-27','Indian','AB+','Hindi','Chettiar','Hindu','Chennai','498280135636','Hearing Impairment',NULL,'Mole on right arm','9','2',2022,'2022-06-18'),(39,'Female','SC','Fathima Menon','2011-01-20','Indian','A+','Kannada','Reddy','Muslim','Salem','141749196981','Hearing Impairment',NULL,'Mole on right arm','9','4',2017,'2017-12-14'),(40,'Male','BC','Bala Verma','2014-02-12','Indian','O+','Kannada','Nair','Muslim','Coimbatore','392149792861','Hearing Impairment','Scar on forehead','Birthmark on neck','9','9',2016,'2016-11-12'),(41,'Male','General','Arun Rao','2025-06-13','indian','AB-','Tamil','Bhagwaan','Hindu','Chennai','327497365784','no','None','Mole on right arm','10','123',2023,'2025-06-13');
/*!40000 ALTER TABLE `student_page2` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_page3`
--

DROP TABLE IF EXISTS `student_page3`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_page3` (
  `user_id` int NOT NULL,
  `email` varchar(255) DEFAULT NULL,
  `address` text,
  `contact` varchar(15) DEFAULT NULL,
  `alt_contact` varchar(15) DEFAULT NULL,
  `country` varchar(100) DEFAULT NULL,
  `state` varchar(100) DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `pincode` varchar(10) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `house` varchar(100) DEFAULT NULL,
  `teacher_ward` enum('yes','no') DEFAULT NULL,
  `rte` enum('yes','no') DEFAULT NULL,
  `sports_quota` enum('yes','no') DEFAULT NULL,
  `prev_school` varchar(255) DEFAULT NULL,
  `prev_board` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  CONSTRAINT `student_page3_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_page3`
--

LOCK TABLES `student_page3` WRITE;
/*!40000 ALTER TABLE `student_page3` DISABLE KEYS */;
INSERT INTO `student_page3` VALUES (1,'jagan.singh13@example.com','97 Main Road, Trichy','9941115549','9174234131','India','Tamil Nadu','Coimbatore','600035','Active','Blue','yes','yes','no','Sacred Heart','CBSE'),(2,'deepa.menon43@example.com','70 Main Road, Trichy','9067371676','9913191440','India','Tamil Nadu','Trichy','600022','Active','Blue','no','no','no','Bharatiya Vidya','State Board'),(3,'bala.patel64@example.com','88 Main Road, Coimbatore','9545535909','9818341578','India','Tamil Nadu','Coimbatore','600089','Active','Blue','no','no','yes','St. Marys','ICSE'),(4,'bala.patel7@example.com','11 Main Road, Chennai','9294517922','9688441168','India','Tamil Nadu','Salem','600090','Active','Green','yes','no','yes','Kendriya Vidyalaya','State Board'),(6,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(7,'hari.pillai84@example.com','14 Main Road, Trichy','9575636397','9369442897','India','Tamil Nadu','Salem','600093','Active','Yellow','yes','no','yes','Bharatiya Vidya','CBSE'),(8,'fathima.kumar6@example.com','9 Main Road, Trichy','9540776746','9542351836','India','Tamil Nadu','Coimbatore','600012','Active','Blue','no','yes','no',NULL,NULL),(9,'chitra.iyer88@example.com','51 Main Road, Salem','9378381286','9204369220','India','Tamil Nadu','Coimbatore','600031','Active','Blue','yes','yes','yes',NULL,NULL),(10,'chitra.patel81@example.com','85 Main Road, Trichy','9094285172','9094220831','India','Tamil Nadu','Madurai','600077','Active','Yellow','yes','no','no',NULL,NULL),(11,'chitra.rao59@example.com','88 Main Road, Coimbatore','9896509510','9984267408','India','Tamil Nadu','Madurai','600087','Active','Red','yes','no','yes','DAV Public','CBSE'),(15,'ezhil.verma56@example.com','91 Main Road, Chennai','9884462560','9121491202','India','Tamil Nadu','Trichy','600098','Active','Red','no','yes','no','Bharatiya Vidya','CBSE'),(16,'hari.menon56@example.com','22 Main Road, Trichy','9347221552','9231932875','India','Tamil Nadu','Madurai','600054','Active','Blue','no','yes','yes','Kendriya Vidyalaya','State Board'),(17,'deepa.menon9@example.com','36 Main Road, Chennai','9433262476','9225691059','India','Tamil Nadu','Chennai','600048','Active','Yellow','yes','no','yes',NULL,NULL),(18,'hari.pillai5@example.com','88 Main Road, Madurai','9154364617','9532489254','India','Tamil Nadu','Madurai','600099','Active','Red','yes','yes','no',NULL,NULL),(19,'jagan.nair100@example.com','9 Main Road, Coimbatore','9451387697','9595133027','India','Tamil Nadu','Madurai','600064','Active','Yellow','yes','yes','yes',NULL,NULL),(20,'arun.rao40@example.com','20 Main Road, Chennai','9877552984','9871312050','India','Tamil Nadu','Salem','600077','Active','Blue','yes','yes','yes','ADCA S','XDDF'),(21,'ezhil.pillai61@example.com','44 Main Road, Madurai','9249627092','9945167998','India','Tamil Nadu','Salem','600072','Active','Blue','yes','yes','yes',NULL,NULL),(22,'chitra.kumar58@example.com','76 Main Road, Madurai','9226209791','9946349483','India','Tamil Nadu','Salem','600018','Active','Green','no','yes','yes','Kendriya Vidyalaya','CBSE'),(23,'hari.menon58@example.com','36 Main Road, Trichy','9802315370','9187105327','India','Tamil Nadu','Madurai','600078','Active','Yellow','no','yes','yes',NULL,NULL),(25,'ganesh.iyer87@example.com','43 Main Road, Trichy','9021517615','9344685342','India','Tamil Nadu','Chennai','600060','Active','Blue','yes','no','yes','Bharatiya Vidya','State Board'),(26,'hari.nair46@example.com','30 Main Road, Coimbatore','9405156494','9776115231','India','Tamil Nadu','Salem','600024','Active','Yellow','no','yes','yes','Bharatiya Vidya','State Board'),(27,'chitra.pillai2@example.com','67 Main Road, Madurai','9135822669','9357280160','India','Tamil Nadu','Chennai','600084','Active','Red','yes','no','yes','Sacred Heart','State Board'),(29,'chitra.iyer20@example.com','8 Main Road, Madurai','9621992982','9444510586','India','Tamil Nadu','Chennai','600018','Active','Red','no','no','no','DAV Public','ICSE'),(30,'arun.kumar62@example.com','81 Main Road, Trichy','9890632824','9722114649','India','Tamil Nadu','Trichy','600076','Active','Yellow','no','yes','yes',NULL,NULL),(31,'chitra.patel77@example.com','94 Main Road, Coimbatore','9835406141','9476587364','India','Tamil Nadu','Chennai','600058','Active','Yellow','yes','yes','yes',NULL,NULL),(33,'bala.pillai24@example.com','70 Main Road, Madurai','9565012910','9078545900','India','Tamil Nadu','Coimbatore','600010','Active','Blue','yes','no','yes',NULL,NULL),(34,'jagan.patel88@example.com','85 Main Road, Chennai','9817029429','9160828754','India','Tamil Nadu','Salem','600036','Active','Blue','yes','no','no','St. Marys','CBSE'),(36,'indira.verma14@example.com','63 Main Road, Chennai','9686431250','9827738083','India','Tamil Nadu','Salem','600075','Active','Yellow','yes','no','no','Sacred Heart','CBSE'),(37,'ezhil.iyer70@example.com','11 Main Road, Madurai','9781709943','9489258127','India','Tamil Nadu','Salem','600085','Active','Blue','no','yes','no','St. Marys','ICSE'),(38,'bala.verma85@example.com','10 Main Road, Madurai','9955760854','9333279357','India','Tamil Nadu','Madurai','600089','Active','Yellow','yes','no','no',NULL,NULL),(39,'fathima.menon93@example.com','68 Main Road, Madurai','9313988150','9931760342','India','Tamil Nadu','Coimbatore','600095','Active','Blue','no','yes','yes','Sacred Heart','ICSE'),(40,'bala.verma67@example.com','97 Main Road, Trichy','9481775241','9741033054','India','Tamil Nadu','Chennai','600055','Active','Green','no','yes','yes','Bharatiya Vidya','ICSE'),(41,'avinashg@gmail.com','New Raipur Residenccy\r\n1 st Lane','08109805643','6786678876','India','ΓÇö','RAIPUR','492101','married','white','yes','yes','yes','zcxgsdfvsb','unknown OK');
/*!40000 ALTER TABLE `student_page3` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_page4`
--

DROP TABLE IF EXISTS `student_page4`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_page4` (
  `user_id` int NOT NULL,
  `father_name` varchar(255) DEFAULT NULL,
  `father_name_tamil` varchar(255) DEFAULT NULL,
  `mother_name` varchar(255) DEFAULT NULL,
  `mother_name_tamil` varchar(255) DEFAULT NULL,
  `father_contact` varchar(20) DEFAULT NULL,
  `mother_contact` varchar(20) DEFAULT NULL,
  `father_email` varchar(255) DEFAULT NULL,
  `mother_email` varchar(255) DEFAULT NULL,
  `father_qualification` varchar(255) DEFAULT NULL,
  `mother_qualification` varchar(255) DEFAULT NULL,
  `father_occupation` varchar(255) DEFAULT NULL,
  `mother_occupation` varchar(255) DEFAULT NULL,
  `father_income` varchar(50) DEFAULT NULL,
  `mother_income` varchar(50) DEFAULT NULL,
  `guardian_name` varchar(255) DEFAULT NULL,
  `guardian_contact` varchar(20) DEFAULT NULL,
  `guardian_email` varchar(255) DEFAULT NULL,
  `child_living` varchar(255) DEFAULT NULL,
  `rights_on_child` varchar(255) DEFAULT NULL,
  `med_blood_group` varchar(10) DEFAULT NULL,
  `diseases` text,
  `allergies` text,
  `medicines` text,
  `hospital` varchar(255) DEFAULT NULL,
  `doctor` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  CONSTRAINT `student_page4_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `student_page1` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_page4`
--

LOCK TABLES `student_page4` WRITE;
/*!40000 ALTER TABLE `student_page4` DISABLE KEYS */;
INSERT INTO `student_page4` VALUES (1,'Deepa Sharma','Deepa Sharma','Ezhil Singh','Ezhil Singh','9574700466','9320672748','deepa.sharma@example.com','ezhil.singh@example.com','MBBS','B.Tech','Doctor','Teacher','426074','264123','Ganesh Nair','9744527162','ganesh.nair@example.com','With Parents','Guardian','O+','Diabetes',NULL,'Insulin','Apollo Hospital','Dr. Rajesh'),(2,'Arun Rao','Arun Rao','Ganesh Sharma','Ganesh Sharma','9627517208','9059037245','arun.rao@example.com','ganesh.sharma@example.com','MBBS','Ph.D','Doctor','Doctor','339906','801848','Deepa Iyer','9842651143','deepa.iyer@example.com','With Parents','Guardian','AB+','Asthma',NULL,'Inhaler','Apollo Hospital','Dr. Anil'),(3,'Ezhil Menon','Ezhil Menon','Chitra Kumar','Chitra Kumar','9251464832','9951142504','ezhil.menon@example.com','chitra.kumar@example.com','Ph.D','B.Tech','Teacher','Engineer','485411','451817','Ganesh Iyer','9670300389','ganesh.iyer@example.com','With Parents','Guardian','O+',NULL,'Pollen','Inhaler','Apollo Hospital','Dr. Rajesh'),(4,'Indira Iyer','Indira Iyer','Chitra Nair','Chitra Nair','9599745702','9696805751','indira.iyer@example.com','chitra.nair@example.com','M.Sc','Ph.D','Doctor','Doctor','407522','624832',NULL,NULL,NULL,'With Parents','Father','O-','Asthma',NULL,'Inhaler','Government Hospital','Dr. Rajesh'),(6,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(7,'Chitra Menon','Chitra Menon','Jagan Kumar','Jagan Kumar','9811676757','9832186703','chitra.menon@example.com','jagan.kumar@example.com','M.Sc','B.Com','Government Employee','Government Employee','1153362','632932','Deepa Pillai','9272406624','deepa.pillai@example.com','With Parents','Father','AB+','Asthma','Pollen','Insulin','Apollo Hospital','Dr. Priya'),(8,'Bala Pillai','Bala Pillai','Bala Kumar','Bala Kumar','9418953217','9026016970','bala.pillai@example.com','bala.kumar@example.com','MBBS','M.Sc','Teacher','Businessman','1479657','559464','Ezhil Iyer','9521836815','ezhil.iyer@example.com','With Guardian','Guardian','B-',NULL,'Pollen',NULL,'Apollo Hospital','Dr. Priya'),(9,'Deepa Menon','Deepa Menon','Fathima Singh','Fathima Singh','9192349370','9524159967','deepa.menon@example.com','fathima.singh@example.com','Ph.D','M.Sc','Teacher','Engineer','1053713','698531','Ganesh Nair','9402413916','ganesh.nair@example.com','With Parents','Father','AB+',NULL,'Peanuts','Inhaler','Apollo Hospital','Dr. Priya'),(10,'Jagan Sharma','Jagan Sharma','Ganesh Verma','Ganesh Verma','9579050039','9294665272','jagan.sharma@example.com','ganesh.verma@example.com','B.Com','Ph.D','Businessman','Government Employee','1174063','917554','Bala Singh','9003602309','bala.singh@example.com','With Guardian','Mother','A+','Asthma',NULL,'Inhaler','Fortis Hospital','Dr. Anil'),(11,'Indira Menon','Indira Menon','Jagan Kumar','Jagan Kumar','9884365745','9690438722','indira.menon@example.com','jagan.kumar@example.com','Ph.D','MBBS','Businessman','Government Employee','728589','554265','Fathima Singh','9848363125','fathima.singh@example.com','With Parents','Mother','O+','Diabetes',NULL,NULL,'Government Hospital','Dr. Rajesh'),(15,'Bala Pillai','Bala Pillai','Ezhil Nair','Ezhil Nair','9003337940','9048504038','bala.pillai@example.com','ezhil.nair@example.com','B.Com','B.Com','Government Employee','Engineer','1460964','858847','Indira Patel','9768429290','indira.patel@example.com','With Parents','Guardian','A-',NULL,'Peanuts','Insulin','Fortis Hospital','Dr. Rajesh'),(16,'Ezhil Sharma','Ezhil Sharma','Ganesh Kumar','Ganesh Kumar','9381582871','9461302853','ezhil.sharma@example.com','ganesh.kumar@example.com','Ph.D','B.Com','Businessman','Engineer','338600','666609',NULL,NULL,NULL,'With Guardian','Mother','O+','Diabetes','Pollen',NULL,'Government Hospital','Dr. Rajesh'),(17,'Bala Verma','Bala Verma','Fathima Pillai','Fathima Pillai','9062921125','9826879251','bala.verma@example.com','fathima.pillai@example.com','B.Com','B.Com','Teacher','Government Employee','1348924','765586',NULL,NULL,NULL,'With Guardian','Father','B-','Asthma','Peanuts','Insulin','Fortis Hospital','Dr. Anil'),(18,'Bala Verma','Bala Verma','Jagan Pillai','Jagan Pillai','9378919912','9394517962','bala.verma@example.com','jagan.pillai@example.com','Ph.D','Ph.D','Doctor','Businessman','1480895','948743',NULL,NULL,NULL,'With Guardian','Guardian','A-',NULL,NULL,'Inhaler','Apollo Hospital','Dr. Priya'),(19,'Indira Verma','Indira Verma','Ganesh Sharma','Ganesh Sharma','9946641562','9720781011','indira.verma@example.com','ganesh.sharma@example.com','B.Com','Ph.D','Doctor','Teacher','630688','702514','Jagan Nair','9671206193','jagan.nair@example.com','With Parents','Guardian','AB-',NULL,'Pollen',NULL,'Government Hospital','Dr. Anil'),(20,'Arun Pillai','Arun Pillai','Hari Kumar','Hari Kumar','9059668841','9228863066','arun.pillai@example.com','hari.kumar@example.com','M.Sc','M.Sc','Government Employee','Government Employee','653789','987446','Nair ','32332342','guptaanimesh020@gmail.com','With Guardian','Father','B+','NIL','Peanuts','Insulin','Fortis Hospital','Dr. Anil'),(21,'Fathima Singh','Fathima Singh','Chitra Patel','Chitra Patel','9857623697','9722669447','fathima.singh@example.com','chitra.patel@example.com','Ph.D','B.Tech','Engineer','Engineer','1366833','677279',NULL,NULL,NULL,'With Parents','Guardian','AB+',NULL,'Pollen','Inhaler','Government Hospital','Dr. Anil'),(22,'Bala Kumar','Bala Kumar','Jagan Singh','Jagan Singh','9211924395','9670991345','bala.kumar@example.com','jagan.singh@example.com','M.Sc','B.Com','Engineer','Teacher','1463802','927174',NULL,NULL,NULL,'With Guardian','Father','B-','Diabetes','Peanuts','Inhaler','Government Hospital','Dr. Rajesh'),(23,'Deepa Kumar','Deepa Kumar','Indira Nair','Indira Nair','9508393964','9997850574','deepa.kumar@example.com','indira.nair@example.com','B.Tech','B.Tech','Teacher','Engineer','1479954','670933','Jagan Verma','9091345843','jagan.verma@example.com','With Parents','Mother','AB-','Diabetes',NULL,'Inhaler','Fortis Hospital','Dr. Priya'),(25,'Bala Iyer','Bala Iyer','Bala Menon','Bala Menon','9391679170','9420761657','bala.iyer@example.com','bala.menon@example.com','M.Sc','MBBS','Teacher','Doctor','611001','521571',NULL,NULL,NULL,'With Guardian','Father','A-','Diabetes','Peanuts','Inhaler','Fortis Hospital','Dr. Rajesh'),(26,'Chitra Kumar','Chitra Kumar','Deepa Patel','Deepa Patel','9326307389','9922763833','chitra.kumar@example.com','deepa.patel@example.com','M.Sc','M.Sc','Engineer','Doctor','546939','242390','Arun Rao','9646836817','arun.rao@example.com','With Guardian','Mother','AB-','Asthma','Pollen','Insulin','Apollo Hospital','Dr. Priya'),(27,'Chitra Pillai','Chitra Pillai','Bala Singh','Bala Singh','9143172832','9349596818','chitra.pillai@example.com','bala.singh@example.com','B.Tech','Ph.D','Engineer','Engineer','433409','358151','Hari Pillai','9594409206','hari.pillai@example.com','With Parents','Father','A-',NULL,'Pollen','Inhaler','Fortis Hospital','Dr. Priya'),(29,'Hari Verma','Hari Verma','Ezhil Nair','Ezhil Nair','9310205775','9702641999','hari.verma@example.com','ezhil.nair@example.com','B.Tech','B.Tech','Teacher','Doctor','1052941','639246',NULL,NULL,NULL,'With Parents','Guardian','AB+',NULL,NULL,'Inhaler','Apollo Hospital','Dr. Rajesh'),(30,'Indira Patel','Indira Patel','Chitra Pillai','Chitra Pillai','9688865658','9609582852','indira.patel@example.com','chitra.pillai@example.com','B.Com','MBBS','Teacher','Engineer','1131851','246980','Deepa Singh','9514640022','deepa.singh@example.com','With Parents','Father','B+','Diabetes','Peanuts','Insulin','Apollo Hospital','Dr. Rajesh'),(31,'Ezhil Patel','Ezhil Patel','Chitra Patel','Chitra Patel','9846928524','9529046001','ezhil.patel@example.com','chitra.patel@example.com','M.Sc','Ph.D','Engineer','Engineer','1128734','744633','Arun Pillai','9166021657','arun.pillai@example.com','With Parents','Guardian','B+','Diabetes','Peanuts','Inhaler','Government Hospital','Dr. Anil'),(33,'Chitra Rao','Chitra Rao','Bala Patel','Bala Patel','9457685721','9357679260','chitra.rao@example.com','bala.patel@example.com','M.Sc','MBBS','Doctor','Teacher','726527','710340','Chitra Nair','9507226563','chitra.nair@example.com','With Guardian','Father','AB+',NULL,NULL,NULL,'Government Hospital','Dr. Rajesh'),(34,'Ezhil Iyer','Ezhil Iyer','Chitra Nair','Chitra Nair','9537271333','9225830569','ezhil.iyer@example.com','chitra.nair@example.com','MBBS','MBBS','Government Employee','Teacher','1242383','650199','Chitra Iyer','9471417412','chitra.iyer@example.com','With Parents','Guardian','A+',NULL,'Peanuts',NULL,'Fortis Hospital','Dr. Priya'),(36,'Fathima Iyer','Fathima Iyer','Bala Rao','Bala Rao','9303214327','9870376544','fathima.iyer@example.com','bala.rao@example.com','M.Sc','B.Com','Government Employee','Engineer','1065524','980962',NULL,NULL,NULL,'With Guardian','Father','AB+','Asthma','Pollen',NULL,'Fortis Hospital','Dr. Rajesh'),(37,'Ezhil Nair','Ezhil Nair','Chitra Kumar','Chitra Kumar','9222192053','9830999140','ezhil.nair@example.com','chitra.kumar@example.com','B.Com','B.Com','Doctor','Government Employee','551001','661026','Deepa Nair','9240976275','deepa.nair@example.com','With Guardian','Mother','AB-',NULL,'Pollen',NULL,'Fortis Hospital','Dr. Priya'),(38,'Chitra Nair','Chitra Nair','Arun Pillai','Arun Pillai','9741792555','9283070169','chitra.nair@example.com','arun.pillai@example.com','M.Sc','B.Com','Businessman','Teacher','878177','718632',NULL,NULL,NULL,'With Guardian','Guardian','AB+',NULL,'Peanuts','Inhaler','Government Hospital','Dr. Rajesh'),(39,'Bala Singh','Bala Singh','Ganesh Kumar','Ganesh Kumar','9141069937','9616838878','bala.singh@example.com','ganesh.kumar@example.com','M.Sc','B.Tech','Engineer','Businessman','842257','829311','Ezhil Verma','9190162043','ezhil.verma@example.com','With Parents','Mother','A+','Diabetes','Peanuts','Inhaler','Apollo Hospital','Dr. Rajesh'),(40,'Hari Menon','Hari Menon','Hari Pillai','Hari Pillai','9448454588','9076724603','hari.menon@example.com','hari.pillai@example.com','MBBS','B.Com','Government Employee','Engineer','1018590','538502',NULL,NULL,NULL,'With Guardian','Father','O+',NULL,'Peanuts',NULL,'Fortis Hospital','Dr. Rajesh'),(41,'aceschfeaf','fvcnbvdiufscvnb','Hari Kumarii','Hari Kumar','7676767675','9228863566','avient@gmail.com','swatig@gmail.com','M.Sc','B.Com','Government Employee','Government Employee','386454','987446','awshesh','4434343433','ashes@gmail.com','With Guardian','zrirybvsybfrv','B+','no ','no ','no ','no ','no');
/*!40000 ALTER TABLE `student_page4` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `study_materials`
--

DROP TABLE IF EXISTS `study_materials`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `study_materials` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `file_path` varchar(500) NOT NULL,
  `upload_date` datetime NOT NULL,
  `class` varchar(10) DEFAULT NULL,
  `section` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `study_materials`
--

LOCK TABLES `study_materials` WRITE;
/*!40000 ALTER TABLE `study_materials` DISABLE KEYS */;
INSERT INTO `study_materials` VALUES (6,'study materials ','study_materials/142fda0b9b9c42608eabca2116400c50_DBMS report.pdf','2025-05-12 13:09:23',NULL,NULL),(7,'testing upload  ','study_materials/54a05ba3a5e3435f8bdcd9af469a8710_AdmitCard-253510553098.pdf','2025-06-06 14:45:40','1','B'),(8,'tesitng','study_materials/96b4a82183624691bb366230baf05435_Hold Me Tight_ Seven Conversations for a Lifetime of Love(Z-Library.co).pdf','2025-06-14 01:55:41','1','C');
/*!40000 ALTER TABLE `study_materials` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teacher_signature`
--

DROP TABLE IF EXISTS `teacher_signature`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teacher_signature` (
  `id` int NOT NULL AUTO_INCREMENT,
  `teacher_id` int NOT NULL,
  `signature` text NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `teacher_id` (`teacher_id`),
  CONSTRAINT `teacher_signature_ibfk_1` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teacher_signature`
--

LOCK TABLES `teacher_signature` WRITE;
/*!40000 ALTER TABLE `teacher_signature` DISABLE KEYS */;
/*!40000 ALTER TABLE `teacher_signature` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teachers`
--

DROP TABLE IF EXISTS `teachers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teachers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `subject` varchar(50) NOT NULL,
  `class_teacher_of` varchar(20) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=124 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teachers`
--

LOCK TABLES `teachers` WRITE;
/*!40000 ALTER TABLE `teachers` DISABLE KEYS */;
INSERT INTO `teachers` VALUES (12,'dileep medisetti','dileepmedisetti12@gmail.com','SSB coaching',NULL,'2025-08-10 06:38:05','2222222222'),(13,'verrgroup','verrgroup@gmail.com','English','Class 1-B','2025-06-22 12:14:36','verr'),(123,'adi','adityanair5002@gmail.com','eng',NULL,'2025-10-08 17:21:28','12345678');
/*!40000 ALTER TABLE `teachers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `timetable`
--

DROP TABLE IF EXISTS `timetable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `timetable` (
  `id` int NOT NULL AUTO_INCREMENT,
  `class_id` varchar(20) NOT NULL,
  `subject` varchar(50) NOT NULL,
  `teacher_id` int NOT NULL,
  `day_of_week` enum('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday') NOT NULL,
  `start_time` time NOT NULL,
  `end_time` time NOT NULL,
  `room` varchar(20) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `teacher_id` (`teacher_id`),
  CONSTRAINT `timetable_ibfk_1` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `timetable`
--

LOCK TABLES `timetable` WRITE;
/*!40000 ALTER TABLE `timetable` DISABLE KEYS */;
INSERT INTO `timetable` VALUES (6,'1B','English',13,'Monday','08:38:00','10:38:00','1010','2025-06-22 22:08:38','2025-06-22 22:08:38');
/*!40000 ALTER TABLE `timetable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(150) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Jagan Singh','jagan.singh_1_7b2cd89c@example.com','1362'),(2,'Deepa Menon','deepa.menon_2_7acf4aed@example.com','1955'),(3,'Bala Patel','bala.patel_3_e762783b@example.com','5384'),(4,'Bala Patel_4','bala.patel_4_bf19520d@example.com','2361'),(6,'verrgroup','verrgroup@gmail.com','verr'),(7,'Hari Pillai','hari.pillai_7_dccbd524@example.com','3327'),(8,'newuser','apubhaay@gmail.com','newuser'),(9,'Chitra Iyer','chitra.iyer_9_b0cf0de8@example.com','6072'),(10,'student_449','hello@gmail.com','444'),(11,'Chitra Rao','chitra.rao_11_9d16bde3@example.com','7330'),(15,'student_786','apuRRR@gmail.com','786'),(16,'Hari Menon','hari.menon_16_f256c495@example.com','3580'),(17,'Deepa Menon_17','deepa.menon_17_92116294@example.com','1693'),(18,'Hari Pillai_18','hari.pillai_18_aed90a06@example.com','1884'),(19,'Jagan Nair','jagan.nair_19_f7eac1f7@example.com','8027'),(20,'Arun Rao','arun.rao_20_4bdab95c@example.com','4371'),(21,'Ezhil Pillai','ezhil.pillai_21_1623ef74@example.com','6764'),(22,'Chitra Kumar','chitra.kumar_22_0d3686d9@example.com','4442'),(23,'Hari Menon_23','hari.menon_23_ccc69a12@example.com','7505'),(25,'Ganesh Iyer','ganesh.iyer_25_530b8a91@example.com','8330'),(26,'Hari Nair','hari.nair_26_1e47ff82@example.com','4101'),(27,'Chitra Pillai','chitra.pillai_27_8d452d26@example.com','2763'),(29,'Chitra Iyer_29','chitra.iyer_29_513a6ef8@example.com','2071'),(30,'Arun Kumar','arun.kumar_30_95887f38@example.com','3040'),(31,'Chitra Patel','chitra.patel_31_dce076aa@example.com','4295'),(33,'Bala Pillai','bala.pillai_33_5dfad7a0@example.com','4672'),(34,'Jagan Patel','jagan.patel_34_78dad19f@example.com','1546'),(36,'Indira Verma','indira.verma_36_71c68ed9@example.com','5840'),(37,'Ezhil Iyer','ezhil.iyer_37_5750b8e1@example.com','9912'),(38,'Bala Verma','bala.verma_38_22bd3e51@example.com','6802'),(39,'Fathima Menon','fathima.menon_39_1b4fb68c@example.com','3927'),(40,'Bala Verma_40','bala.verma_40_4b54d981@example.com','7118'),(41,'student_8888','avinashg@gmail.com','8888'),(42,'apurvasingh','singhapurva297@gmail.com','apurva'),(43,'Aditya','an9103@srmist.edu.in','12345678'),(44,'soumyasnehal_05','soumyasnehal279@gmail.com','Eddie_BUCK_07'),(45,'jatin','jatin@gmail.com','jatin'),(47,'xjrqossxlg','yxodpjjm@testform.xyz','ryonvdidmtuf'),(48,'Vignesh','vigneshrajatamil@gmail.com','123456'),(49,'dileep','dileepmedisetti12@gmail.com','dileep'),(51,'verrgroupit','verrgroupit@gmail.com','verrgroupit'),(52,'123','adityanair5002@gmail.com','12345678');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-10-24 13:28:05
