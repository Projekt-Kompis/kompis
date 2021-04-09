CREATE DATABASE  IF NOT EXISTS `kompis` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */;
USE `kompis`;
-- MariaDB dump 10.19  Distrib 10.5.9-MariaDB, for Win64 (AMD64)
--
-- ------------------------------------------------------
-- Server version	10.5.9-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `account`
--

DROP TABLE IF EXISTS `account`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `account` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `password` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(320) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username_UNIQUE` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `assembly`
--

DROP TABLE IF EXISTS `assembly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `assembly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `account_id` int(11) DEFAULT NULL,
  `visibility` enum('private','unlisted','public') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `points_average` float NOT NULL DEFAULT 5,
  `points_average_weighted` float NOT NULL DEFAULT 5,
  PRIMARY KEY (`id`),
  KEY `fk_assembly_user1_idx` (`account_id`),
  KEY `visibility` (`visibility`),
  KEY `points_average` (`points_average`),
  KEY `points_average_weighted` (`points_average_weighted`),
  CONSTRAINT `fk_assembly_user1` FOREIGN KEY (`account_id`) REFERENCES `account` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `assembly_comment`
--

DROP TABLE IF EXISTS `assembly_comment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `assembly_comment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `account_id` int(11) NOT NULL,
  `assembly_id` int(11) NOT NULL,
  `parent_assembly_comment_id` int(11) DEFAULT NULL,
  `time_created` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `fk_comment_user1_idx` (`account_id`),
  KEY `fk_comment_assembly1_idx` (`assembly_id`),
  KEY `fk_assembly_comment_assembly_comment1_idx` (`parent_assembly_comment_id`),
  CONSTRAINT `fk_assembly_comment_assembly_comment1` FOREIGN KEY (`parent_assembly_comment_id`) REFERENCES `assembly_comment` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_comment_assembly1` FOREIGN KEY (`assembly_id`) REFERENCES `assembly` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_comment_user1` FOREIGN KEY (`account_id`) REFERENCES `account` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `assembly_comment_revision`
--

DROP TABLE IF EXISTS `assembly_comment_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `assembly_comment_revision` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment_id` int(11) NOT NULL,
  `text` longtext COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `time_created` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `fk_comment_revision_comment1_idx` (`comment_id`),
  CONSTRAINT `fk_comment_revision_comment1` FOREIGN KEY (`comment_id`) REFERENCES `assembly_comment` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `assembly_listing`
--

DROP TABLE IF EXISTS `assembly_listing`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `assembly_listing` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `listing_id` int(11) NOT NULL,
  `assembly_revision_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_assembly_listing_listing1_idx` (`listing_id`),
  KEY `fk_assembly_listing_assembly_revision1_idx` (`assembly_revision_id`),
  CONSTRAINT `fk_assembly_listing_assembly_revision1` FOREIGN KEY (`assembly_revision_id`) REFERENCES `assembly_revision` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_assembly_listing_listing1` FOREIGN KEY (`listing_id`) REFERENCES `listing` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `assembly_rating`
--

DROP TABLE IF EXISTS `assembly_rating`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `assembly_rating` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `points` int(11) NOT NULL,
  `account_id` int(11) NOT NULL,
  `assembly_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_account_assembly` (`account_id`,`assembly_id`),
  KEY `fk_assembly_rating_account1_idx` (`account_id`),
  KEY `fk_assembly_rating_assembly1_idx` (`assembly_id`),
  CONSTRAINT `fk_assembly_rating_account1` FOREIGN KEY (`account_id`) REFERENCES `account` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_assembly_rating_assembly1` FOREIGN KEY (`assembly_id`) REFERENCES `assembly` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `assembly_revision`
--

DROP TABLE IF EXISTS `assembly_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `assembly_revision` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `time_created` timestamp NULL DEFAULT current_timestamp(),
  `assembly_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_assembly_revision_assembly1_idx` (`assembly_id`),
  KEY `time_created` (`time_created`),
  CONSTRAINT `fk_assembly_revision_assembly1` FOREIGN KEY (`assembly_id`) REFERENCES `assembly` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `listing`
--

DROP TABLE IF EXISTS `listing`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `listing` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `store` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `item_condition` enum('new','unpacked','used') COLLATE utf8mb4_unicode_ci DEFAULT 'used',
  `time_expires` timestamp NULL DEFAULT NULL,
  `part_id` int(11) NOT NULL,
  `price` int(11) DEFAULT NULL,
  `author` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `location` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `time_created` timestamp NULL DEFAULT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `store_url` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `time_added` timestamp NOT NULL DEFAULT current_timestamp(),
  `time_updated` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `is_invalid` tinyint(1) NOT NULL DEFAULT 0,
  `listing_score` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `store_url` (`store_url`),
  KEY `fk_listing_part1_idx` (`part_id`),
  CONSTRAINT `fk_listing_part1` FOREIGN KEY (`part_id`) REFERENCES `part` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=46519 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `listing_blacklist`
--

DROP TABLE IF EXISTS `listing_blacklist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `listing_blacklist` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `store` varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL,
  `store_url` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `store_url` (`store_url`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `listing_temp`
--

DROP TABLE IF EXISTS `listing_temp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `listing_temp` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `store` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `condition` int(11) DEFAULT NULL,
  `time_expires` datetime DEFAULT NULL,
  `price` int(11) DEFAULT NULL,
  `author` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `location` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `time_added` datetime DEFAULT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `store_url` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `store_url` (`store_url`)
) ENGINE=InnoDB AUTO_INCREMENT=112 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `part`
--

DROP TABLE IF EXISTS `part`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `part` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `model` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `brand` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `type` enum('case','cooler','cpu','gpu','motherboard','optical','os','psu','ram','storage') COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `model` (`model`)
) ENGINE=InnoDB AUTO_INCREMENT=37676 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `part_case`
--

DROP TABLE IF EXISTS `part_case`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `part_case` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `motherboard_form_factor` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `psu_form_factor` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `part_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `part_id` (`part_id`),
  KEY `fk_part_case_part1_idx` (`part_id`),
  CONSTRAINT `fk_part_case_part1` FOREIGN KEY (`part_id`) REFERENCES `part` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=1249 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `part_cooler`
--

DROP TABLE IF EXISTS `part_cooler`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `part_cooler` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `part_id` int(11) NOT NULL,
  `cpu_socket` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `part_id_UNIQUE` (`part_id`),
  KEY `fk_part_cooler_part1_idx` (`part_id`),
  CONSTRAINT `fk_part_cooler_part1` FOREIGN KEY (`part_id`) REFERENCES `part` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=537 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `part_cpu`
--

DROP TABLE IF EXISTS `part_cpu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `part_cpu` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `userbenchmark_score` float DEFAULT NULL,
  `userbenchmark_url` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `tdp` int(11) DEFAULT NULL,
  `part_id` int(11) NOT NULL,
  `cpu_socket` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `frequency` int(11) DEFAULT NULL,
  `core_count` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `part_id` (`part_id`),
  KEY `fk_part_cpu_part1_idx` (`part_id`),
  CONSTRAINT `fk_part_cpu_part1` FOREIGN KEY (`part_id`) REFERENCES `part` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=1285 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `part_gpu`
--

DROP TABLE IF EXISTS `part_gpu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `part_gpu` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tdp` int(11) DEFAULT NULL,
  `userbenchmark_score` float DEFAULT NULL,
  `userbenchmark_url` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `part_id` int(11) NOT NULL,
  `vram` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `part_id` (`part_id`),
  KEY `fk_part_gpu_part1_idx` (`part_id`),
  CONSTRAINT `fk_part_gpu_part1` FOREIGN KEY (`part_id`) REFERENCES `part` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=3590 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `part_motherboard`
--

DROP TABLE IF EXISTS `part_motherboard`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `part_motherboard` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `motherboard_form_factor` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `part_id` int(11) NOT NULL,
  `cpu_socket` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ddr_version` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `part_id` (`part_id`),
  KEY `fk_part_motherboard_part1_idx` (`part_id`),
  CONSTRAINT `fk_part_motherboard_part1` FOREIGN KEY (`part_id`) REFERENCES `part` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=5683 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `part_optical`
--

DROP TABLE IF EXISTS `part_optical`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `part_optical` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `optical_type` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `part_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `part_id` (`part_id`),
  KEY `fk_part_optical_part1_idx` (`part_id`),
  CONSTRAINT `fk_part_optical_part1` FOREIGN KEY (`part_id`) REFERENCES `part` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=1444 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `part_os`
--

DROP TABLE IF EXISTS `part_os`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `part_os` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `invoice` tinyint(4) DEFAULT NULL,
  `part_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `part_id` (`part_id`),
  KEY `fk_part_os_part1_idx` (`part_id`),
  CONSTRAINT `fk_part_os_part1` FOREIGN KEY (`part_id`) REFERENCES `part` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=291 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `part_psu`
--

DROP TABLE IF EXISTS `part_psu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `part_psu` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `psu_form_factor` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `part_id` int(11) NOT NULL,
  `wattage` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `part_id` (`part_id`),
  KEY `fk_part_psu_part1_idx` (`part_id`),
  CONSTRAINT `fk_part_psu_part1` FOREIGN KEY (`part_id`) REFERENCES `part` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=1595 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `part_ram`
--

DROP TABLE IF EXISTS `part_ram`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `part_ram` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ddr_version` int(11) DEFAULT NULL,
  `speed` int(11) DEFAULT NULL,
  `userbenchmark_score` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `userbenchmark_url` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `size` int(11) DEFAULT NULL,
  `part_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `part_id` (`part_id`),
  KEY `fk_part_ram_part1_idx` (`part_id`),
  CONSTRAINT `fk_part_ram_part1` FOREIGN KEY (`part_id`) REFERENCES `part` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=10146 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `part_storage`
--

DROP TABLE IF EXISTS `part_storage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `part_storage` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `storage_type` enum('ssd','sshd','hdd') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `connector` enum('sata','m2','nvme','usb') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `rpm` int(11) DEFAULT NULL,
  `part_id` int(11) NOT NULL,
  `size` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `part_id` (`part_id`),
  KEY `fk_part_storage_part1_idx` (`part_id`),
  CONSTRAINT `fk_part_storage_part1` FOREIGN KEY (`part_id`) REFERENCES `part` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=5941 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping events for database 'kompis'
--

--
-- Dumping routines for database 'kompis'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-04-09  2:46:12
