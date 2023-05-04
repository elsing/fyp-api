CREATE DATABASE  IF NOT EXISTS `watershed` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `watershed`;
-- MySQL dump 10.13  Distrib 8.0.31, for Win64 (x86_64)
--
-- Host: 10.60.0.1    Database: watershed
-- ------------------------------------------------------
-- Server version	8.0.33

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `delta`
--

DROP TABLE IF EXISTS `delta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `delta` (
  `delta_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(20) NOT NULL,
  `initiated` tinyint(1) NOT NULL DEFAULT '0',
  `org_id_id` int NOT NULL,
  PRIMARY KEY (`delta_id`),
  KEY `fk_delta_org_d4897204` (`org_id_id`),
  CONSTRAINT `fk_delta_org_d4897204` FOREIGN KEY (`org_id_id`) REFERENCES `org` (`org_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `delta`
--

LOCK TABLES `delta` WRITE;
/*!40000 ALTER TABLE `delta` DISABLE KEYS */;
/*!40000 ALTER TABLE `delta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `flow`
--

DROP TABLE IF EXISTS `flow`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `flow` (
  `flow_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `create_time` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `status` varchar(10) NOT NULL DEFAULT 'init',
  `description` varchar(255) DEFAULT '',
  `monitor` tinyint(1) NOT NULL DEFAULT '1',
  `api_key` varchar(36) NOT NULL,
  `locked` tinyint(1) NOT NULL DEFAULT '0',
  `created_by_id` int NOT NULL,
  `org_id_id` int NOT NULL,
  PRIMARY KEY (`flow_id`),
  KEY `fk_flow_user_061a6981` (`created_by_id`),
  KEY `fk_flow_org_e3d58b0d` (`org_id_id`),
  CONSTRAINT `fk_flow_org_e3d58b0d` FOREIGN KEY (`org_id_id`) REFERENCES `org` (`org_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_flow_user_061a6981` FOREIGN KEY (`created_by_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `flow`
--

LOCK TABLES `flow` WRITE;
/*!40000 ALTER TABLE `flow` DISABLE KEYS */;
/*!40000 ALTER TABLE `flow` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `org`
--

DROP TABLE IF EXISTS `org`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `org` (
  `org_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `contact` varchar(50) NOT NULL,
  `preffered_protocol` varchar(10) DEFAULT NULL,
  `preffered_port` int DEFAULT NULL,
  PRIMARY KEY (`org_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `org`
--

LOCK TABLES `org` WRITE;
/*!40000 ALTER TABLE `org` DISABLE KEYS */;
INSERT INTO `org` VALUES (1,'default','',NULL,NULL);
/*!40000 ALTER TABLE `org` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `river`
--

DROP TABLE IF EXISTS `river`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `river` (
  `river_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(20) NOT NULL,
  `protocol` varchar(10) NOT NULL DEFAULT 'wireguard',
  `delta_id` int NOT NULL,
  PRIMARY KEY (`river_id`),
  KEY `fk_river_delta_0b9fbbd3` (`delta_id`),
  CONSTRAINT `fk_river_delta_0b9fbbd3` FOREIGN KEY (`delta_id`) REFERENCES `delta` (`delta_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `river`
--

LOCK TABLES `river` WRITE;
/*!40000 ALTER TABLE `river` DISABLE KEYS */;
/*!40000 ALTER TABLE `river` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stream`
--

DROP TABLE IF EXISTS `stream`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stream` (
  `stream_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(12) NOT NULL,
  `role` varchar(6) NOT NULL DEFAULT 'client',
  `port` int NOT NULL DEFAULT '51820',
  `config` varchar(1000) DEFAULT NULL,
  `public_key` varchar(1000) DEFAULT NULL,
  `ip` varchar(18) NOT NULL,
  `endpoint` varchar(15) NOT NULL,
  `tunnel` varchar(1000) DEFAULT NULL,
  `error` varchar(1000) NOT NULL DEFAULT '',
  `status` varchar(16) NOT NULL DEFAULT 'init',
  `flow_id` int NOT NULL,
  `river_id` int NOT NULL,
  PRIMARY KEY (`stream_id`),
  KEY `fk_stream_flow_b5249258` (`flow_id`),
  KEY `fk_stream_river_4a7d9d4d` (`river_id`),
  CONSTRAINT `fk_stream_flow_b5249258` FOREIGN KEY (`flow_id`) REFERENCES `flow` (`flow_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_stream_river_4a7d9d4d` FOREIGN KEY (`river_id`) REFERENCES `river` (`river_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stream`
--

LOCK TABLES `stream` WRITE;
/*!40000 ALTER TABLE `stream` DISABLE KEYS */;
/*!40000 ALTER TABLE `stream` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(20) NOT NULL,
  `email` varchar(255) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) DEFAULT '',
  `password` varchar(128) NOT NULL,
  `create_time` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `last_login_time` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  `permission` varchar(10) NOT NULL DEFAULT 'default',
  `org_id_id` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`user_id`),
  KEY `fk_user_org_7e47e418` (`org_id_id`),
  CONSTRAINT `fk_user_org_7e47e418` FOREIGN KEY (`org_id_id`) REFERENCES `org` (`org_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'admin','','Admin','','$2b$12$e08GkLARJIk1mMT//u15B.uxrZTjez5HPfosY9wjXQyNkYEej/UPy','2023-05-04 16:19:03.744335','2023-05-04 16:21:17.157077','admin',1);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;