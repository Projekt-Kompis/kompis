-- phpMyAdmin SQL Dump
-- version 5.0.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 01, 2021 at 02:32 AM
-- Server version: 10.5.9-MariaDB
-- PHP Version: 8.0.2

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `kompis`
--

-- --------------------------------------------------------

--
-- Table structure for table `account`
--

CREATE TABLE `account` (
  `id` int(11) NOT NULL,
  `username` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `password` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(320) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ip_address` varbinary(16) DEFAULT NULL,
  `usercol` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `assembly`
--

CREATE TABLE `assembly` (
  `id` int(11) NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `account_id` int(11) DEFAULT NULL,
  `visibility` enum('private','unlisted','public') COLLATE utf8mb4_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `assembly_comment`
--

CREATE TABLE `assembly_comment` (
  `id` int(11) NOT NULL,
  `account_id` int(11) NOT NULL,
  `assembly_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `assembly_comment_revision`
--

CREATE TABLE `assembly_comment_revision` (
  `id` int(11) NOT NULL,
  `comment_id` int(11) NOT NULL,
  `text` longtext COLLATE utf8mb4_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `assembly_listing`
--

CREATE TABLE `assembly_listing` (
  `id` int(11) NOT NULL,
  `listing_id` int(11) NOT NULL,
  `assembly_revision_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `assembly_rating`
--

CREATE TABLE `assembly_rating` (
  `id` int(11) NOT NULL,
  `assembly_revision_id` int(11) NOT NULL,
  `account_id` int(11) NOT NULL,
  `points` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `assembly_revision`
--

CREATE TABLE `assembly_revision` (
  `id` int(11) NOT NULL,
  `time_created` timestamp NULL DEFAULT current_timestamp(),
  `assembly_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `listing`
--

CREATE TABLE `listing` (
  `id` int(11) NOT NULL,
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
  `time_updated` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `listing_blacklist`
--

CREATE TABLE `listing_blacklist` (
  `id` int(11) NOT NULL,
  `store` varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL,
  `store_url` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `part`
--

CREATE TABLE `part` (
  `id` int(11) NOT NULL,
  `model` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `brand` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `type` enum('case','cpu','gpu','motherboard','optical','os','psu','ram','storage') COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `part_case`
--

CREATE TABLE `part_case` (
  `id` int(11) NOT NULL,
  `motherboard_form_factor` int(11) DEFAULT NULL,
  `psu_form_factor` int(11) DEFAULT NULL,
  `part_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `part_cpu`
--

CREATE TABLE `part_cpu` (
  `id` int(11) NOT NULL,
  `userbenchmark_score` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `userbenchmark_url` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `tdp` int(11) DEFAULT NULL,
  `part_id` int(11) NOT NULL,
  `cpu_socket` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `frequency` int(11) DEFAULT NULL,
  `core_count` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `part_gpu`
--

CREATE TABLE `part_gpu` (
  `id` int(11) NOT NULL,
  `tdp` int(11) DEFAULT NULL,
  `userbenchmark_score` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `userbenchmark_url` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `part_id` int(11) NOT NULL,
  `vram` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `part_motherboard`
--

CREATE TABLE `part_motherboard` (
  `id` int(11) NOT NULL,
  `motherboard_form_factor` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `part_id` int(11) NOT NULL,
  `cpu_socket` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ddr_version` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `part_optical`
--

CREATE TABLE `part_optical` (
  `id` int(11) NOT NULL,
  `optical_type` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `part_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `part_os`
--

CREATE TABLE `part_os` (
  `id` int(11) NOT NULL,
  `invoice` tinyint(4) DEFAULT NULL,
  `part_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `part_psu`
--

CREATE TABLE `part_psu` (
  `id` int(11) NOT NULL,
  `psu_form_factor` int(11) DEFAULT NULL,
  `part_id` int(11) NOT NULL,
  `wattage` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `part_ram`
--

CREATE TABLE `part_ram` (
  `id` int(11) NOT NULL,
  `ddr_version` int(11) DEFAULT NULL,
  `speed` int(11) DEFAULT NULL,
  `userbenchmark_score` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `userbenchmark_url` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `size` int(11) DEFAULT NULL,
  `part_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `part_storage`
--

CREATE TABLE `part_storage` (
  `id` int(11) NOT NULL,
  `storage_type` enum('ssd','sshd','hdd') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `connector` enum('sata','m2','nvme','usb') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `rpm` int(11) DEFAULT NULL,
  `part_id` int(11) NOT NULL,
  `size` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `account`
--
ALTER TABLE `account`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username_UNIQUE` (`username`);

--
-- Indexes for table `assembly`
--
ALTER TABLE `assembly`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_assembly_user1_idx` (`account_id`);

--
-- Indexes for table `assembly_comment`
--
ALTER TABLE `assembly_comment`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_comment_user1_idx` (`account_id`),
  ADD KEY `fk_comment_assembly1_idx` (`assembly_id`);

--
-- Indexes for table `assembly_comment_revision`
--
ALTER TABLE `assembly_comment_revision`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_comment_revision_comment1_idx` (`comment_id`);

--
-- Indexes for table `assembly_listing`
--
ALTER TABLE `assembly_listing`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_assembly_listing_listing1_idx` (`listing_id`),
  ADD KEY `fk_assembly_listing_assembly_revision1_idx` (`assembly_revision_id`);

--
-- Indexes for table `assembly_rating`
--
ALTER TABLE `assembly_rating`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_assembly_rating_assembly_revision1_idx` (`assembly_revision_id`),
  ADD KEY `fk_assembly_rating_account1_idx` (`account_id`);

--
-- Indexes for table `assembly_revision`
--
ALTER TABLE `assembly_revision`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_assembly_revision_assembly1_idx` (`assembly_id`);

--
-- Indexes for table `listing`
--
ALTER TABLE `listing`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `store_url` (`store_url`),
  ADD KEY `fk_listing_part1_idx` (`part_id`);

--
-- Indexes for table `listing_blacklist`
--
ALTER TABLE `listing_blacklist`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `store_url` (`store_url`);

--
-- Indexes for table `part`
--
ALTER TABLE `part`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `model` (`model`);

--
-- Indexes for table `part_case`
--
ALTER TABLE `part_case`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `part_id` (`part_id`),
  ADD KEY `fk_part_case_part1_idx` (`part_id`);

--
-- Indexes for table `part_cpu`
--
ALTER TABLE `part_cpu`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `part_id` (`part_id`),
  ADD KEY `fk_part_cpu_part1_idx` (`part_id`);

--
-- Indexes for table `part_gpu`
--
ALTER TABLE `part_gpu`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `part_id` (`part_id`),
  ADD KEY `fk_part_gpu_part1_idx` (`part_id`);

--
-- Indexes for table `part_motherboard`
--
ALTER TABLE `part_motherboard`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `part_id` (`part_id`),
  ADD KEY `fk_part_motherboard_part1_idx` (`part_id`);

--
-- Indexes for table `part_optical`
--
ALTER TABLE `part_optical`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `part_id` (`part_id`),
  ADD KEY `fk_part_optical_part1_idx` (`part_id`);

--
-- Indexes for table `part_os`
--
ALTER TABLE `part_os`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `part_id` (`part_id`),
  ADD KEY `fk_part_os_part1_idx` (`part_id`);

--
-- Indexes for table `part_psu`
--
ALTER TABLE `part_psu`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `part_id` (`part_id`),
  ADD KEY `fk_part_psu_part1_idx` (`part_id`);

--
-- Indexes for table `part_ram`
--
ALTER TABLE `part_ram`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `part_id` (`part_id`),
  ADD KEY `fk_part_ram_part1_idx` (`part_id`);

--
-- Indexes for table `part_storage`
--
ALTER TABLE `part_storage`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `part_id` (`part_id`),
  ADD KEY `fk_part_storage_part1_idx` (`part_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `account`
--
ALTER TABLE `account`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `assembly`
--
ALTER TABLE `assembly`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `assembly_comment`
--
ALTER TABLE `assembly_comment`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `assembly_comment_revision`
--
ALTER TABLE `assembly_comment_revision`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `assembly_listing`
--
ALTER TABLE `assembly_listing`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `assembly_rating`
--
ALTER TABLE `assembly_rating`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `assembly_revision`
--
ALTER TABLE `assembly_revision`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `listing`
--
ALTER TABLE `listing`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `listing_blacklist`
--
ALTER TABLE `listing_blacklist`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `part`
--
ALTER TABLE `part`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `part_case`
--
ALTER TABLE `part_case`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `part_cpu`
--
ALTER TABLE `part_cpu`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `part_gpu`
--
ALTER TABLE `part_gpu`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `part_motherboard`
--
ALTER TABLE `part_motherboard`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `part_optical`
--
ALTER TABLE `part_optical`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `part_os`
--
ALTER TABLE `part_os`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `part_psu`
--
ALTER TABLE `part_psu`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `part_ram`
--
ALTER TABLE `part_ram`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `part_storage`
--
ALTER TABLE `part_storage`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `assembly`
--
ALTER TABLE `assembly`
  ADD CONSTRAINT `fk_assembly_user1` FOREIGN KEY (`account_id`) REFERENCES `account` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Constraints for table `assembly_comment`
--
ALTER TABLE `assembly_comment`
  ADD CONSTRAINT `fk_comment_assembly1` FOREIGN KEY (`assembly_id`) REFERENCES `assembly` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  ADD CONSTRAINT `fk_comment_user1` FOREIGN KEY (`account_id`) REFERENCES `account` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Constraints for table `assembly_comment_revision`
--
ALTER TABLE `assembly_comment_revision`
  ADD CONSTRAINT `fk_comment_revision_comment1` FOREIGN KEY (`comment_id`) REFERENCES `assembly_comment` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Constraints for table `assembly_listing`
--
ALTER TABLE `assembly_listing`
  ADD CONSTRAINT `fk_assembly_listing_assembly_revision1` FOREIGN KEY (`assembly_revision_id`) REFERENCES `assembly_revision` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  ADD CONSTRAINT `fk_assembly_listing_listing1` FOREIGN KEY (`listing_id`) REFERENCES `listing` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Constraints for table `assembly_rating`
--
ALTER TABLE `assembly_rating`
  ADD CONSTRAINT `fk_assembly_rating_account1` FOREIGN KEY (`account_id`) REFERENCES `account` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  ADD CONSTRAINT `fk_assembly_rating_assembly_revision1` FOREIGN KEY (`assembly_revision_id`) REFERENCES `assembly_revision` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Constraints for table `assembly_revision`
--
ALTER TABLE `assembly_revision`
  ADD CONSTRAINT `fk_assembly_revision_assembly1` FOREIGN KEY (`assembly_id`) REFERENCES `assembly` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Constraints for table `listing`
--
ALTER TABLE `listing`
  ADD CONSTRAINT `fk_listing_part1` FOREIGN KEY (`part_id`) REFERENCES `part` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Constraints for table `part_case`
--
ALTER TABLE `part_case`
  ADD CONSTRAINT `fk_part_case_part1` FOREIGN KEY (`part_id`) REFERENCES `part` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Constraints for table `part_cpu`
--
ALTER TABLE `part_cpu`
  ADD CONSTRAINT `fk_part_cpu_part1` FOREIGN KEY (`part_id`) REFERENCES `part` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Constraints for table `part_gpu`
--
ALTER TABLE `part_gpu`
  ADD CONSTRAINT `fk_part_gpu_part1` FOREIGN KEY (`part_id`) REFERENCES `part` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Constraints for table `part_motherboard`
--
ALTER TABLE `part_motherboard`
  ADD CONSTRAINT `fk_part_motherboard_part1` FOREIGN KEY (`part_id`) REFERENCES `part` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Constraints for table `part_optical`
--
ALTER TABLE `part_optical`
  ADD CONSTRAINT `fk_part_optical_part1` FOREIGN KEY (`part_id`) REFERENCES `part` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Constraints for table `part_os`
--
ALTER TABLE `part_os`
  ADD CONSTRAINT `fk_part_os_part1` FOREIGN KEY (`part_id`) REFERENCES `part` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Constraints for table `part_psu`
--
ALTER TABLE `part_psu`
  ADD CONSTRAINT `fk_part_psu_part1` FOREIGN KEY (`part_id`) REFERENCES `part` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Constraints for table `part_ram`
--
ALTER TABLE `part_ram`
  ADD CONSTRAINT `fk_part_ram_part1` FOREIGN KEY (`part_id`) REFERENCES `part` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Constraints for table `part_storage`
--
ALTER TABLE `part_storage`
  ADD CONSTRAINT `fk_part_storage_part1` FOREIGN KEY (`part_id`) REFERENCES `part` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
