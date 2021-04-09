-- RECALCULATE RATINGS
UPDATE assembly a 
INNER JOIN
(
   SELECT assembly_id, (SUM(points)/COUNT(*)) 'average'
   FROM assembly_rating 
   GROUP BY assembly_id
) b ON a.id = b.assembly_id
SET a.points_average = b.average;

-- RECALCULATE WEIGHTED RATINGS
UPDATE assembly a 
INNER JOIN
(
   SELECT assembly_id, (SUM(points)/(COUNT(*)*0.9)) 'average'
   FROM assembly_rating 
   GROUP BY assembly_id
) b ON a.id = b.assembly_id
SET a.points_average_weighted = b.average;

-- RECALCULATE LISTING SCORE - USERBENCHMARK
UPDATE listing
INNER JOIN part_cpu ON listing.part_id = part_cpu.part_id
SET listing.listing_score = (part_cpu.userbenchmark_score / listing.price)*1000
WHERE price > 0 AND is_invalid = 0;

UPDATE listing
INNER JOIN part_gpu ON listing.part_id = part_gpu.part_id
SET listing.listing_score = (part_gpu.userbenchmark_score / listing.price)*1000
WHERE price > 0 AND is_invalid = 0;

-- RECALCULATE LISTING SCORE - RAM
UPDATE listing
INNER JOIN part_ram ON listing.part_id = part_ram.part_id
SET listing.listing_score = (part_ram.size / listing.price)*1000
WHERE price > 0 AND is_invalid = 0;